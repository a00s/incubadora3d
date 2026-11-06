#!/usr/bin/env python3
import csv,json,hashlib,time
from pathlib import Path
import numpy as np
import argparse
parser=argparse.ArgumentParser(description='Approximate delayed input/output fit; requires NumPy and a captured serial trace.')
parser.add_argument('trace',type=Path)
parser.add_argument('--boot',default='9')
parser.add_argument('--report',type=Path,required=True)
args=parser.parse_args()
p=args.trace
rows=[];events=[];boot=False;pending=None
for r in csv.reader(p.read_text(errors='replace').splitlines()):
 if r[:2]==['BOOT_COUNT',args.boot]:boot=True;continue
 if not boot:continue
 if len(r)==3 and r[:2] in [['EVENT','co2_pulse'],['EVENT','co2_probe']]:pending=int(r[2])
 if len(r)==26 and r[0]=='DATA' and r[1].isdigit() and r[3]=='1':
  sec=int(r[1])/1000;rows.append((sec,int(r[2])))
  if pending is not None:events.append((sec,pending));pending=None
arr=np.array(rows);dt=2.;tt=np.arange(0,arr[-1,0],dt);yy=np.interp(tt,arr[:,0],arr[:,1])-400
N=len(tt);M=1<<(2*N-1).bit_length();train=int(N*.75);begin=150
ix=np.arange(begin,train,3);ixval=np.arange(train,N,3)
results=[];start=time.monotonic()
for dead in [0.,2.,4.,6.,8.]:
 for power in [1.,1.5,2.]:
  u=np.zeros(N)
  for sec,pulse in events:
   i=int(round(sec/dt))
   if i<N:u[i]+=max(0.,pulse-dead)**power
  fu=np.fft.rfft(u,M)
  for lam in [0.0004,0.0005,0.0006,0.0007,0.0008,0.001,0.0012]:
   slow=np.exp(-lam*tt)
   for tau in [4.,8.,12.,16.,24.,32.,48.]:
    fast=np.exp(-tt/tau);kernel=(slow-fast)/(1-lam*tau)
    zz=np.fft.irfft(fu*np.fft.rfft(kernel,M),M)[:N]
    for delay in range(0,62,2):
     sh=delay//2;z=zz if sh==0 else np.r_[np.zeros(sh),zz[:-sh]]
     X=np.column_stack([slow[ix],fast[ix],z[ix]])
     coeff=np.linalg.lstsq(X,yy[ix],rcond=None)[0]
     if coeff[2]<=0:continue
     pred=coeff[0]*slow+coeff[1]*fast+coeff[2]*z
     rmse=np.sqrt(np.mean((pred[ix]-yy[ix])**2))
     val=np.sqrt(np.mean((pred[ixval]-yy[ixval])**2))
     results.append(dict(dead_ms=dead,power=power,loss_rate_s=lam,transport_s=delay,mixing_s=tau,gain=coeff[2],initial_slow=coeff[0],initial_fast=coeff[1],train_rmse_ppm=rmse,validation_rmse_ppm=val))
results.sort(key=lambda x:x['train_rmse_ppm'])
report={'log':p.name,'log_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'samples':len(rows),'pulses':len(events),'train_fraction':.75,'best_by_training':results[:12],'elapsed_s':time.monotonic()-start,'model':'Two exponential state impulse response; gain times max(duration-dead,0)**power. Constant leak decay, transport, mixing. Fit actual pulses; chronologic holdout. Not an isolated physical calibration.'}
args.report.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
