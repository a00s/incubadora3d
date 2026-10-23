#!/usr/bin/env python3
"""Exercise real door inference, mode transitions, pulse math and raw dose learning."""
from pathlib import Path
import re
import subprocess
import tempfile

source = (Path(__file__).resolve().parents[1] / 'temperatura.ino').read_text()
inference = source[source.index('void updateDoorState('):source.index('bool co2ResponseWaitComplete(')]
setter = source[source.index('bool setCo2Enabled(bool enabled)'):source.index('\nvoid setHeaterEnabled')]
pulse = source[source.index('int32_t calcularDelayProporcional('):source.index('//void wakeUpScreen')]
rise = re.search(r'int32_t increaseSincePump =.*?if \(increaseSincePump > max_co2_increase\) \{.*?\n        \}',source,re.S).group(0)
notice = source[source.index('void drawDoorNotice()'):source.index('void renderDisplay(')]
visible = re.search(r'if \((co2DoorMode.*?)\) drawDoorNotice\(\);',source).group(1)
harness = r'''
#include <stdint.h>
#include <assert.h>
#include <cmath>
#include <cstring>
#define F(x) x
#define incubadora_font_7x13 0
#define EEPROM_SAFETY_FAULT 30
#define EEPROM_CONTROL_STATE 29
#define CO2PUMP 7
#define HIGH 1
#define CO2_CONTROL_MIN_PPM 49000L
#define CO2_TOLERANCE_PPM 1000L
#define DELAY_MINIMO 20
struct Store { void update(int,int) {} } EEPROM;
void digitalWrite(int,int) {}
int finished = 0;
void finishCo2Loss() { finished++; }
bool co2RangeWrapLatched = false, co2DoseResponsePending = true;
bool lastCo2ReadingValid = true;
int safetyFault = 0, botao_co2_onoff = 1, botao_aquecedor_onoff = 1;
uint8_t co2DoorMode = 0, co2ResponseLagSeconds = 120;
int32_t CO2i = 50000, doorCo2Before = 0, co2RatePpmMin = 0;
float chamberTemperatureC = 37, doorTemperatureBefore = NAN;
int32_t co2_before_pump = 45000, max_co2_increase = 0;
unsigned long co2MaxRiseAt = 0;
'''+inference+setter+pulse+r'''
const char *label = nullptr;
struct Display {
  void setFont(int) {}
  void setPrintPos(int,int) {}
  void print(const char *text) { label = text; }
  void drawBox(int x,int y,int w,int h) {assert(x>=0 && y>=0 && x+w<=128 && y+h<=160);}
  void drawFrame(int x,int y,int w,int h) {drawBox(x,y,w,h);}
  void drawLine(int x,int y,int a,int b) {assert(x>=0 && x<128 && a>=0 && a<128 && y>=0 && y<160 && b>=0 && b<160);}
} ucg;
void setDisplayBackground() {}
void setDisplayForeground(int,int,int) {}
'''+notice+'''
void drawVisibleNotice() { if ('''+visible+''') drawDoorNotice(); }

void observeRise(unsigned long currentTime) { '''+rise+''' }
'''+r'''
int main() {
  co2DoorMode = 0; drawVisibleNotice(); assert(label == nullptr);
  co2DoorMode = 1; drawVisibleNotice(); assert(strcmp(label,"CO2 PAUSADO")==0);
  co2DoorMode = 2; drawVisibleNotice(); assert(strcmp(label,"PORTA ABERTA")==0);
  label = nullptr; co2DoorMode = 3; drawVisibleNotice(); assert(label == nullptr);
  co2DoorMode = 0;

  // Just turning off does not claim that the door is open.
  assert(setCo2Enabled(false));
  assert(co2DoorMode == 1 && doorCo2Before == 50000 && doorTemperatureBefore == 37);
  CO2i = 49500; updateDoorState(37,true);
  assert(co2DoorMode == 1);
  assert(setCo2Enabled(true)); assert(co2DoorMode == 0);
  // Off + CO2 loss + temperature fall => inferred open, on => recovery.
  CO2i = 50000; chamberTemperatureC = 37; setCo2Enabled(false);
  CO2i = 47000; updateDoorState(36.5,true); assert(co2DoorMode == 2);
  updateDoorState(36.5,false); assert(co2DoorMode == 2);
  setCo2Enabled(true); assert(co2DoorMode == 3 && !co2DoseResponsePending);
  updateDoorState(37,true); assert(co2DoorMode == 3);
  // Recovery is stronger but still bounded by pulseLimit.
  co2RatePpmMin = 0;
  assert(calcularDelayProporcional(47000,50000,10000,true,80) == 30);
  assert(calcularDelayProporcional(30000,50000,10000,true,80) == 80);
  assert(calcularDelayProporcional(47000,50000,10000,false,80) == 20);
  CO2i = 49000; updateDoorState(37,true); assert(co2DoorMode == 0);
  assert(calcularDelayProporcional(47000,50000,10000,true,80) == 20);
  // A strong drop confirms even if temperature has not responded yet.
  CO2i = 50000; chamberTemperatureC = 37; setCo2Enabled(false);
  CO2i = 47000; co2RatePpmMin = 0;
  updateDoorState(37,false); assert(co2DoorMode == 1);
  updateDoorState(37,true); assert(co2DoorMode == 2);
  // Smaller drop plus temperature fall also confirms, without a ready slope.
  setCo2Enabled(true); CO2i = 49000; chamberTemperatureC = 37;
  setCo2Enabled(false); CO2i = 48300; co2RatePpmMin = 0;
  updateDoorState(36.5,true); assert(co2DoorMode == 2);
  co2RangeWrapLatched = true;
  assert(!setCo2Enabled(true) && !botao_co2_onoff);
  co2RangeWrapLatched = false; setCo2Enabled(true);
  // Repeated ON commands must not restart recovery or drop its state.
  setCo2Enabled(true); assert(co2DoorMode == 3);
  // Re-enable can recognize the latest drop even before the next main-loop check.
  CO2i = 50000; chamberTemperatureC = 37; setCo2Enabled(false);
  CO2i = 47000; setCo2Enabled(true); assert(co2DoorMode == 3);
  // Door-opening fall must not invent dose gain or delay the observed peak.
  CO2i = 44000; observeRise(60000); assert(max_co2_increase == 0);
  CO2i = 45100; observeRise(70000);
  assert(max_co2_increase == 100 && co2MaxRiseAt == 70000);
  CO2i = 45050; observeRise(120000);
  assert(max_co2_increase == 100 && co2MaxRiseAt == 70000);
}
'''
with tempfile.TemporaryDirectory(prefix='incubadora-door-') as folder:
    cpp = Path(folder)/'door.cpp'; binary = Path(folder)/'door-test'
    cpp.write_text(harness)
    subprocess.run(['g++','-std=c++11','-Wall','-Wextra','-Werror',str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
print('Door inference, recovery and raw-dose learning checks passed.')
