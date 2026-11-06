#!/usr/bin/env python3
"""Real sketch gates + last-dose proportional calculation and measured loss refill."""
from pathlib import Path
import subprocess
import tempfile
from co2_firmware_harness import harness
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
 assert(c.pulse(120000)==10);c.lastPpm=46000;assert(c.pulse(120000)==22); // Upward extrapolation capped at10%.
 c.lastPpm=49000;c.referenceRise=4000;assert(c.pulse(120000)==5);
 c.falling=1;assert(!c.ready(120000));c.falling=2;assert(c.ready(120000));
 recordAutomatic(10,120000);assert(!firmwareReady(139999));
 c.falling=2;c.observing=true;assert(firmwareReady(140010)); // No additional observation pause.
 // A flat summit replenishes measured loss at the normal 20 s cadence.
 c.lastPpm=50000;c.falling=0;c.flat=2;c.lossPpmPerSec=20;c.referenceMs=20;c.referenceRise=2000;
 assert(c.pulse(140010)==5);c.lossPpmPerSec=0;assert(c.pulse(140010)==0);
 c.lastPpm=51000;c.lossPpmPerSec=20;assert(c.pulse(140010)==0);
 // A rising response forbids a new command, independent of the old rolling slope.
 c.update(150000,50000,true);c.update(152000,50025,true);assert(!c.ready(160000));
 // A real valley-to-peak rise remains useful even below ppm at the command.
 resetFirmware();c.update(100000,50000,true);c.record(20,100000);
 c.update(110000,47000,true);c.update(120000,47500,true);c.update(130000,49000,true);
 c.update(140000,48900,true);c.update(150000,48800,true);assert(c.trained);
 for(uint32_t t=160000;t<=220000;t+=10000)c.update(t,48800-(t-150000)/100,true);
 assert(c.trained&&c.referenceMs==20&&c.referenceRise>=2000);

 // Maintenance never relearns a false small gain from overlapping flat doses.
 c.lastPpm=50000;auto rise=c.referenceRise;c.record(5,230000);assert(!c.observing);
 c.update(232000,50000,true);c.update(234000,50000,true);assert(c.referenceRise==rise);
 c.reset(true);assert(!c.trained&&c.referenceMs==20&&c.hasSent);
 // No response cannot divide by zero; two declines must be in the same 20 s window.
 resetFirmware();c.update(100000,48000,true);c.update(102000,47900,true);
 assert(c.falling==1);c.update(130000,47800,true);assert(c.falling==0);
 c.update(132000,47700,true);c.update(134000,47600,true);assert(c.ready(134000));
 assert(c.pulse(134000)>=5);assert(c.projection(134000)==-1);
 // millis rollover keeps the full 20 s after the valve closes.
 resetFirmware();c.previousValid=true;c.lastPpm=48000;c.trained=true;c.referenceRise=2000;
 recordAutomatic(5,UINT32_MAX-10000);c.observing=false;c.falling=2;
 assert(!firmwareReady(9000));assert(firmwareReady(11000));
 std::mt19937 rng(20261106);
 for(int history=0;history<20000;history++){
  resetFirmware();uint32_t t=UINT32_MAX-50000;
  for(int n=0;n<100;n++){
   t+=2000+rng()%400;int32_t ppm=1000+rng()%59000;bool valid=rng()%20;
   c.update(t,ppm,valid);auto q=c.pulse(t);assert(q==0||(q>=5&&q<=1000));
   assert(c.lossPpmPerSec>=0&&c.lossPpmPerSec<=200);
   if(q)c.record(q,t);
  }
 }
}
'''
with tempfile.TemporaryDirectory(prefix='co2-test-') as folder:
    cpp=Path(folder)/'test.cpp';exe=Path(folder)/'test';cpp.write_text(code)
    subprocess.run(['g++','-std=c++11','-O2',str(cpp),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print('CO2: actual gates, proportional dose, two declines/20s, flat loss refill, no observation pause, rollover, 20000 histories passed')
