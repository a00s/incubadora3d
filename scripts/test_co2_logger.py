#!/usr/bin/env python3
"""Exercise auto capture/reconnect through a pseudoterminal, never real Arduino USB."""
from pathlib import Path
import os
import pty
import signal
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
def wait_for(predicate,timeout=6):
    end=time.monotonic()+timeout
    while time.monotonic()<end:
        if predicate():return
        time.sleep(.05)
    raise AssertionError('USB recorder did not produce the expected simulated capture')

with tempfile.TemporaryDirectory(prefix='co2-usb-test-') as folder:
    base=Path(folder);port=base/'arduino-usb';logs=base/'logs'
    master,slave=pty.openpty();target=os.ttyname(slave);os.close(slave);port.symlink_to(target)
    process=subprocess.Popen([sys.executable,str(ROOT/'scripts/co2_logger.py'),'--port',str(port),'--log-dir',str(logs)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        wait_for(lambda:list((logs/'telemetria').glob('*.log')))
        time.sleep(.25)
        os.write(master,b'BOOT_COUNT,77\r\nDATA,1000,48000\r\n')
        wait_for(lambda:any('BOOT_COUNT,77' in p.read_text() for p in (logs/'telemetria').glob('*.log')))
        first=list((logs/'telemetria').glob('*.log'))[0]
        assert 'HOST_TIME,' in first.read_text()
        os.close(master);master=None
        wait_for(lambda:'USB desconectada' in (logs/'connection-events.jsonl').read_text())
        port.unlink();master,slave=pty.openpty();target=os.ttyname(slave);os.close(slave);port.symlink_to(target)
        wait_for(lambda:len(list((logs/'telemetria').glob('*.log')))>=2)
        time.sleep(.25)
        os.write(master,b'BOOT_COUNT,78\r\nDATA,2000,49000\r\n')
        wait_for(lambda:any('BOOT_COUNT,78' in p.read_text() for p in (logs/'telemetria').glob('*.log')))
        assert 'BOOT_COUNT,77' in first.read_text()
    finally:
        process.send_signal(signal.SIGTERM)
        try:process.wait(timeout=5)
        except subprocess.TimeoutExpired:process.kill();process.wait()
        if master is not None:os.close(master)
print('Automatic USB capture, host timestamps, disconnect, reconnect and retained history passed (simulated serial port).')
