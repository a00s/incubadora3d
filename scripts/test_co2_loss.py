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
int32_t CO2i = 50000;
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
  assert(lossCm3Hour == -1 && !lossFresh);
  co2RatePpmMin = 100; measure(120000);
  assert(lossStartAt == 0 && lossCm3Hour == -1);
  co2RatePpmMin = -100; co2TrendReady = false; measure(130000);
  assert(lossStartAt == 130000);
  finishCo2Loss();
  co2TrendReady = true;
  // Three completed 60-second declines build evidence across doses.
  // The next dose comes only 80 s after the previous one: no long wait needed.
  for (int i=0; i<3; ++i) {
    unsigned long start = 140000UL + i*80000UL;
    CO2i = 50000; co2LastPulseAt = start - 20000; measure(start);
    assert(lossStartAt == start);
    CO2i = 49990; measure(start + 6000);
    assert(lossFresh && lossCm3Hour == 11); // No fixed minimum duration.
    CO2i = 49980; measure(start + 12000);
    assert(lossFresh && !lossStable);
    CO2i = 49900; measure(start + 60000);
    assert(lossCm3Hour == 11 && lossFresh && !lossStable);
    finishCo2Loss();
    assert(lossWindows == i+1 && !lossFresh && lossStartAt == 0);
    // Injected rise is never included in the next decline.
    co2RatePpmMin = 1000; CO2i = 51000; measure(start + 62000);
    assert(lossCm3Hour == 11 && !lossFresh && lossWindows == i+1);
    co2RatePpmMin = -100;
  }
  CO2i = 50000; measure(400000);
  CO2i = 49950; measure(430000);
  assert(lossCm3Hour == 11 && lossStable && lossFresh);
  // Divergent new decline removes confidence rather than reusing old certainty.
  CO2i = 49700; measure(460000);
  assert(lossCm3Hour == 33 && !lossStable && lossWindows == 0);
  finishCo2Loss(); assert(lossWindows == 1 && !lossFresh);
  // A short interval with enough observed drop counts; duration is not the gate.
  CO2i = 50000; measure(480000);
  CO2i = 49940; measure(492000); finishCo2Loss();
  assert(lossWindows == 2 && lossStartAt == 0);
  // A tiny drop remains provisional regardless of duration.
  CO2i = 50000; measure(500000);
  CO2i = 49999; measure(560000); finishCo2Loss();
  assert(lossWindows == 2);
  // Even a two-second observed decline is measured with its actual duration.
  CO2i = 50000; measure(570000);
  CO2i = 49990; measure(572000);
  assert(lossCm3Hour == 33 && lossFresh);
  finishCo2Loss();
  // Invalid readings, rising concentration and unavailable trend retain history.
  updateCo2Loss(false); assert(lossCm3Hour >= 0 && !lossFresh && lossWindows == 0);
  co2RatePpmMin = 1000; measure(1200000);
  assert(lossCm3Hour >= 0 && !lossFresh);
  co2RatePpmMinReady = false; measure(1300000);
  assert(lossCm3Hour >= 0 && lossStartAt == 0);
  co2RatePpmMinReady = true; co2RatePpmMin = 0;
  CO2i = 50000; measure(1400000); measure(1430000);
  assert(lossCm3Hour == 0 && lossFresh);
  // Actual elapsed duration, not a fixed sampling interval, sets the rate.
  finishCo2Loss(); CO2i = 50000; co2RatePpmMin = -100; measure(1500000);
  CO2i = 49900; measure(1545000);
  assert(lossCm3Hour == 15);
  // An increase beyond the segment origin restarts the decline anchor.
  CO2i = 50100; measure(1547000);
  assert(!lossFresh && lossStartPpm == 50100 && lossStartAt == 1547000);

}

'''
with tempfile.TemporaryDirectory(prefix='incubadora-loss-') as folder:
    cpp = Path(folder) / 'loss.cpp'
    binary = Path(folder) / 'loss-test'
    cpp.write_text(harness)
    subprocess.run(['g++', '-std=c++11', '-Wall', '-Wextra', '-Werror', str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('Loss estimator and alert color regression checks passed.')
