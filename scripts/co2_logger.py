#!/usr/bin/env python3
"""Keep a single USB capture, reconnect automatically, and retain host timestamps."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
STOP=False

def stop(*_):
    global STOP
    STOP=True

def port_owners(port):
    result=subprocess.run(['fuser',str(port)],capture_output=True,text=True)
    return [int(v) for v in result.stdout.split() if v.isdigit()]

def journal(folder,label,raw,t=None):
    event={'id':'usb:'+uuid.uuid4().hex,'t':t or time.time(),'kind':'usb','label':label,'raw':raw,'source':'collector','session':None,'duration_ms':None,'estimated':False}
    with (folder/'connection-events.jsonl').open('a') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')

def run(port,folder):
    folder.mkdir(parents=True,exist_ok=True)
    archive=folder/'telemetria';archive.mkdir(exist_ok=True)
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    previous=None
    while not STOP:
        if not port.exists():
            state='USB ausente; aguardando conexão'
        elif port_owners(port):
            state='Porta já está em uso; preservando a coleta existente'
        else:
            state=None
        if state:
            if state!=previous:print(state,flush=True);previous=state
            time.sleep(1);continue
        previous=None
        name='usb-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S-%fZ')+'.log'
        path=archive/name
        started=time.time()
        journal(folder,'USB conectada · coleta iniciada',f'{port}; {name}',started)
        print(f'Coletando {port} → {path}',flush=True)
        child=subprocess.Popen([sys.executable,'-u',str(ROOT/'scripts/capture_serial.py'),str(port),'--keep-dtr'],stdout=subprocess.PIPE,stderr=None)
        pending=bytearray()
        try:
            with path.open('ab',buffering=0) as output:
                while not STOP:
                    ready,_,_=select.select([child.stdout],[],[],.3)
                    if ready:
                        chunk=os.read(child.stdout.fileno(),65536)
                        if not chunk:break
                        pending.extend(chunk)
                        while b'\n' in pending:
                            line,_,rest=pending.partition(b'\n');pending=bytearray(rest)
                            output.write(f'HOST_TIME,{time.time():.6f}\n'.encode()+line+b'\n')
                    elif child.poll() is not None:break
                if pending:output.write(f'HOST_TIME,{time.time():.6f}\n'.encode()+pending+b'\n')
        finally:
            if child.poll() is None:
                child.send_signal(signal.SIGINT)
                try:child.wait(timeout=3)
                except subprocess.TimeoutExpired:child.terminate();child.wait(timeout=3)
            journal(folder,'Coleta USB encerrada' if port.exists() else 'USB desconectada',str(port))
        if not STOP:time.sleep(1)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--port',type=Path,default=Path('/dev/ttyACM0'))
    p.add_argument('--log-dir',type=Path,default=ROOT/'logs')
    args=p.parse_args();run(args.port,args.log_dir)
