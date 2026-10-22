#!/usr/bin/env python3
"""Exercise the actual firmware loss estimator with simulated sensor time/state."""
from pathlib import Path
import re
import subprocess
import tempfile

source = (Path(__file__).resolve().parents[1] / 'temperatura.ino').read_text()
constants = source[source.index('const uint16_t CO2_GAS_VOLUME_CM3'):source.index('// Variáveis globais para aprendizado adaptativo')]
function = source[source.index('void updateCo2Loss(bool valid)'):source.index('\nvoid drawTextChanges')]
colors = source[source.index("void setDisplayBackground()"):source.index("void drawCo2Icon(")]
alert = re.search(r"bool alert = (.*);", source).group(1)
harness = r'''
#include <stdint.h>
#include <assert.h>
#define CO2_SENSOR_WARMUP_MS 120000UL
unsigned long clockMs = 0;
unsigned long millis() { return clockMs; }
unsigned long co2LastPulseAt = 0;
bool co2RatePpmMinReady = true, co2TrendReady = true;
int32_t co2RatePpmMin = -100;
uint8_t co2ResponseLagSeconds = 120;
'''+constants+function+r'''
struct ColorRecorder {
  uint8_t r, g, b;
  void setColor(int, uint8_t red, uint8_t green, uint8_t blue) {r=red;g=green;b=blue;}
} ucg;
bool displayAlert = false;
'''+colors+'''
bool alertFor(int co2Quality, int tempQuality, int safetyAlert, bool co2RangeWrapLatched) {
  return '''+alert+''';
}
'''+r'''
int main() {
  assert(!alertFor(1, 1, 0, false));
  assert(!alertFor(2, 2, 0, false));
  assert(alertFor(-1, 1, 0, false));
  assert(alertFor(1, -1, 0, false));
  assert(alertFor(0, 1, 0, false));
  assert(alertFor(1, 0, 0, false));
  assert(alertFor(1, 1, 2, false));
  assert(alertFor(1, 1, 0, true));
  setDisplayBackground(); assert(ucg.r==8 && ucg.g==18 && ucg.b==30);
  setDisplayForeground(70,235,145); assert(ucg.r==70 && ucg.g==235 && ucg.b==145);
  displayAlert = true;
  setDisplayBackground(); assert(ucg.r==160 && ucg.g==8 && ucg.b==12);
  setDisplayForeground(255,65,75); assert(ucg.r==255 && ucg.g==255 && ucg.b==255);
  displayAlert = false;
  setDisplayBackground(); assert(ucg.r==8 && ucg.g==18 && ucg.b==30);

  clockMs = 100000; updateCo2Loss(true);
  assert(lossCm3Hour == -1 && !lossStable);
  clockMs = 120000; updateCo2Loss(true);
  assert(lossCm3Hour == 11 && !lossStable && lossWindows == 1);
  // Correlated readings within one rolling window do not add confidence.
  clockMs = 122000; updateCo2Loss(true);
  assert(!lossStable && lossWindows == 1);
  clockMs = 150000; updateCo2Loss(true);
  assert(!lossStable && lossWindows == 2);
  clockMs = 180000; updateCo2Loss(true);
  assert(lossStable && lossWindows == 3);
  // A large change restarts evidence collection.
  clockMs = 182000; co2RatePpmMin = -300; updateCo2Loss(true);
  assert(lossCm3Hour == 33 && !lossStable && lossWindows == 1);
  // Repeated replenishment for over an hour retains a usable estimate.
  for (int i=0; i<40; ++i) {
    co2LastPulseAt = clockMs;
    clockMs += 2000; updateCo2Loss(true);
    assert(lossCm3Hour >= 0 && !lossStable && lossWindows == 0);
    clockMs = co2LastPulseAt + 32000; updateCo2Loss(true);
    assert(!lossStable && lossWindows == 1);
    clockMs += 30000; updateCo2Loss(true);
    assert(!lossStable && lossWindows == 2);
    clockMs += 30000; updateCo2Loss(true);
    assert(!lossStable && lossWindows == 3); // Still awaiting valve response.
    clockMs = co2LastPulseAt + 122000; updateCo2Loss(true);
    assert(lossCm3Hour == 33 && lossStable);
  }
  co2RatePpmMin = 100; clockMs += 2000; updateCo2Loss(true);
  assert(lossCm3Hour == 33 && !lossStable && lossWindows == 0);
  clockMs += 600001; updateCo2Loss(true);
  assert(lossCm3Hour == -1 && !lossStable);
  co2RatePpmMin = 0; updateCo2Loss(true);
  assert(lossCm3Hour == 0 && !lossStable);
  clockMs += 30000; updateCo2Loss(true);
  clockMs += 30000; updateCo2Loss(true);
  assert(lossCm3Hour == 0 && lossStable);
  // Confidence depends on sample consistency, not the control's ready flag.
  co2TrendReady = false; updateCo2Loss(true);
  assert(lossStable);
  updateCo2Loss(false);
  assert(lossCm3Hour == -1 && !lossStable && lossWindows == 0);
}

'''
with tempfile.TemporaryDirectory(prefix='incubadora-loss-') as folder:
    cpp = Path(folder) / 'loss.cpp'
    binary = Path(folder) / 'loss-test'
    cpp.write_text(harness)
    subprocess.run(['g++', '-std=c++11', '-Wall', '-Wextra', '-Werror', str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('Loss estimator and alert color regression checks passed.')
