#!/usr/bin/env python3
"""Check the firmware's replenishment timing and retained dose interlocks."""
from pathlib import Path
import re
import subprocess
import tempfile

source = (Path(__file__).resolve().parents[1] / 'temperatura.ino').read_text()
function = source[source.index('bool co2ResponseWaitComplete('):source.index('void setup()')]
admission = re.search(r'if \((validCo2 && currentTime >= CO2_SENSOR_WARMUP_MS.*?)\) \{\s*int32_t pulseMs;',source,re.S).group(1)
gate = re.search(r'bool doseResponseReady = (.*?);', source, re.S).group(1)
weak_probe = re.search(r'if \(!co2GainValidatedThisBoot \|\| co2LastResponseWeak\).*?;', source, re.S).group(0)
start = source.index('      if (pulseMs > pulseLimit)')
caps = source[start:source.index('      co2_before_pump', start)]
initial = re.search(r'if \(lastCo2PulseMs == 0\) \{.*?pulseMs = (.*?);', source, re.S).group(1)
harness = r'''
#include <stdint.h>
#include <initializer_list>
#include <assert.h>
#define CO2_CONTROL_MIN_PPM 49000L
#define CO2_SENSOR_WARMUP_MS 120000UL
#define CO2_TARGET_PPM 50000L
#define CO2_TOLERANCE_PPM 1000L
#define DELAY_MINIMO 20
bool co2GainValidatedThisBoot = false, co2LastResponseWeak = false;
int32_t lastCo2PulseMs = 0;
int32_t CO2i = 47700, co2RatePpmMin = -200;
unsigned long co2LastPulseAt = 100000;
uint8_t co2ResponseLagSeconds = 180;
'''+function+'''
int32_t boundedProbe(int32_t pulseMs, int32_t pulseLimit) {
  if (!lastCo2PulseMs) pulseMs = '''+initial+''';
  else { '''+weak_probe+''' }
'''+caps+'''
  return pulseMs;
}
bool admit(uint8_t doorButtonStep, bool botao_co2_onoff=true, bool validCo2=true) {
  unsigned long currentTime=120000;
  int32_t co2ProjectedPpm=47000;
  bool doseResponseReady=true;
  uint8_t co2ClickCount=0;
  return '''+admission+''';
}
bool ready(unsigned long now, bool validCo2, int contador_pomp, bool co2TrendReady) {
  bool responseWaitComplete = co2ResponseWaitComplete(now);
  return '''+gate+''';
}
'''+r'''
int main() {
  assert(admit(0));
  assert(!admit(1) && !admit(2)); // No automatic dose during a pending door gesture.
  assert(!admit(0,false) && !admit(0,true,false));

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
  assert(boundedProbe(5,80) == 20);
  co2LastResponseWeak = true; lastCo2PulseMs = 40;
  assert(boundedProbe(20,80) == 60);
  assert(!ready(159999, true, 0, true));
  assert(ready(160000, true, 0, true)); // Falling at 47,700: no 180 s wait.
  assert(!ready(160000, false, 0, true));
  assert(!ready(160000, true, 1, true));
  assert(!ready(160000, true, 0, false)); // Sustained trend still required.
  co2RatePpmMin = 500;
  assert(!ready(160000, true, 0, true)); // Rising: preserve full response wait.
  assert(ready(280000, true, 0, true));
  co2RatePpmMin = -50;
  assert(!ready(160000, true, 0, true)); // Small/noisy change is insufficient.
  co2RatePpmMin = -51;
  assert(ready(160000, true, 0, true));
  CO2i = 49000;
  assert(!ready(160000, true, 0, true)); // Near target: no early-dose shortcut.
  assert(ready(280000, true, 0, true));
  co2ResponseLagSeconds = 90;
  assert(!ready(189999, true, 0, true));
  assert(ready(190000, true, 0, true));
}
'''
with tempfile.TemporaryDirectory(prefix='incubadora-control-') as folder:
    cpp = Path(folder) / 'control.cpp'
    binary = Path(folder) / 'control-test'
    cpp.write_text(harness)
    subprocess.run(['g++', '-std=c++11', '-Wall', '-Wextra', '-Werror', str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('CO2 replenishment timing and interlock checks passed.')
