#!/usr/bin/env python3
"""Check dose arithmetic and delayed command attribution through real Uno gates."""
from pathlib import Path
import subprocess
import tempfile
from co2_firmware_harness import ROOT, harness
model = Path(globals().get('MODEL_PATH', ROOT/'firmware/experimentos/co2_proporcional_simples.h'))
code = harness(model) + r'''
int main() {
  resetFirmware(); auto &c=co2DoseModel;
  c.update(100000,48050,true); c.update(110000,48025,true); c.update(120000,48000,true); CO2i=48000;
  assert(firmwarePulse(119999)==0); assert(firmwarePulse(120000)==20);
  assert(firmwarePulse(120000,false)==0); assert(firmwarePulse(120000,true,false)==0);
  assert(firmwarePulse(120000,true,true,1)==0); assert(firmwarePulse(120000,true,true,0,true)==0);
  c.reset(); c.previousValid=true;c.lastPpm=49000;c.falling=2;
  c.trained=true;c.referenceMs=20;c.referenceRise=500;c.lastProbeMs=20;
  assert(c.pulse(120000)==40); // Actual20ms/500ppm, missing1000ppm.
  c.lastPpm=49900;assert(c.pulse(120000)==5);
  c.lastPpm=50890;assert(c.pulse(120000)==0); // No unbounded loss*response term.
  c.lastPpm=50283;assert(c.pulse(120000)==0);
  c.lastPpm=50000;assert(c.pulse(120000)==0); // No history, no invented maintenance.
  c.lastPpm=51000;assert(c.pulse(120000)==0);
  c.lastPpm=48000;c.lastProbeMs=80;c.referenceMs=2500;c.referenceRise=1;
  assert(c.pulse(120000)==100); // Largest physical history, product fits32bits.
  c.record(100,120000);c.falling=2;assert(c.pulse(140001)<=100);
  c.reset(); c.previousValid=true;c.flat=2;c.lastPpm=5700;
  uint32_t at=120000;
  for(unsigned n=0;n<7;n++,at+=22000) {
    c.flat=2;
    unsigned expected=n<5?(n+1)*20:100;
    assert(c.pulse(at)==expected);c.record(expected,at);
  }
  assert(!c.trained); // No fake gain from elapsed time.
  // First20ms response must not be attributed to the later60ms command.
  c.reset();c.update(120000,45733,true);c.record(20,120000);
  c.update(142000,45336,true);c.record(40,142000);
  c.update(164000,44942,true);c.record(60,164000);
  c.update(174000,44735,true);
  c.update(180000,45400,true);c.update(186000,45861,true);
  c.update(188000,45860,true);c.update(190000,45859,true);
  assert(c.trained&&c.stepCount==1&&c.referenceMs==20&&c.referenceRise==1126);
  assert(c.arrivalMs==54000&&c.responseMs==66000);
  assert(c.pulse(190000)==0); // Already commanded40+60ms cover remaining deficit.
  c.lastPpm=38000;assert(c.pulse(190000)>0); // Pending gas doesn't impose a fixed pause.
  // Real combined stair:20+40+60ms, valley169044, peak231615.
  // Duration must exclude the46s separating first and last contributing commands.
  c.reset();c.update(120648,46720,true);c.record(20,120648);
  c.update(141632,45908,true);c.record(40,141632);
  c.update(166768,45752,true);c.record(60,166768);
  c.update(169044,45733,true);c.update(231615,52434,true);
  c.update(233615,52434,true);c.update(235615,52434,true);
  assert(c.referenceMs==120&&c.referenceRise==6701);
  assert(c.arrivalMs==48396&&c.responseMs==64847); // Not110967ms.
  // Restore the first isolated-step model for reset preservation checks.
  c.arrivalMs=54000;c.referenceMs=20;
  // Door/re-enable/invalid-read reset preserves measured gain; full reset doesn't.
  auto before=c.referenceRise;c.reset(true);
  assert(c.trained&&c.referenceMs==20&&c.referenceRise==before);
  assert(!c.previousValid&&!c.observing&&c.arrivalMs==54000);
  for(auto &p:c.pending)assert(p.ms==0);
  c.reset();assert(!c.trained&&c.stepCount==0&&c.lastProbeMs==0);
  // Rolling history uses1..5 available useful stairs, replacing the oldest.
  uint32_t t=120000;int32_t ppm=10000;
  for(int n=1;n<=6;n++) {
    c.update(t,ppm,true);c.record(20,t);
    for(int j=1;j<=10;j++)c.update(t+j*2000,ppm+n*500*(j<5?j:5)/5,true);
    ppm+=n*500;t+=20000;
    assert(c.stepCount==(n<5?n:5));
    assert(c.referenceMs==(unsigned)(n<5?n:5)*20);
    assert(c.referenceRise==(unsigned)(n<6?n*(n+1)*250:10000));
  }
  // Noise of69ppm cannot replace a measured response with a fictitious weak gain.
  c.reset();c.update(120000,5700,true);c.record(20,120000);
  c.update(140000,5769,true);c.update(142000,5769,true);c.update(144000,5769,true);
  assert(!c.trained&&c.stepCount==0);
  // Maintenance must cover measured arrival, not just the minimum pulse interval.
  c.reset();c.previousValid=true;c.flat=2;c.lastPpm=50000;
  c.trained=true;c.referenceMs=20;c.referenceRise=500;c.lastProbeMs=20;
  c.arrivalMs=35000;c.responseMs=65000;
  for(int i=0;i<5;i++){c.pending[i].ms=20;c.pending[i].at=60000+i*20000;}
  assert(c.pulse(220000)==20); //35s horizon, limited to500ppm ->20ms.
  c.arrivalMs=0;assert(c.pulse(220000)==12); //20s minimum still applies.
  c.arrivalMs=35000;c.lastPpm=50500;assert(c.pulse(220000)==0);
  c.lastPpm=50900;assert(c.pulse(220000)==0);
  // Very old response timings must not multiply beyond available command history.
  c.lastPpm=50000;c.arrivalMs=0xffffffffUL;c.responseMs=20000;
  assert(c.pulse(220000)==20); //500ppm cap, bounded32bit arithmetic.
  c.referenceMs=2500;c.referenceRise=327675;c.lastPpm=49000;
  assert(c.pulse(220000)<=40); //Largest five-stair history and+20 cap.
  // Counter wrap uses unsigned elapsed time, without expiring a recent dose.
  c.reset();c.previousValid=true;c.flat=2;c.lastPpm=50000;
  c.trained=true;c.referenceMs=20;c.referenceRise=500;c.responseMs=60000;c.arrivalMs=40000;
  c.record(20,0xffffd8efUL);c.flat=2;
  assert(c.pulse(12000)==0); // Still in transit; no duplicate correction.
  c.flat=0;c.falling=0;assert(c.pulse(60000)==0); // Rising never starts another command.
}
'''
with tempfile.TemporaryDirectory(prefix='co2-simple-candidate-') as folder:
    cpp=Path(folder)/'test.cpp';exe=Path(folder)/'test';cpp.write_text(code)
    subprocess.run(['g++','-std=c++11','-O2',str(cpp),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print('Arithmetic, delayed attribution, pending quantities and preserved learning passed; physical stability remains separate.')
