#!/usr/bin/env python3
"""Exercise the real dosing header and extracted Uno gates, including uint32 wrap."""
from pathlib import Path
import subprocess
import tempfile
from co2_firmware_harness import harness
code=harness()+r'''
#include <random>
int main(){
 resetFirmware();CO2i=48000;co2DoseModel.update(100000,CO2i,true);
 assert(firmwarePulse(119999)==0);assert(firmwarePulse(120000)==5);
 assert(firmwarePulse(120000,false)==0);assert(firmwarePulse(120000,true,false)==0);
 assert(firmwarePulse(120000,true,true,1)==0);assert(firmwarePulse(120000,true,true,0,true)==0);
 recordAutomatic(5,120000);assert(!firmwareReady(139999));assert(!firmwareReady(219999));
 assert(firmwareReady(220000)); // Unknown-flow calibration gets a full observation window.
 co2DoseModel.trained=true;co2DoseModel.gain=70;co2DoseModel.lastPpm=CO2i=49000;
 co2Rate=3;updateCo2RecentRise(220000);assert(!firmwareReady(220000));
 co2Rate=-1;assert(!firmwareReady(225999));assert(firmwareReady(226000));
 auto p=co2DoseModel.pulse(226000);co2DoseModel.gain=140;
 assert(co2DoseModel.pulse(226000)<=p); // A larger learned flow reduces opening.
 co2DoseModel.lastPpm=51000;assert(co2DoseModel.pulse(226000)==0);
 co2DoseModel.lastPpm=49000;co2DoseModel.reset(true);
 assert(!co2DoseModel.trained&&co2DoseModel.referenceMs==5&&co2DoseModel.inventory()>0);
 // Calibration includes gas loss; a net fall alone does not imply zero gas.
 resetFirmware();auto &c=co2DoseModel;c.update(120000,48000,true);c.record(20,120000);
 for(uint32_t t=122000;t<=220000;t+=2000)c.update(t,48000-(t-120000)/1000*10,true);
 assert(c.trained&&c.gain>=1&&c.gain<=500);
 // Restarting at an arbitrary phase must not complete calibration before the probe.
 resetFirmware();c.update(37123,48000,true);c.record(5,100345);
 c.update(160345,48300,true);assert(!c.trained);
 c.update(200345,48000,true); // A long sampling gap is discarded, not learned.
 assert(!c.trained);
 // No response returns to isolated probes rather than learning an infinite opening.
 resetFirmware();c.update(120000,48000,true);c.record(5,120000);
 for(uint32_t t=122000;t<=220000;t+=2000)c.update(t,48000-(t-120000)/1000*20,true);
 assert(!c.trained&&c.referenceMs<=100);assert(c.pulse(220000)<=18);
 // Isolated failed probes learn opening overhead, not fixed gas flow.
 resetFirmware();c.update(120000,48000,true);uint32_t now=120000;int32_t ppm=48000;
 for(uint16_t duration: {5,10,15}){
  c.record(duration,now);
  for(int j=0;j<50;j++){
   ppm-=c.loss(ppm)*2;if(duration==15 && j==30)ppm+=500;
   now+=2000;c.update(now,ppm,true);
  }
 }
 assert(c.zeroMs==10&&c.trained&&c.floorLearned);
 c.trained=false;c.record(20,now);
 for(int j=0;j<50;j++){ppm-=c.loss(ppm)*2;now+=2000;c.update(now,ppm,true);}
 assert(c.zeroMs==10); // A loss of contact/flow cannot invent a larger mechanical delay.
 c.update(now+2000,53500,true);assert(c.zeroMs==0&&!c.floorLearned);
 // A full manual queue retains every commanded duration, including the overflow shot.
 resetFirmware();for(int i=0;i<5;i++)c.record(20,1000+i*100);
 uint32_t sum=0;for(auto &s:c.shots)sum+=s.ms;assert(sum==100);
 // Unsigned timer subtraction survives millis rollover.
 resetFirmware();c.previousValid=true;c.lastPpm=48000;c.trained=true;
 recordAutomatic(5,UINT32_MAX-10000);assert(!firmwareReady(9000));assert(firmwareReady(11000));
 // Random numerical states use only sensor/firmware bounds and actual API calls.
 std::mt19937 rng(20261106);
 for(int history=0;history<20000;history++){
  resetFirmware();uint32_t t=UINT32_MAX-50000;
  for(int n=0;n<100;n++){
   t+=2000+(rng()%400);int32_t ppm=1000+rng()%59000;bool valid=rng()%20;
   c.update(t,ppm,valid);uint16_t q=c.pulse(t);assert(q==0||(q>=5&&q<=1000));
   assert(c.gain>=1&&c.gain<=500);if(q)c.record(q,t);
  }
 }
}
'''
with tempfile.TemporaryDirectory(prefix='co2-test-') as folder:
    cpp=Path(folder)/'test.cpp';exe=Path(folder)/'test'
    cpp.write_text(code)
    subprocess.run(['g++','-std=c++11','-O2',str(cpp),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print('CO2: real gates, adaptive flow, delayed inventory, no response, rollover, 20000 histories passed')
