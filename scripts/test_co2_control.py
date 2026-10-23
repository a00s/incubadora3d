#!/usr/bin/env python3
"""Check the firmware's replenishment timing and retained dose interlocks."""
from pathlib import Path
import re
import subprocess
import tempfile

source = (Path(__file__).resolve().parents[1] / 'temperatura.ino').read_text()
function = source[source.index('bool co2ResponseWaitComplete('):source.index('void setup()')]
gate = re.search(r'bool doseResponseReady = (.*?);', source, re.S).group(1)
harness = r'''
#include <stdint.h>
#include <assert.h>
#define CO2_CONTROL_MIN_PPM 49000L
int32_t CO2i = 47700, co2RatePpmMin = -200;
unsigned long co2LastPulseAt = 100000;
uint8_t co2ResponseLagSeconds = 180;
'''+function+'''
bool ready(unsigned long now, bool validCo2, int contador_pomp, bool co2TrendReady) {
  bool responseWaitComplete = co2ResponseWaitComplete(now);
  return '''+gate+''';
}
'''+r'''
int main() {
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
