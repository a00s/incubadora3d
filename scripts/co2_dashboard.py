#!/usr/bin/env python3
"""Local read-only telemetry dashboard. Reads capture files, never the USB device."""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import sqlite3
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'web/co2'
COLS = ['t','ppm','temp','last_ms','next_ms','rate','co2_on','heat_on','locked','projected','uptime_ms','raw_ppm','display_ppm','wrap_estimated']
FALLBACK = 'DATA,ms,co2_ppm,co2_valid,temp_c,rh_pct,t_int_c,co2_enabled,heater_enabled,heater_on,fan_on,valve_open,next_pulse_ms,last_pulse_ms,rate_ppm_s,rate_ppm_min_valid,rate_ppm_min,max_rate_ppm_s,delta_ppm,dose_rise_ppm,wait_cycles,trend_ready,heater_pid_demand_ms,heat_rate_c_min,co2_range_lock,co2_proj_ppm'.split(',')


def number(value):
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def describe_event(row):
    raw = ','.join(row)
    if row[0] == 'EVENT':
        key = row[1] if len(row)>1 else ''
        value = row[2] if len(row)>2 else ''
        if key == 'co2_no_response':
            return ('control', 'Desligamento pela versão antiga · regra de subida removida', None)
        if key == 'door':
            return ('door', 'Porta aberta' if value=='open' else 'Porta fechada', None)
        if key in ('co2_pulse','co2_probe'):
            ms = number(value)
            return ('dose', ('Sonda' if key=='co2_probe' else 'Injeção')+f' · {value} ms', ms)
        if key == 'co2_manual_pulse':
            ms = number(row[3]) if len(row)>3 else None
            return ('dose', f'Dose manual · {ms:g} ms' if ms is not None else 'Dose manual', ms)
        if any(word in key for word in ('locked','lock_restored','jump_suspected','near_protocol')):
            return ('alert','Trava / alerta de CO₂',None)
        if 'sensor_read_failed' in key or 'zero_reading' in key:
            return ('sensor','Leitura do sensor inválida',None)
        if key == 'fan':
            return ('control','Ventilador '+('ligado' if value=='on' else 'desligado'),None)
        if key=='co2_button_clicks':
            return ('button',f'Botão CO₂ · {value} toque(s)',None)
    if row[0]=='EVT' and 'SAFE_OFF' in row:
        return ('alert','Desligamento de segurança',None)
    if row[0]=='ACK':
        return ('control','Comando confirmado · '+', '.join(row[1:]),None)
    return ('other',raw,None)


def parse_log(text: str, name: str, start_epoch: float):
    """Events belong to the following DATA frame, never the preceding frame.

    Historical wall time is estimated from capture creation + MCU uptime. A
    missing boot marker is identified from a large uptime reset. Serial garbage
    before an existing BOOT_COUNT is discarded. No physical door state is inferred.
    """
    lines=text.splitlines()
    has_boot=any(line.startswith('BOOT_COUNT,') for line in lines)
    active=not has_boot
    header=FALLBACK
    sessions=[]
    current=None
    pending=[]
    ordinal=0
    boot=None
    previous_ms=None
    previous_point=None
    offset=start_epoch
    host_time=None
    previous_raw=None
    wrap_offset=0
    door_open=False

    def new_session(counter, inferred=False):
        nonlocal current,ordinal,boot,previous_ms,previous_point,offset,pending,previous_raw,wrap_offset,door_open
        if current and current['points']:
            offset=current['points'][-1][0]
        ordinal+=1
        boot=counter
        key=hashlib.sha1(f'{name}:{ordinal}:{counter}'.encode()).hexdigest()[:16]
        current={'id':key,'file':name,'boot':counter,'estimated_time':True,'points':[], 'events':[], 'start':offset,'end':offset}
        sessions.append(current)
        pending=[{'kind':'restart','label':f'Reinício · boot {counter}' if counter is not None else 'Início da captura / reinício detectado', 'raw':f'BOOT_COUNT,{counter}' if counter is not None else 'uptime reset / capture start','duration_ms':None,'estimated':inferred}]
        if counter is not None or inferred:
            pending.append({'kind':'warmup','label':'Aquecimento inicial do sensor · 120 s','raw':'firmware warmup','duration_ms':120000,'estimated':False})
        previous_ms=previous_point=None
        previous_raw=None;wrap_offset=0;door_open=False

    for line in lines:
        try:
            row=next(csv.reader([line]))
        except csv.Error:
            continue
        if not row: continue
        if row[0]=='HOST_TIME' and len(row)==2:
            host_time=number(row[1]);continue
        received=host_time;host_time=None
        if row[0]=='BOOT_COUNT' and len(row)==2 and row[1].strip().isdigit():
            active=True
            new_session(int(row[1]))
            if received is not None:
                offset=received;current['start']=offset
                for event in pending:
                    if event['kind']=='restart':event['received_at']=received
            continue
        if not active: continue
        if row[0]=='DATA' and len(row)>1 and row[1]=='ms':
            if len(row)==26: header=row
            continue
        if row[0] in ('EVENT','EVT','ACK'):
            kind,label,duration=describe_event(row)
            if row[:2]==['EVENT','door']:
                door_open=len(row)>2 and row[2]=='open'
                if door_open:previous_raw=None;wrap_offset=0
            pending.append({'kind':kind,'label':label,'raw':','.join(row),'duration_ms':duration,'estimated':False,'received_at':received})
            continue
        if row[0]!='DATA' or len(row)!=26: continue
        values=dict(zip(header,row))
        ms=number(values.get('ms'))
        if ms is None or ms<0 or ms>4294967295: continue
        if current is None:
            saved=pending[:]
            new_session(None,True)
            pending+=saved
        if previous_ms is not None and ms<previous_ms:
            if previous_ms>4294000000 and ms<1000000:
                if received is None:offset+=4294967296/1000
            elif previous_ms-ms>1000:
                saved=pending[:]
                new_session(None,True)
                pending+=saved
            else:
                continue
        if previous_ms is not None and ms==previous_ms: continue
        raw_ppm=number(values.get('co2_ppm'))
        if raw_ppm is None or not 0<=raw_ppm<=65535:raw_ppm=None
        ppm=raw_ppm
        if values.get('co2_valid')!='1' or ppm is None or not 0<ppm<=65535: ppm=None
        def v(key,default=None):
            parsed=number(values.get(key))
            return default if parsed is None else parsed
        point=[round(received if received is not None else offset+ms/1000,3),ppm,v('temp_c'),v('last_pulse_ms'),v('next_pulse_ms'),v('rate_ppm_s'),v('co2_enabled',0),v('heater_enabled',0),v('co2_range_lock',0),(v('co2_proj_ppm') if v('co2_proj_ppm') is not None and v('co2_proj_ppm')>=0 else None),int(ms)]
        display_ppm=ppm
        if raw_ppm is not None and (ppm is not None or point[8]):
            if previous_raw is not None and previous_ms is not None and ms-previous_ms<=10000 and not door_open:
                if point[8] and previous_raw-raw_ppm>32768:wrap_offset+=65536
                elif wrap_offset>=65536 and raw_ppm-previous_raw>32768:wrap_offset-=65536
            display_ppm=raw_ppm+wrap_offset
            previous_raw=raw_ppm
        else:
            previous_raw=None
        point.extend([raw_ppm,display_ppm,bool(wrap_offset and display_ppm is not None)])
        if received is not None:
            current['estimated_time']=False
            if not current['points']:
                offset=received-ms/1000
                current['start']=offset
        for event in pending:
            event.update(t=event.get('received_at') or point[0],session=current['id'],source='firmware',id=f"{current['id']}:{int(ms)}:{len(current['events'])}")
            if event['kind']=='dose':
                event['basis_ms']=v('basis_ms')
                event['basis_rise_ppm']=v('basis_rise_ppm')
                event['basis_steps']=v('basis_steps')
            # Restart belongs to the start of uptime, rather than 1.5 s later.
            if event['kind'] in ('restart','warmup') and event.get('received_at') is None:event['t']=offset
            current['events'].append(event)
        pending=[]
        if previous_point:
            for index,kind,label in [(6,'control','CO₂ automático'),(7,'control','Aquecimento'),(8,'alert','Trava de CO₂')]:
                if point[index]!=previous_point[index]:
                    current['events'].append({'id':f"{current['id']}:{int(ms)}:state:{index}",'t':point[0],'session':current['id'],'kind':kind,'label':label+(' ativado' if point[index] else ' desativado'),'raw':f'DATA transition,{COLS[index]},{point[index]}','duration_ms':None,'source':'state','estimated':False})
            if (ppm is None)!=(previous_point[1] is None):
                current['events'].append({'id':f"{current['id']}:{int(ms)}:sensor",'t':point[0],'session':current['id'],'kind':'sensor','label':'Sensor recuperado' if ppm is not None else 'Sensor sem leitura válida','raw':'DATA validity transition','duration_ms':None,'source':'state','estimated':False})
        current['points'].append(point)
        current['start']=offset
        current['end']=point[0]
        previous_ms=ms
        previous_point=point
    # A trailing event has no following sensor frame yet. Keep it pending until
    # the next refresh; assigning it backwards would give a misleading timestamp.
    for session in sessions:
        opened=None
        for event in session['events']:
            if event['kind']!='door' or event['source']!='firmware':continue
            if event['raw']=='EVENT,door,open':
                event['door_action']='open'
                opened=event
            elif event['raw']=='EVENT,door,closed':
                event['door_action']='closed'
                if opened:
                    duration=round((event['t']-opened['t'])*1000)
                    event['duration_ms']=opened['duration_ms']=duration
                    event['paired_event']=opened['id']
                    opened['paired_event']=event['id']
                    label=f"{duration:,}".replace(',','.')+' ms'
                    opened['label']='Porta aberta · '+label
                    event['label']='Porta fechada · aberta por '+label
                    opened=None
                else:
                    event['label']='Porta fechada · duração não registrada'
        if opened:
            opened['elapsed_ms']=max(0,round((session['end']-opened['t'])*1000))
            opened['open_ended']=True
            opened['label']='Porta aberta · fechamento não registrado'
    return [session for session in sessions if session['points']]


def creation_time(path: Path):
    try:
        birth=float(subprocess.check_output(['stat','-c','%W',str(path)],text=True,stderr=subprocess.DEVNULL).strip())
        if birth>0:return birth
    except (OSError,ValueError,subprocess.CalledProcessError):
        pass
    # Explicitly estimated fallback for platforms without file creation time.
    last=0
    for line in path.read_text(errors='replace').splitlines():
        if line.startswith('DATA,'):
            ms=number(line.split(',',2)[1])
            if ms is not None:last=ms/1000
    return path.stat().st_mtime-last


class Store:
    def __init__(self,source:Path,archive:Path):
        self.source,self.archive=source,archive
        archive.mkdir(parents=True,exist_ok=True)
        self.manifest_path=archive/'manifest.json'
        try:self.manifest=json.loads(self.manifest_path.read_text())
        except (OSError,ValueError):self.manifest={}
        self.cache={}
        self.lock=threading.RLock()
        self.db_path=archive.parent/'co2_dashboard.sqlite3'
        with sqlite3.connect(self.db_path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS annotations (id INTEGER PRIMARY KEY, t REAL NOT NULL, kind TEXT NOT NULL, label TEXT NOT NULL, created REAL NOT NULL, duration_ms REAL)')
            if 'duration_ms' not in [column[1] for column in db.execute('PRAGMA table_info(annotations)')]:
                db.execute('ALTER TABLE annotations ADD COLUMN duration_ms REAL')

    def refresh(self):
        with self.lock:
            files={p.name:p for p in self.archive.glob('*.log')}
            if self.source.exists():files.update({p.name:p for p in self.source.glob('*.log')})
            changed=False
            for name,path in files.items():
                stat=path.stat()
                signature=(stat.st_size,stat.st_mtime_ns)
                if name in self.cache and self.cache[name][0]==signature:continue
                if name not in self.manifest:
                    self.manifest[name]={'start_epoch':creation_time(path)}
                    changed=True
                # Append only new capture bytes. Re-copying a whole day of logs
                # every two seconds would create unnecessary disk writes.
                if path.parent!=self.archive:
                    destination=self.archive/name
                    old_inode=self.manifest[name].get('source_inode')
                    rotated=destination.exists() and (stat.st_size<destination.stat().st_size or old_inode is not None and old_inode!=stat.st_ino or stat.st_size>0 and stat.st_size==destination.stat().st_size and stat.st_mtime_ns!=destination.stat().st_mtime_ns)
                    if rotated:
                        backup=self.archive/(path.stem+'--archived-'+str(time.time_ns())+'.log')
                        destination.rename(backup)
                        self.manifest[backup.name]=dict(self.manifest[name])
                        previous=parse_log(backup.read_text(errors='replace'),backup.name,self.manifest[backup.name]['start_epoch'])
                        for session in previous:session['modified']=backup.stat().st_mtime
                        old=backup.stat()
                        self.cache[backup.name]=((old.st_size,old.st_mtime_ns),previous)
                        # A tee restart may reuse the inode/creation time. Anchor
                        # its fresh capture from the current end, explicitly estimated.
                        raw=path.read_bytes()[:stat.st_size].decode(errors='replace')
                        fresh=parse_log(raw,name,0)
                        self.manifest[name]={'start_epoch':stat.st_mtime-(fresh[-1]['end'] if fresh else 0)}
                        changed=True
                    if self.manifest[name].get('source_inode')!=stat.st_ino:
                        self.manifest[name]['source_inode']=stat.st_ino
                        changed=True
                    existing=destination.stat().st_size if destination.exists() else 0
                    if existing<stat.st_size:
                        with path.open('rb') as source,destination.open('ab') as target:
                            source.seek(existing)
                            target.write(source.read(stat.st_size-existing))
                    elif not destination.exists():destination.touch()
                    os.utime(destination,ns=(stat.st_atime_ns,stat.st_mtime_ns))
                text=path.read_bytes()[:stat.st_size].decode(errors='replace')
                if text and not text.endswith(('\n','\r')):text=text.rsplit('\n',1)[0] if '\n' in text else ''
                parsed=parse_log(text,name,self.manifest[name]['start_epoch'])
                for session in parsed:session['modified']=stat.st_mtime
                self.cache[name]=(signature,parsed)
            if changed:
                temporary=self.manifest_path.with_suffix('.tmp')
                temporary.write_text(json.dumps(self.manifest,indent=2)+'\n')
                temporary.replace(self.manifest_path)
            sessions=sorted([s for _,parts in self.cache.values() for s in parts],key=lambda s:s['start'])
            return sessions

    def annotations(self):
        with sqlite3.connect(self.db_path) as db:
            return [{'id':f'note:{r[0]}','t':r[1],'kind':r[2],'label':r[3],'source':'annotation','raw':'Anotação manual','duration_ms':r[4],'session':None,'estimated':False} for r in db.execute('SELECT id,t,kind,label,duration_ms FROM annotations ORDER BY t')]

    def add_annotation(self,item):
        stamp=number(item.get('t'))
        label=str(item.get('label','')).strip()
        kind=item.get('kind','note')
        if stamp is None or not 946684800<=stamp<=time.time()+86400:raise ValueError('Horário inválido.')
        if not label or len(label)>300:raise ValueError('Escreva uma anotação de até 300 caracteres.')
        if kind not in ('note','door','cylinder','restart'):raise ValueError('Tipo de evento inválido.')
        duration=number(item.get('duration_ms'))
        if item.get('duration_ms') not in (None,'') and (duration is None or not 0<=duration<=86400000):raise ValueError('Duração inválida (0–86.400.000 ms).')
        with sqlite3.connect(self.db_path) as db:
            result=db.execute('INSERT INTO annotations(t,kind,label,created,duration_ms) VALUES(?,?,?,?,?)',(stamp,kind,label,time.time(),duration))
            return result.lastrowid

    def snapshot(self,selected='latest'):
        with self.lock:
            all_sessions=self.refresh()
            meta=[{k:v for k,v in s.items() if k not in ('points','events')}|{'samples':len(s['points']),'last':s['points'][-1]} for s in all_sessions]
            latest=all_sessions[-1]['id'] if all_sessions else None
            selected=latest if selected=='latest' or selected!='all' and selected not in {s['id'] for s in all_sessions} else selected
            chosen=all_sessions if selected=='all' else [s for s in all_sessions if s['id']==selected]
            events=[e for s in chosen for e in s['events']]
            uploads=[]
            for name in ('firmware-events.jsonl','connection-events.jsonl'):
                journal=self.archive.parent/name
                if journal.exists():
                    for line in journal.read_text().splitlines():
                        try:uploads.append(json.loads(line))
                        except ValueError:continue
            annotations=self.annotations()
            if chosen:
                start,end=min(s['start'] for s in chosen),max(s['end'] for s in chosen)
                events.extend(e for e in annotations+uploads if (start<=e['t']<=max(end,time.time() if selected==latest else end)) or (e.get('kind') in ('firmware','usb') and start-30<=e['t']<start))
                display_start=min([start]+[e['t'] for e in events if e.get('kind')=='firmware' and e['t']<start])
            return {'display_start':display_start if chosen else None,'columns':COLS,'sessions':meta,'selected':selected,'latest':latest,'series':[{'id':s['id'],'points':s['points']} for s in chosen], 'events':sorted(events,key=lambda e:e['t']),'server_time':time.time(),'target':50000,'band':[49000,51000],'clock_note':'Capturas antigas: horário estimado e eventos aproximados ao ciclo da leitura. Novas capturas USB automáticas: horário do computador salvo em cada registro.'}


def serve(args):
    store=Store(args.log_dir.resolve(),args.archive_dir.resolve())
    store.refresh()
    def archive_continuously():
        while True:
            time.sleep(2)
            try:store.refresh()
            except OSError as exc:print(f'Arquivo temporariamente indisponível: {exc}',flush=True)
    threading.Thread(target=archive_continuously,daemon=True,name='telemetry-archive').start()
    class Handler(BaseHTTPRequestHandler):
        def json_reply(self,value,status=200):
            payload=json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':')).encode()
            compressed='gzip' in self.headers.get('Accept-Encoding','') and len(payload)>1024
            if compressed:payload=gzip.compress(payload)
            self.send_response(status)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            if compressed:self.send_header('Content-Encoding','gzip')
            self.send_header('Content-Length',str(len(payload)))
            self.end_headers();self.wfile.write(payload)
        def do_GET(self):
            parsed=urlparse(self.path)
            if parsed.path=='/api/history':
                try:self.json_reply(store.snapshot(parse_qs(parsed.query).get('session',['latest'])[0]))
                except (OSError,ValueError) as exc:self.json_reply({'error':str(exc)},500)
                return
            files={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/style.css':'style.css'}
            if parsed.path not in files:self.send_error(404);return
            path=WEB/files[parsed.path]
            data=path.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type',{'html':'text/html; charset=utf-8','js':'text/javascript; charset=utf-8','css':'text/css; charset=utf-8'}[path.suffix[1:]])
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-cache')
            self.send_header('X-Content-Type-Options','nosniff')
            self.end_headers();self.wfile.write(data)
        def do_POST(self):
            if self.path!='/api/annotations':self.send_error(404);return
            # Local annotations only. There is deliberately no actuator endpoint.
            origin=self.headers.get('Origin')
            if origin and urlparse(origin).netloc!=self.headers.get('Host'):
                self.json_reply({'error':'Origem inválida.'},403);return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=4096:raise ValueError('Anotação inválida.')
                item=json.loads(self.rfile.read(length))
                self.json_reply({'id':store.add_annotation(item)},201)
            except (ValueError,TypeError,AttributeError) as exc:self.json_reply({'error':str(exc)},400)
        def do_DELETE(self):
            origin=self.headers.get('Origin')
            if origin and urlparse(origin).netloc!=self.headers.get('Host'):
                self.json_reply({'error':'Origem inválida.'},403);return
            identifier=self.path.removeprefix('/api/annotations/')
            if not self.path.startswith('/api/annotations/') or not identifier.isdigit():
                self.send_error(404);return
            with sqlite3.connect(store.db_path) as db:
                db.execute('DELETE FROM annotations WHERE id=?',(int(identifier),))
            self.json_reply({'ok':True})
        def log_message(self,format,*values):
            if values and str(values[1] if len(values)>1 else '') not in ('200','201'):super().log_message(format,*values)
    print(f'Histórico CO₂: http://127.0.0.1:{args.port} — arquivos: {args.log_dir} — arquivo permanente: {args.archive_dir}',flush=True)
    ThreadingHTTPServer((args.host,args.port),Handler).serve_forever()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--port',type=int,default=8082)
    parser.add_argument('--log-dir',type=Path,default=Path('/tmp/incubadora-telemetria'))
    parser.add_argument('--archive-dir',type=Path,default=ROOT/'logs/telemetria')
    serve(parser.parse_args())
