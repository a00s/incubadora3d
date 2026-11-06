#!/usr/bin/env python3
"""Coordinate USB logging and record each verified firmware upload for the chart."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import uuid
from co2_logger import port_owners

ROOT=Path(__file__).resolve().parents[1]
UNIT='incubadora-co2-logger.service'

def identity():
    result={}
    for name in ('temperatura.ino','firmware/incubadora/co2_dosing.h','.arduino-build/incubadora.ino.hex'):
        path=ROOT/name
        if path.exists():result[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    return result

def stop_legacy_reader(port):
    for pid in port_owners(port):
        process=Path('/proc')/str(pid)
        try:
            args=(process/'cmdline').read_bytes().split(b'\0')
            own=(process/'cwd').resolve()==ROOT
            known=any(a.decode(errors='replace').endswith('scripts/capture_serial.py') for a in args)
        except OSError:continue
        if not own or not known:raise RuntimeError(f'Porta ocupada pelo processo {pid}; não foi encerrado automaticamente.')
        os.kill(pid,signal.SIGINT)
    for _ in range(30):
        if not port_owners(port):return
        time.sleep(.1)
    raise RuntimeError('A porta USB ainda está ocupada; envio não iniciado.')

def upload(command,port):
    folder=ROOT/'logs';folder.mkdir(exist_ok=True)
    with (folder/'firmware-upload.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        active=subprocess.run(['systemctl','--user','is-active','--quiet',UNIT]).returncode==0
        if active:subprocess.run(['systemctl','--user','stop',UNIT],check=True)
        try:
            stop_legacy_reader(port)
            started=time.time();hashes=identity()
            result=subprocess.run(command)
            finished=time.time();digest=hashes.get('.arduino-build/incubadora.ino.hex','')
            event={'id':'upload:'+uuid.uuid4().hex,'t':started,'completed_at':finished,'kind':'firmware' if result.returncode==0 else 'alert','label':('Firmware enviado e verificado · ' if result.returncode==0 else 'Falha no envio de firmware · ')+digest[:8],'raw':'Envio iniciado '+time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(started))+'; verificação '+('OK' if result.returncode==0 else 'FALHOU'),'source':'upload','session':None,'duration_ms':round((finished-started)*1000),'estimated':False,'hashes':hashes,'exit_code':result.returncode}
            with (folder/'firmware-events.jsonl').open('a') as output:output.write(json.dumps(event,ensure_ascii=False)+'\n')
            return result.returncode
        finally:
            if active:subprocess.run(['systemctl','--user','start',UNIT],check=False)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',default='/dev/ttyACM0')
    parser.add_argument('command',nargs=argparse.REMAINDER)
    args=parser.parse_args();command=args.command
    if command and command[0]=='--':command=command[1:]
    if not command:parser.error('Falta o comando de upload.')
    raise SystemExit(upload(command,args.port))
