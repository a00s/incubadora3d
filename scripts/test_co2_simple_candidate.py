#!/usr/bin/env python3
"""Check the requested arithmetic, separately from closed-loop acceptance."""
from pathlib import Path
import subprocess
import tempfile
from co2_firmware_harness import ROOT, harness

model = ROOT / 'firmware/experimentos/co2_proporcional_simples.h'
code = harness(model) + r'''
int main() {
  resetFirmware(); auto &c = co2DoseModel;
  c.previousValid=true; c.lastPpm=49000; c.falling=2;
  c.trained=true; c.referenceMs=20; c.referenceRise=500;
  assert(c.pulse(120000)==40); //20ms gave500ppm;1000ppm missing.
  c.lastPpm=49900; assert(c.pulse(120000)==5); //4ms below mechanical minimum.
  c.lastPpm=51000; assert(c.pulse(120000)==0);
  c.falling=0; c.flat=0; assert(c.pulse(120000)==0);
  c.lastPpm=45000; c.flat=2; assert(c.pulse(120000)==200);
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
  for(uint32_t at=122000;at<=720000;at+=2000) {
    c.update(at,5700-(at-120000)/10000,true);
    if(c.ready(at)) {
      auto ms=c.pulse(at); assert(ms==20); c.record(ms,at);
    }
  }
  assert(c.lastMs>66 && !c.trained);
  // Missing gain never divides by zero; a valid large ratio cannot overflow32bits.
  c.previousValid=true; c.falling=2; c.observing=false;
  c.trained=true; c.referenceMs=400000; c.referenceRise=1000;
  c.lastPpm=1000; assert(c.pulse(800000)==1000);
  c.reset(); assert(c.stepCount==0 && !c.trained);
}
'''
with tempfile.TemporaryDirectory(prefix='co2-simple-candidate-') as folder:
    cpp=Path(folder)/'test.cpp'; exe=Path(folder)/'test'
    cpp.write_text(code)
    subprocess.run(['g++','-std=c++11','-O2',str(cpp),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print('Candidate arithmetic passed; this does NOT certify closed-loop dosing.')
