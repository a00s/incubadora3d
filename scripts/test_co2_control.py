#!/usr/bin/env python3
"""Check the firmware's replenishment timing and retained dose interlocks."""
from pathlib import Path
import re
import subprocess
import tempfile

source = (Path(__file__).resolve().parents[1] / 'temperatura.ino').read_text()
function = source[source.index('bool co2ResponseWaitComplete('):source.index('void setup()')]
admission = re.search(r'if \((validCo2 && currentTime >= CO2_SENSOR_WARMUP_MS.*?)\) \{\s*int32_t pulseMs;',source,re.S).group(1)
recovery = re.search(r'bool recoveryReady = (.*?);',source,re.S).group(1)
advance = re.search(r'if \(co2DoorMode == 4\) co2DoorMode = 3;',source).group(0)
gate = re.search(r'bool doseResponseReady = (.*?);', source, re.S).group(1)
weak_probe = re.search(r'if \(!co2GainValidatedThisBoot \|\| co2LastResponseWeak\).*?;', source, re.S).group(0)
start = source.index('      if (pulseMs > lastCo2PulseMs + 20)')
caps = source[start:source.index('      co2_before_pump', start)]
initial = re.search(r'if \(lastCo2PulseMs == 0.*?\) \{.*?pulseMs = (.*?);', source, re.S).group(1)
gain_update = source[source.index('          if (max_co2_increase >= 50) {'):source.index('          if (max_co2_increase >= 50 && co2MaxRiseAt') ]
harness = r'''
#include <stdint.h>
#include <initializer_list>
#include <assert.h>
#define CO2_RESPONSE_LAG_MAX_MS 180000UL
#define CO2_CONTROL_MIN_PPM 49000L
#define CO2_SENSOR_WARMUP_MS 120000UL
#define CO2_TARGET_PPM 50000L
#define CO2_TOLERANCE_PPM 1000L
#define DELAY_MINIMO 20
#define CO2_MAX_RISING_RATE_PPM_PER_MIN 300L
uint8_t co2DoorMode=0;
bool co2RatePpmMinReady=true;
bool co2GainValidatedThisBoot = false, co2LastResponseWeak = false;
int32_t lastCo2PulseMs = 0;
int32_t CO2i = 47700, co2RatePpmMin = -200;
unsigned long co2LastPulseAt = 100000, actualNow=120000;
unsigned long millis() {return actualNow;}
uint8_t co2ResponseLagSeconds = 180;
'''+function+'''
int32_t co2GainEstimatePpmPerMsX100=1200;
const int32_t CO2_MIN_GAIN_ESTIMATE_X100=50;
void learn(int32_t max_co2_increase) {
'''+gain_update+'''
}

int32_t boundedProbe(int32_t pulseMs, int32_t pulseLimit) {
  if (!lastCo2PulseMs) pulseMs = '''+initial+''';
  else { '''+weak_probe+''' }
'''+caps+'''
  return pulseMs;
}
bool admit(bool heaterPressPending, bool botao_co2_onoff=true, bool validCo2=true, unsigned long currentTime=120000) {
  actualNow=currentTime;
  int32_t co2ProjectedPpm=47000;
  bool doseResponseReady=true;
  uint8_t co2ClickCount=0;
  return '''+admission+''';
}
bool ready(unsigned long now, bool validCo2, int contador_pomp, bool co2TrendReady) {
  unsigned long currentTime=now;
  bool responseWaitComplete = co2ResponseWaitComplete(currentTime);
  bool recoveryReady = '''+recovery+''';
  return '''+gate+''';
}
'''+r'''
void markDoseSent() { '''+advance+''' }
int main() {
  lastCo2PulseMs=100;
  learn(10000); // New cylinder: increased flow is adopted immediately.
  assert(co2GainEstimatePpmPerMsX100==10000);
  learn(5000); // Depletion follows recent responses gradually.
  assert(co2GainEstimatePpmPerMsX100==8333);
  for (int n=0;n<10;n++) learn(5000);
  assert(co2GainEstimatePpmPerMsX100<5100);
  learn(0); assert(co2LastResponseWeak);
  lastCo2PulseMs=0; co2GainValidatedThisBoot=false; co2LastResponseWeak=false;
  assert(admit(0));
  assert(!admit(true)); // No automatic dose while a possible long press is pending.
  assert(!admit(0,false) && !admit(0,true,false));

  co2LastPulseAt=119500;assert(!admit(0)); // A fresh manual pulse prevents a duplicate automatic shot.
  co2LastPulseAt=100000;
  assert(!admit(0,true,true,119999)); // Sensor warmup is never bypassed.
  co2DoorMode=4; CO2i=47700; co2RatePpmMin=-200;
  assert(ready(100001,true,30,false)); // First close dose: no stale counter/trend wait.
  assert(!ready(100001,false,30,false));
  co2RatePpmMin=500; assert(!ready(100001,true,30,false));
  co2RatePpmMin=-200; CO2i=49000; assert(!ready(100001,true,30,false));
  CO2i=47700; markDoseSent(); assert(co2DoorMode==3);
  assert(!ready(159999,true,30,false)); // No repeated immediate recovery dose.
  assert(!ready(160000,true,30,false)); // Falling recovery ignores obsolete counter.
  co2RatePpmMin=0; assert(!ready(160000,true,30,false));
  assert(!ready(159999,true,30,false));
  co2RatePpmMin=10; assert(!ready(160000,true,30,false));
  co2RatePpmMin=500; assert(!ready(160000,true,30,false));
  co2RatePpmMin=-200; co2DoorMode=0;
  // Restart near target: the first probe stays small, then escapes the old 40 ms cap.
  assert(boundedProbe(80,80) == 20);
  lastCo2PulseMs = 20;
  for (int expected : {40,60,80,80}) {
    co2LastResponseWeak = true;
    lastCo2PulseMs = boundedProbe(20,80);
    assert(lastCo2PulseMs == expected);
  }
  assert(boundedProbe(80,25) == 25); // A small deficit still limits the pulse.
  co2GainValidatedThisBoot = true; co2LastResponseWeak = false;
  assert(boundedProbe(35,80) == 35);
  assert(boundedProbe(100,80) == 80);
  lastCo2PulseMs = 80;
  assert(boundedProbe(900,1000) == 100); // Valid gain also ramps rather than jumping.
  for (int expected : {100,120,140,160,180,200}) {
    lastCo2PulseMs = boundedProbe(900,1000);
    assert(lastCo2PulseMs == expected);
  }
  assert(boundedProbe(900,25) == 25); // Deficit can shrink immediately.
  lastCo2PulseMs = 1000;
  assert(boundedProbe(1200,1000) == 1000);
  assert(boundedProbe(5,80) == 20);
  co2LastResponseWeak = true; lastCo2PulseMs = 40;
  assert(boundedProbe(20,80) == 60);
  for (uint8_t mode : {0,3}) {
    co2DoorMode=mode;
    for (int rate : {-200,0,500}) {
      co2RatePpmMin=rate;
      assert(!ready(279999,true,0,true));
      assert(ready(280000,true,0,true));
    }
  }
  co2DoorMode=0;
  assert(!ready(280000,false,0,true));
  assert(!ready(280000,true,1,true));
  assert(!ready(280000,true,0,false));
}
'''
with tempfile.TemporaryDirectory(prefix='incubadora-control-') as folder:
    cpp = Path(folder) / 'control.cpp'
    binary = Path(folder) / 'control-test'
    cpp.write_text(harness)
    subprocess.run(['g++', '-std=c++11', '-Wall', '-Wextra', '-Werror', str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('CO2 replenishment timing and interlock checks passed.')
