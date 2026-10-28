import json
import argparse
import math
import os
import signal
import time
from datetime import datetime
from pathlib import Path

parser = argparse.ArgumentParser(description='Supervisão térmica contínua, sem limite de duração. Não reinicia a serial.')
parser.add_argument('--log', type=Path, required=True)
parser.add_argument('--state', type=Path, required=True)
parser.add_argument('--port', default='/dev/ttyACM0')
args = parser.parse_args()
log, out = args.log, args.state
release = out.with_suffix('.release')
assert not release.exists(), 'Arquivo de liberação já existe; não armar.'

def stamp():
    return datetime.now().astimezone().isoformat()

def sample():
    if time.time() - log.stat().st_mtime > 5:
        raise RuntimeError('Telemetria sem atualização')
    with log.open('rb') as f:
        f.seek(max(0, log.stat().st_size - 8192))
        lines = f.read().decode(errors='replace').splitlines()
    for line in reversed(lines):
        fields = line.split(',')
        if len(fields) == 26 and fields[0] == 'DATA' and fields[1].isdigit():
            if not math.isfinite(float(fields[4])):
                raise RuntimeError('Leitura de temperatura inválida')
            return fields
    raise RuntimeError('Sem amostra completa')

def interrupted(*_):
    raise KeyboardInterrupt

signal.signal(signal.SIGTERM, interrupted)
state = {'started_at': stamp(), 'status': 'arming', 'abort_c': 37.2,
         'peak_c': None, 'samples_above_37_1': 0}
fd = None
released = False
try:
    fields = sample()
    assert fields[7] == '1', 'CO2 deve estar habilitado antes da retomada'
    assert float(fields[4]) < 37.2, 'Temperatura já no limite'
    previous_ms = int(fields[1])
    fd = os.open(args.port, os.O_WRONLY | os.O_NOCTTY | os.O_NONBLOCK)
    if fields[8] == '0':
        os.write(fd, b'HEAT ON\n')
        state['heat_on_command_at'] = stamp()
    state.update(status='watching', initial_temp_c=float(fields[4]),
                 duration_limit_seconds=None, note='Contínuo por solicitação do usuário; modo porta permitido')
    start = time.monotonic()
    seen = None
    saved = 0
    heartbeat = 0
    while True:
        fields = sample()
        ms = int(fields[1])
        if ms < previous_ms:
            raise RuntimeError('Reinício durante o ensaio')
        previous_ms = ms
        temp = float(fields[4])
        if ms != seen:
            seen = ms
            if state['peak_c'] is None or temp > state['peak_c']:
                state.update(peak_c=temp, peak_at=stamp(), peak_arduino_ms=ms)
            if temp > 37.1:
                state['samples_above_37_1'] += 1
        state.update(last_at=stamp(), last_temp_c=temp, last_arduino_ms=ms,
                     heater_enabled=int(fields[8]), heater_on=int(fields[9]),
                     pid_demand_ms=int(fields[22]), heat_rate_c_min=float(fields[23]))
        if temp >= state['abort_c']:
            raise RuntimeError('Limite de interrupção do ensaio atingido')
        if time.monotonic() - saved > 5:
            out.write_text(json.dumps(state, indent=2) + '\n')
            saved = time.monotonic()
        if time.monotonic() - heartbeat > 30:
            print(json.dumps(state), flush=True)
            heartbeat = time.monotonic()
        if release.exists():
            released = True
            state['status'] = 'released_by_operator'
            break
        time.sleep(.2)
except BaseException as exc:
    state.update(status='aborted', reason=type(exc).__name__ + ': ' + str(exc))
finally:
    if fd is not None:
        if not released:
            os.write(fd, b'HEAT OFF\n')
            state['heat_off_command_at'] = stamp()
        os.close(fd)
    if not released:
        for _ in range(50):
            time.sleep(.1)
            try:
                fields = sample()
                if fields[8:10] == ['0', '0']:
                    state['off_confirmed'] = True
                    break
            except Exception:
                pass
    state['ended_at'] = stamp()
    out.write_text(json.dumps(state, indent=2) + '\n')
    print(json.dumps(state), flush=True)
