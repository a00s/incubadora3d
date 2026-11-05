#!/usr/bin/env python3
"""Run the real dosing model and firmware admission/timing functions on the host."""
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'temperatura.ino').read_text()

def function(signature):
    start = source.index(signature)
    brace = source.index('{', start)
    end, depth = brace + 1, 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end].replace('unsigned long', 'uint32_t')

macros = '\n'.join(re.findall(r'^#define CO2_[^\n]+', source, re.M))
admission = re.search(r'if \((validCo2 && currentTime >= CO2_SENSOR_WARMUP_MS.*?)\) \{\s*int32_t pulseMs;', source, re.S).group(1)
a = source.index('    bool responseWaitComplete =')
gates = source[a:source.index('    int32_t pulseLimit', a)]
header = root / 'firmware/incubadora/co2_dosing.h'
harness = '#include "' + str(header) + '"\n' + r'''
#include <cassert>
#include <cmath>
#include <cstdint>
#include <random>
''' + macros + r'''
int32_t CO2i=47000, co2RatePpmMin=-20, max_co2_increase=0, lastCo2PulseMs=0;
uint8_t co2DoorMode=0, co2RateHistoryCount=16;
int32_t co2RateHistoryPpm[16];
float co2Rate=0;
bool co2DoseResponsePending=false, co2RatePpmMinReady=true;
uint16_t co2NoisePpm=10, co2ResponseWaitSeconds=600;
uint32_t co2LastPulseAt=100000, co2MaxRiseAt=100000, actualNow=120000;
uint32_t millis() { return actualNow; }
''' + function('bool co2ResponseWaitComplete(') + function('void measureCo2Noise(') + r'''
bool ready(uint32_t currentTime, bool validCo2=true, int contador_pomp=0, bool co2TrendReady=true) {
''' + gates + r'''
  (void)contador_pomp; (void)co2TrendReady;
  return doseResponseReady;
}
bool admit(bool heaterPressPending=false, bool validCo2=true, bool botao_co2_onoff=true, uint32_t currentTime=120000) {
  actualNow=currentTime;
  bool doseResponseReady=true;
  uint8_t co2ClickCount=0;
  return ''' + admission + r''';
}
int main() {
  Co2DoseModel dose;
  assert(dose.pulse(48000,1000)==80);
  dose.learn(160,2000);
  assert(dose.pulse(4000,1000)==160); // Last duration * half deficit / last rise.
  assert(dose.pulse(1000,1000)==40);
  assert(dose.pulse(100000,1000)==176); // Controlled upward change, no fixed increment.
  dose.learn(100,1000);assert(dose.pulse(1000,1000)==50);
  dose.learn(100,500);assert(dose.pulse(1000,1000)==100); // Falling pressure.
  dose.learn(100,2000);assert(dose.pulse(1000,1000)==25); // Higher cylinder flow.
  dose.learn(100,0);assert(dose.pulse(48000,1000)==110); // No response: no divide by zero or reset.
  assert(!dose.fresh && !dose.trained);
  dose.learn(110,0);assert(dose.pulse(48000,1000)==121);
  assert(dose.pulse(0,1000)==0 && dose.pulse(-1,1000)==0);
  dose.reset();assert(dose.fresh && !dose.trained && dose.referenceMs==80);
  std::mt19937 rng(20261105);
  for(int i=0;i<20000;i++) {
    if(i%31==0)dose.reset();
    auto pulse=dose.pulse(1+rng()%50000,1000);
    assert(pulse>=5 && pulse<=1000);
    dose.learn(pulse,rng()%65536);
  }

  CO2i=47000; assert(admit());
  assert(!admit(true) && !admit(false,false) && !admit(false,true,false));
  assert(!admit(false,true,true,119999));
  CO2i=49500;assert(!admit());CO2i=47000;
  co2LastPulseAt=119500;assert(!admit());co2LastPulseAt=100000;
  assert(!ready(119999) && ready(120000)); // Exactly 20 seconds, including no detected response.
  co2DoseResponsePending=true;max_co2_increase=0;
  assert(ready(120000,true,30,false)); // Old cycle/stability counters cannot prolong the minimum.
  co2RatePpmMin=100;assert(!ready(120000)); // Still rising: wait beyond minimum.
  co2Rate=10;assert(!ready(120000));co2Rate=0; // New rise blocks even while old slope is falling.
  co2MaxRiseAt=110000;assert(!ready(120000));co2MaxRiseAt=100000;
  co2RatePpmMin=0;assert(ready(120000)); // Plateau: no need to wait until falling.
  co2RatePpmMin=-100;assert(ready(120000));
  assert(!ready(120000,false));
  co2RatePpmMinReady=false;assert(!ready(120000));co2RatePpmMinReady=true;
  for(co2DoorMode=0;co2DoorMode<=4;co2DoorMode++) {
    assert(!ready(119999));assert(ready(120000));
    co2RatePpmMin=100;assert(!ready(120000));co2RatePpmMin=0;
  }
  co2DoorMode=0;co2LastPulseAt=0;lastCo2PulseMs=0;assert(ready(120000));
  co2LastPulseAt=UINT32_MAX-1000;lastCo2PulseMs=100;
  assert(!ready(1000));
  assert(ready((uint32_t)(co2LastPulseAt+20000UL)));

  for(int i=0;i<16;i++)co2RateHistoryPpm[i]=2000+(i%2?80:-80);
  measureCo2Noise();assert(co2NoisePpm==160);
  for(int i=0;i<16;i++)co2RateHistoryPpm[i]=2000;
  measureCo2Noise();assert(co2NoisePpm==0);
}
'''
with tempfile.TemporaryDirectory(prefix='incubadora-co2-') as folder:
    cpp, exe = Path(folder)/'test.cpp', Path(folder)/'test'
    cpp.write_text(harness)
    subprocess.run(['g++','-std=c++11','-Wall','-Wextra','-Werror','-ftrapv',str(cpp),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print('CO2 last-dose calculation, 20s minimum, rise/plateau/fall, door and rollover checks passed.')
