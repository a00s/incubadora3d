#!/usr/bin/env python3
"""Exercise the actual firmware loss estimator with simulated sensor time/state."""
from pathlib import Path
import re
import subprocess
import tempfile

source = (Path(__file__).resolve().parents[1] / 'temperatura.ino').read_text()
constants = source[source.index('const uint16_t CO2_GAS_VOLUME_CM3'):source.index('// Variáveis globais para aprendizado adaptativo')]
function = source[source.index('void finishCo2Loss()'):source.index('\nvoid drawTextChanges')]
colors = source[source.index("void setDisplayBackground()"):source.index("void drawCo2Icon(")]
alert = re.search(r"bool alert = (.*);", source).group(1)
harness = r'''
#include <stdint.h>
#include <cmath>
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
  assert(lossCm3HourX10 == -1 && !lossFresh);
  co2RatePpmMin = 100; measure(120000);
  assert(lossStartAt == 0 && lossCm3HourX10 == -1);
  co2RatePpmMin = -100;
  // Three cycles of 100 ppm loss in 60 s: 11.1 cm3/h.
  for (int i=0; i<3; ++i) {
    unsigned long start = 140000UL + i*80000UL;
    CO2i = 50000; measure(start);
    CO2i = 49990; measure(start + 6000);
    assert(lossCm3HourX10 == 111 && lossFresh);
    CO2i = 49900; measure(start + 60000);
    assert(lossCm3HourX10 == 111);
    // Re-reading the same prefix must not count it twice.
    measure(start + 60000);
    assert(lossTimeTotal == i*60000UL);
    finishCo2Loss();
    assert(lossDropTotal == (i+1)*100 && lossTimeTotal == (i+1)*60000UL);
    co2RatePpmMin = 1000; CO2i = 52000; measure(start + 62000);
    assert(lossCm3HourX10 == 111 && !lossFresh);
    co2RatePpmMin = -100;
  }
  // A new flat sample must not overwrite the established mean with zero.
  CO2i = 50000; measure(400000); measure(402000);
  assert(lossCm3HourX10 == 110 && lossStable);
  // Different duration: 100 ppm in 120 s carries twice the weight of 60 s.
  CO2i = 49900; measure(520000);
  assert(lossCm3HourX10 == 89); // 400 ppm / 300 s -> 8.88 cm3/h.
  finishCo2Loss();
  assert(lossDropTotal == 400 && lossTimeTotal == 300000);
  // A 1 ppm decline over 2 s is retained too; no fixed minimum or signal filter.
  CO2i = 50000; measure(540000); CO2i = 49999; measure(542000);
  finishCo2Loss();
  assert(lossDropTotal == 401 && lossTimeTotal == 302000);
  int32_t held = lossCm3HourX10;
  updateCo2Loss(false);
  assert(lossCm3HourX10 == held && !lossFresh);
  co2RatePpmMin = 1000; measure(1200000);
  assert(lossCm3HourX10 == held && lossDropTotal == 401);
  co2RatePpmMinReady = false; measure(1300000);
  assert(lossCm3HourX10 == held && lossStartAt == 0);
  // Many later consistent cycles damp a short new fluctuation.
  co2RatePpmMinReady = true; co2RatePpmMin = -100;
  for (int i=0; i<100; ++i) {
    unsigned long start = 1400000UL + i*80000UL;
    CO2i = 50000; measure(start); CO2i = 49900; measure(start+60000);
    finishCo2Loss();
  }
  held = lossCm3HourX10;
  CO2i = 50000; measure(10000000); measure(10002000);
  assert(lossCm3HourX10 >= held-1 && lossCm3HourX10 > 0);
  // Sub-unit loss remains visible: 1 ppm per minute = 0.111 cm3/h.
  finishCo2Loss(); lossDropTotal = lossTimeTotal = 0; lossWindows = 0;
  CO2i = 50000; measure(11000000); CO2i = 49999; measure(11060000);
  assert(lossCm3HourX10 == 1); // Display 0.1, not 0.
  co2RatePpmMin = 100; measure(11062000);
  assert(lossDropTotal == 1 && lossTimeTotal == 60000 && !lossFresh);

}

'''
with tempfile.TemporaryDirectory(prefix='incubadora-loss-') as folder:
    cpp = Path(folder) / 'loss.cpp'
    binary = Path(folder) / 'loss-test'
    cpp.write_text(harness)
    subprocess.run(['g++', '-std=c++11', '-Wall', '-Wextra', '-Werror', str(cpp), '-o', str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
print('Loss estimator and alert color regression checks passed.')
