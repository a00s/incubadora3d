#!/usr/bin/env python3
"""Real sketch gates + last-dose proportional calculation and measured loss refill."""
from pathlib import Path
import json
import subprocess
import tempfile
from co2_firmware_harness import harness
fixture=json.loads((Path(__file__).parent/'fixtures/co2_jump_228.json').read_text())
replay_rows=',\n'.join('{%d,%d,%d}'%(t,p,int(v)) for t,p,v in fixture['rows'])
code=harness()+r'''
#include <random>
int main(){
 resetFirmware();auto &c=co2DoseModel;
 c.update(100000,48050,true);c.update(110000,48025,true);c.update(120000,48000,true);CO2i=48000;
 assert(firmwarePulse(119999)==0);assert(firmwarePulse(120000)==18);
 assert(firmwarePulse(120000,false)==0);assert(firmwarePulse(120000,true,false)==0);
 assert(firmwarePulse(120000,true,true,1)==0);assert(firmwarePulse(120000,true,true,0,true)==0);
 // The exact requested proportion, with only mechanical/growth bounds.
 resetFirmware();c.previousValid=true;c.trained=true;c.referenceMs=20;c.referenceRise=2000;
 c.lastPpm=49000;c.falling=2;c.lossPpmPerSec=0;
 assert(c.pulse(120000)==10);c.lastPpm=46000;assert(c.pulse(120000)==40); // Exact ratio; no percentage ceiling.
 c.lastPpm=49000;c.referenceRise=4000;assert(c.pulse(120000)==5);
 c.falling=1;assert(!c.ready(120000));c.falling=2;assert(c.ready(120000));
 recordAutomatic(10,120000);assert(!firmwareReady(139999));
 c.falling=2;c.observing=true;assert(firmwareReady(140010)); // No additional observation pause.
 // A flat summit replenishes measured loss at the normal 20 s cadence.
 c.lastPpm=50000;c.falling=0;c.flat=2;c.lossPpmPerSec=20;c.referenceMs=20;c.referenceRise=2000;
 assert(c.pulse(140010)==5);c.lossPpmPerSec=0;assert(c.pulse(140010)==0);
 c.lastPpm=51000;c.lossPpmPerSec=20;assert(c.pulse(140010)==0);
 // A rising curve flattening at45000 must act before any decline, after20s.
 resetFirmware();c.previousValid=true;c.trained=true;c.referenceMs=44;c.referenceRise=5000;
 c.lastPpm=45000;c.lastAt=100000;c.hasSent=true;c.sendAt=100000;
 c.update(102000,45001,true);c.update(104000,45002,true);
 assert(c.falling==0&&c.flat==2);assert(!c.ready(119999));assert(c.ready(120000));
 assert(c.pulse(120000)==44);
 // The same plateau can continue short calibration probes before useful gain exists.
 c.trained=false;assert(c.pulse(120000)>=5);
 // A useful response can be learned at the plateau, without two falling samples.
 resetFirmware();c.update(100000,40000,true);c.record(20,100000);
 c.update(110000,41000,true);c.update(120000,42000,true);
 c.update(122000,42001,true);c.update(124000,42002,true);
 assert(c.falling==0&&c.trained&&c.referenceRise>=2000);
 // A rising response forbids a new command, independent of the old rolling slope.
 c.update(150000,50000,true);c.update(152000,50025,true);assert(!c.ready(160000));
 // A real valley-to-peak rise remains useful even below ppm at the command.
 resetFirmware();c.update(100000,50000,true);c.record(20,100000);
 c.update(110000,47000,true);c.update(120000,47500,true);c.update(130000,49000,true);
 c.update(140000,48900,true);c.update(150000,48800,true);assert(c.trained);
 for(uint32_t t=160000;t<=220000;t+=10000)c.update(t,48800-(t-150000)/100,true);
 assert(c.trained&&c.referenceMs==20&&c.referenceRise>=2000);

 // A flat dose with no measurable rise does not invent a new gain.
 c.lastPpm=50000;auto rise=c.referenceRise;c.record(5,230000);assert(c.observing);
 c.update(232000,50000,true);c.update(234000,50000,true);assert(c.referenceRise==rise);
 c.reset(true);assert(!c.trained&&c.referenceMs==20&&c.hasSent);
 // Plateau recognition has no49000/51000 gate; the separate upper cut still prevents gas.
 resetFirmware();c.previousValid=true;c.flat=2;c.lastPpm=2000;assert(c.ready(120000));
 c.lastPpm=52000;assert(c.ready(120000));assert(c.pulse(120000)==0);
 // A large proportional result is not silently converted to a10% increment.
 c.trained=true;c.referenceMs=40;c.referenceRise=2000;c.lastPpm=40000;c.lossPpmPerSec=0;
 assert(c.pulse(120000)==200);
 // No response cannot divide by zero; two declines must be in the same 20 s window.
 resetFirmware();c.update(100000,48000,true);c.update(102000,47900,true);
 assert(c.falling==1);c.update(130000,47800,true);assert(c.falling==0);
 c.update(132000,47700,true);c.update(134000,47600,true);assert(c.ready(134000));
 assert(c.pulse(134000)>=5);assert(c.projection(134000)==-1);
 // millis rollover keeps the full 20 s after the valve closes.
 resetFirmware();c.previousValid=true;c.lastPpm=48000;c.trained=true;c.referenceRise=2000;
 recordAutomatic(5,UINT32_MAX-10000);c.observing=false;c.falling=2;
 assert(!firmwareReady(9000));assert(firmwareReady(11000));
 // Use1,2,...5 actual stairs, without waiting for five. Roll the oldest out.
 resetFirmware();uint32_t stepTime=120000;int32_t level=20000;
 for(int n=1;n<=6;n++){
  c.update(stepTime,level,true);c.record(20,stepTime);
  for(int j=1;j<=10;j++)c.update(stepTime+j*2000,level+(n*500*(j<5?j:5))/5,true);
  level+=n*500;stepTime+=20000;
  assert(c.stepCount==(n<5?n:5));assert(c.referenceMs==(n<5?n:5)*20);
  assert(c.referenceRise==(n<6?n*(n+1)*250:10000));
  c.lossPpmPerSec=0;c.lastPpm=49000;c.flat=2;c.falling=0;c.observing=false;
  if(n==1)assert(c.pulse(stepTime+20000)==40); //20ms→500ppm, need1000→40ms.
  if(n==2)assert(c.pulse(stepTime+20000)==27); //gain averaged over two stairs.
  if(n==5)assert(c.pulse(stepTime+20000)==14);
  if(n==6)assert(c.pulse(stepTime+20000)==10); //five newest, first is discarded.
 }
 c.reset();assert(c.stepCount==0&&!c.trained);
 // Replay the actual20→228ms failure. The69ppm wiggle must not enter the history.
 resetFirmware();c.steps[0].ms=25;c.steps[0].rise=4744;c.stepCount=1;c.stepHead=1;
 c.referenceMs=25;c.referenceRise=4744;c.trained=true;c.previousValid=true;
 c.lastPpm=46971;c.lastAt=237389;c.lossPpmPerSec=34.967f;c.record(20,237389);
 struct Reading {uint32_t at;int32_t ppm;bool valid;};
 const Reading replay[]={ REPLAY_ROWS };
 for(const auto &row:replay)c.update(row.at,row.ppm,row.valid);
 assert(c.mass==69&&c.stepCount==1&&c.referenceMs==25&&c.referenceRise==4744);
 assert(c.pulse(258411)==19); //Not228ms; keep the measured useful reference.
 std::mt19937 rng(20261106);
 for(int history=0;history<20000;history++){
  resetFirmware();uint32_t t=UINT32_MAX-50000;
  for(int n=0;n<100;n++){
   t+=2000+rng()%400;int32_t ppm=1000+rng()%59000;bool valid=rng()%20;
   c.update(t,ppm,valid);auto q=c.pulse(t);assert(q==0||(q>=5&&q<=1000));
   assert(c.lossPpmPerSec>=0&&c.lossPpmPerSec<=200);
   assert(c.stepCount<=5&&c.referenceMs<=5000&&c.referenceRise<=327675UL);
   if(q)c.record(q,t);
  }
 }
}
'''
code=code.replace('REPLAY_ROWS',replay_rows)
with tempfile.TemporaryDirectory(prefix='co2-test-') as folder:
    cpp=Path(folder)/'test.cpp';exe=Path(folder)/'test';cpp.write_text(code)
    subprocess.run(['g++','-std=c++11','-O2',str(cpp),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print('CO2: rolling1..5 stairs, real20→228ms replay corrected to19ms, proportional dose, plateau, rollover and20000 histories passed')
