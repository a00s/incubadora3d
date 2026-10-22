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
#include <initializer_list>
#include <assert.h>
#define CO2_SENSOR_WARMUP_MS 120000UL
unsigned long clockMs = 0;
unsigned long millis() { return clockMs; }
unsigned long co2LastPulseAt = 0;
bool co2RatePpmMinReady = true, co2TrendReady = true;
int32_t co2RatePpmMin = -100;
uint8_t co2ResponseLagSeconds = 120;
uint8_t co2RateHistoryNext = 0;
unsigned long co2RateHistoryTime[16] = {};
'''+constants+function+r'''
void measure(unsigned long now, unsigned long windowMs = 30000UL) {
  clockMs = now;
  co2RateHistoryTime[co2RateHistoryNext] = now - windowMs;
  updateCo2Loss(true);
}

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

  measure(100000);
  assert(lossCm3Hour == -1 && !lossStable);
  // A window crossing the response boundary cannot produce even a provisional value.
  measure(120000);
  assert(lossCm3Hour == -1 && lossWindows == 0);
  measure(149999);
  assert(lossCm3Hour == -1 && lossWindows == 0);
  measure(150000);
  assert(lossCm3Hour == 11 && !lossStable && lossWindows == 1);
  measure(152000);
  assert(!lossStable && lossWindows == 1); // Overlapping window.
  // Actual 45-second windows cannot count again after only 30 seconds.
  measure(180000,45000);
  assert(!lossStable && lossWindows == 1);
  measure(195000,45000);
  assert(!lossStable && lossWindows == 2);
  measure(225000);
  assert(lossStable && lossWindows == 3);
  co2RatePpmMin = -300; measure(227000);
  assert(lossCm3Hour == 33 && !lossStable && lossWindows == 1);
  // Forty frequent doses never produce confidence from contaminated windows.
  for (int i=0; i<40; ++i) {
    co2LastPulseAt = clockMs;
    measure(co2LastPulseAt + 2000);
    assert(!lossStable && lossWindows == 0);
    measure(co2LastPulseAt + 32000);
    assert(!lossStable && lossWindows == 0);
    measure(co2LastPulseAt + 120000);
    assert(!lossStable && lossWindows == 0);
  }
  // Frequent doses retain the last measurement, marked as held rather than fresh.
  assert(lossCm3Hour == 33 && !lossFresh && !lossStable);
  for (uint8_t lag : {90,120,180}) {
    co2ResponseLagSeconds = lag;
    co2LastPulseAt = clockMs;
    measure(co2LastPulseAt + 2000);
    measure(co2LastPulseAt + lag*1000UL + 29999);
    assert(lossCm3Hour == 33 && !lossFresh && lossWindows == 0);
    measure(co2LastPulseAt + lag*1000UL + 30000);
    assert(lossCm3Hour == 33 && !lossStable && lossWindows == 1);
    measure(clockMs + 30000);
    assert(!lossStable && lossWindows == 2);
    measure(clockMs + 30000);
    assert(lossStable && lossWindows == 3);
    updateCo2Loss(false);
    assert(lossCm3Hour == 33 && !lossFresh && !lossStable && lossWindows == 0);
  }
  co2RatePpmMin = 0; measure(clockMs + 30000);
  assert(lossCm3Hour == 0 && !lossStable);
  measure(clockMs + 30000); measure(clockMs + 30000);
  assert(lossStable);
  co2TrendReady = false; measure(clockMs + 2000);
  assert(lossStable); // Independent of the controller's ready state.
  co2RatePpmMin = 100; measure(clockMs + 2000);
  assert(lossCm3Hour == 0 && !lossStable && lossWindows == 0);
  measure(clockMs + 600001);
  assert(lossCm3Hour == 0 && !lossFresh && !lossStable);
  co2RatePpmMinReady = false; co2RatePpmMin = -100;
  measure(clockMs + 2000);
  assert(lossCm3Hour == 0 && !lossFresh && lossWindows == 0);

}

'''
with tempfile.TemporaryDirectory(prefix='incubadora-loss-') as folder:
    cpp = Path(folder) / 'loss.cpp'
    binary = Path(folder) / 'loss-test'
    cpp.write_text(harness)
    subprocess.run(['g++', '-std=c++11', '-Wall', '-Wextra', '-Werror', str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('Loss estimator and alert color regression checks passed.')
