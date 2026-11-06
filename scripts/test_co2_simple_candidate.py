#!/usr/bin/env python3
"""Check the requested arithmetic, separately from closed-loop acceptance."""
from pathlib import Path
import subprocess
import tempfile
from co2_firmware_harness import ROOT, harness

model = Path(globals().get('MODEL_PATH', ROOT / 'firmware/experimentos/co2_proporcional_simples.h'))
code = harness(model) + r'''
int main() {
  resetFirmware(); auto &c = co2DoseModel;
  c.update(100000,48050,true);c.update(110000,48025,true);c.update(120000,48000,true);CO2i=48000;
  assert(firmwarePulse(119999)==0);assert(firmwarePulse(120000)==20);
  assert(firmwarePulse(120000,false)==0);assert(firmwarePulse(120000,true,false)==0);
  assert(firmwarePulse(120000,true,true,1)==0);assert(firmwarePulse(120000,true,true,0,true)==0);
  resetFirmware();
  c.previousValid=true; c.lastPpm=49000; c.falling=2;
  c.trained=true; c.referenceMs=20; c.referenceRise=500;c.lastProbeMs=20;
  assert(c.pulse(120000)==40); //20ms gave500ppm;1000ppm missing.
  c.lastPpm=49900; assert(c.pulse(120000)==5); //4ms below mechanical minimum.
  c.lastPpm=51000; assert(c.pulse(120000)==0);
  c.falling=0; c.flat=0; assert(c.pulse(120000)==0);
  c.lastPpm=45000; c.flat=2; assert(c.pulse(120000)==40);
  c.lastProbeMs=80;c.referenceMs=80;c.referenceRise=2000;c.lastPpm=41570;
  assert(c.pulse(120000)==100); //Raw338ms cannot jump from80ms to338ms.
  c.record(100,120000);c.falling=2;assert(c.pulse(140100)==100);
  c.lastPpm=49900;assert(c.pulse(140100)==5); //Only increases are limited.
  resetFirmware(); uint32_t t=120000; int32_t ppm=10000;
  for(int n=1;n<=6;n++) {
    c.update(t,ppm,true); c.record(20,t);
    for(int j=1;j<=10;j++)c.update(t+j*2000,ppm+n*500*(j<5?j:5)/5,true);
    ppm+=n*500; t+=20000;
    assert(c.stepCount==(n<5?n:5));
    assert(c.referenceMs==(unsigned)(n<5?n:5)*20);
    assert(c.referenceRise==(unsigned)(n<6?n*(n+1)*250:10000));
  }
  // No total66ms budget, timeout, or response threshold blocks new commands.
  resetFirmware(); c.update(120000,5700,true); c.record(20,120000);
  unsigned expected=40,commands=1;
  for(uint32_t at=122000;at<=720000;at+=2000) {
    c.update(at,5700-(at-120000)/10000,true);
    if(c.ready(at)) {
      auto ms=c.pulse(at); assert(ms==expected); c.record(ms,at);
      expected=expected>=80?100:expected+20;commands++;
    }
  }
  assert(c.lastMs>66 && !c.trained && commands>10);
  c.reset();c.previousValid=true;c.flat=2;c.lastPpm=5700;
  assert(c.pulse(800000)==20); //Restart calibration, not the last doubled probe.
  c.record(20,800000);c.update(802000,5699,true);c.update(804000,5698,true);c.update(806000,5697,true);
  assert(!c.ready(819999));assert(c.pulse(820000)==40);
  c.update(822000,6200,true);assert(!c.ready(822000)); //Do not double during a rise.
  c.update(824000,6700,true);c.update(826000,6701,true);c.update(828000,6702,true);
  assert(c.trained&&c.stepCount==1); //Switch to the measured proportion immediately.
  c.lossPpmPerSec=0;c.lastPpm=49000;c.referenceMs=20;c.referenceRise=500;
  assert(c.pulse(830000)==40); //Not60 from continuing the calibration sequence.
  // Missing gain never divides by zero; a valid large ratio cannot overflow32bits.
  c.previousValid=true; c.falling=2; c.observing=false;
  c.trained=true; c.referenceMs=400000; c.referenceRise=1000;
  c.lastProbeMs=1000;c.lastPpm=1000; assert(c.pulse(900000)==100);
  c.reset(); assert(c.stepCount==0 && !c.trained);
  c.update(120000,39600,true);c.record(20,120000);c.record(40,142000);
  c.record(60,164000);c.record(80,186000);
  c.update(200000,41000,true);c.update(206000,42400,true);
  c.update(208000,42401,true);c.update(210000,42402,true);
  assert(c.trained&&c.referenceMs==80&&c.lastMs==80); //Not the200ms sum.
  assert(c.pulse(210000)<=100);
  // Observed372ppm must not become5117ppm by adding estimated loss.
  c.reset();c.update(100000,46900,true);c.record(8,100000);c.lossPpmPerSec=40;
  for(uint32_t t=102000;t<=216000;t+=2000)c.update(t,46900,true);
  c.update(218625,47272,true);c.update(220625,47272,true);c.update(222625,47272,true);
  assert(c.trained&&c.referenceMs==8&&c.referenceRise==372);
  // The same deficit now asks for more time, still bounded to+20ms.
  c.lossPpmPerSec=0;assert(c.pulse(222625)==28);
  // Five observed stairs keep loss estimates out of the gain average.
  c.referenceMs=67;c.referenceRise=16990;c.lastProbeMs=6;c.lastPpm=47273;
  assert(c.pulse(222625)==11); //Old inflated42270ppm would ask for only5ms.
}
'''
with tempfile.TemporaryDirectory(prefix='co2-simple-candidate-') as folder:
    cpp=Path(folder)/'test.cpp'; exe=Path(folder)/'test'
    cpp.write_text(code)
    subprocess.run(['g++','-std=c++11','-O2',str(cpp),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print('Candidate arithmetic passed; this does NOT certify closed-loop dosing.')
