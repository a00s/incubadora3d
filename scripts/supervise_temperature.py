import json
import argparse
import math
import signal
import time
from datetime import datetime
from pathlib import Path

parser = argparse.ArgumentParser(description='Observação térmica contínua e somente leitura; nunca comanda o Arduino.')
parser.add_argument('--log', type=Path, required=True)
parser.add_argument('--state', type=Path, required=True)
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
state = {'started_at': stamp(), 'status': 'starting', 'abort_c': None,
         'peak_c': None, 'samples_above_37_1': 0}
released = False
try:
    fields = sample()
    previous_ms = int(fields[1])
    state.update(status='watching', initial_temp_c=float(fields[4]),
                 duration_limit_seconds=None, read_only=True, note='Somente registro; cortes pertencem ao firmware')
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
    state['ended_at'] = stamp()
    out.write_text(json.dumps(state, indent=2) + '\n')
    print(json.dumps(state), flush=True)
