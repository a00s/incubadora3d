#!/usr/bin/env python3
"""Exercise actual thermal control: duty, recovery, trend braking and safety."""
from pathlib import Path
import re
import subprocess
import tempfile
s = (Path(__file__).resolve().parents[1] / 'temperatura.ino').read_text()
defines = '\n'.join(line for line in s.splitlines() if line.startswith('#define HEATER') or line.startswith('#define EEPROM_SAFETY_FAULT') or line.startswith('#define CHAMBER_TEMPERATURE_OFFSET_C'))
globals_ = s[s.index('unsigned long heaterPidLastUpdateAt'):s.index('bool heaterTrendReady')]+ 'bool heaterTrendReady = false;'
fn = s[s.index('void controlHeater(float'):s.index('void finishCo2ClickSequence()')]
harness = r'''
#include <cmath>
#include <cstdint>
#include <cassert>
using std::isnan;
#define LOW 0
#define HIGH 1
#define F(x) x
int pin=HIGH;
int digitalRead(int) {return pin;}
void digitalWrite(int,int v) {pin=v;}
bool botao_aquecedor_onoff=true,botao_co2_onoff=false;
uint8_t co2DoorMode=0;
int safetyFault=0;
struct {void update(int,int) {}} EEPROM;
struct {void println(const char*) {}} Serial;
void setHeaterEnabled(bool b) {botao_aquecedor_onoff=b;pin=HIGH;}
void setCo2Enabled(bool b) {botao_co2_onoff=b;}
'''+defines+'\n'+globals_+'\n'+fn+r'''
int main() {
  controlHeater(36.2f,4000);
  assert(pin==LOW && heaterPidDemandMs==10000);
  assert(heaterPidIntegralMs==10000); // measured startup maintenance, no cold-error charge
  heaterPidIntegralMs=12000;
  controlHeater(36.2f,5000);
  assert(heaterPidDemandMs==12000);
  assert(heaterPidIntegralMs==12000); // far from target, preserve learned maintenance
  controlHeater(36.6f,6000);
  assert(heaterPidDemandMs<=17000 && heaterCurrentPulseMs<=17000);
  heaterTrendReady=true;heaterTempRateCPerMin=0;
  controlHeater(35.0f,6001);
  assert(heaterPidDemandMs==17000);
  controlHeater(37.1f,6002);
  assert(pin==HIGH && heaterPidDemandMs==0);
  controlHeater(37.2f,6003);
  assert(pin==HIGH && botao_aquecedor_onoff); // regulation pauses output, not the enabled control
  controlHeater(36.2f,8000);
  assert(pin==HIGH); // mandatory 3 s off
  controlHeater(36.2f,9001);
  assert(pin==HIGH); // 3 s off is insufficient before the 20 s pulse period
  controlHeater(36.2f,24000);
  assert(pin==LOW);
  controlHeater(NAN,24001);
  assert(pin==HIGH && heaterPidDemandMs==0);
  controlHeater(39.0f,24002);
  assert(pin==HIGH && !botao_aquecedor_onoff && !botao_co2_onoff && safetyFault==2);
  controlHeater(36.0f,90000);
  assert(pin==HIGH && !botao_aquecedor_onoff); // cooling cannot clear the latched trip

  // Actual GPIO duty over six periods at target: 6 s demand means 30%, not 67%.
  pin=HIGH;botao_aquecedor_onoff=true;safetyFault=0;
  heaterPidInitialized=false;heaterLastTransitionAt=90000;heaterPulseStartedAt=0;
  controlHeater(37.0f,100000);
  assert(pin==HIGH && heaterPidDemandMs==0); // no heating at target before trend is known
  heaterTrendReady=true;heaterTempRateCPerMin=0;
  heaterPidIntegralMs=6000;
  unsigned long onMs=0,lastStart=0;int starts=0;
  for (unsigned long now=100020;now<220020;now+=20) {
    int before=pin;controlHeater(37.0f,now);
    if (before==HIGH && pin==LOW) {
      if (lastStart) assert(now-lastStart==20000);
      lastStart=now;starts++;
    }
    if (pin==LOW) onMs+=20;
  }
  assert(starts==6 && onMs==36000);

  // A measured rise must brake before reaching target, without bypassing caps.
  heaterTrendReady=true;heaterTempRateCPerMin=0.3f;
  heaterTrendReferenceAt=220000;heaterPidIntegralMs=6000;pin=HIGH;
  controlHeater(36.8f,220020);
  assert(pin==HIGH && heaterPidDemandMs==0); // forecast crosses target before measurement
  heaterTempRateCPerMin=-0.3f;
  controlHeater(36.8f,220040);
  assert(heaterPidDemandMs<=17000);
  // Maintenance can use more than 60% without switching temperature bands.
  heaterTempRateCPerMin=0;heaterPidIntegralMs=15000;heaterFilteredTempC=37.0f;
  controlHeater(37.0f,220060);
  assert(heaterPidIntegralMs==15000 && heaterPidDemandMs==15000);

  // Door pause keeps learned maintenance; resume does not reintegrate the cold air.
  co2DoorMode=2;botao_aquecedor_onoff=false;heaterPidIntegralMs=11000;
  controlHeater(36.8f,230000);
  assert(pin==HIGH && heaterPidIntegralMs==11000);
  co2DoorMode=4;botao_aquecedor_onoff=true;
  controlHeater(36.8f,260000);
  assert(heaterPidIntegralMs==11000 && heaterPidDemandMs>0);
  heaterTrendReady=true;heaterTempRateCPerMin=-0.05f;
  controlHeater(37.05f,260020);
  assert(heaterPidDemandMs>0); // PI maintenance survives a reading just above target.
  controlHeater(37.1f,260040);
  assert(pin==HIGH && heaterPidDemandMs==0); // independent hard cut remains.
  // Learn a stationary loss even far from target, but freeze during rapid recovery.
  heaterTrendReady=true;heaterTempRateCPerMin=0;heaterTrendReferenceAt=300000;
  heaterPidLastUpdateAt=300000;heaterPidIntegralMs=9000;heaterPidDemandMs=0;
  controlHeater(36.3f,301000);
  assert(heaterPidIntegralMs>9000);
  heaterPidIntegralMs=9000;heaterTempRateCPerMin=0.12f;
  controlHeater(36.7f,301500);
  assert(heaterPidIntegralMs>9000); // one DS18B20 step cannot freeze loss learning
  heaterPidIntegralMs=9000;heaterTempRateCPerMin=0.2f;
  controlHeater(36.3f,302000);
  assert(heaterPidIntegralMs==9000);
  heaterTempRateCPerMin=0.14f;heaterPidIntegralMs=11000;
  controlHeater(36.9f,303000);
  assert(pin==HIGH && heaterPidDemandMs==0 && heaterPidIntegralMs==11000);
  heaterTempRateCPerMin=0.04f;
  controlHeater(36.9f,304000);
  assert(heaterPidDemandMs>0 && botao_aquecedor_onoff); // automatic return after forecast clears
  // A real warming trend must replace a stale cooling trend at the next window.
  pin=HIGH;botao_aquecedor_onoff=true;safetyFault=0;co2DoorMode=0;
  heaterPidInitialized=true;heaterTrendReady=true;
  heaterPidLastUpdateAt=400000;heaterTrendReferenceAt=400000;
  heaterFilteredTempC=36.6f;heaterTrendReferenceC=36.6f;heaterTempRateCPerMin=-0.3f;
  for (unsigned long now=400020;now<=431000;now+=20)
    controlHeater(36.6f+(now-400000)*0.000005f,now);
  assert(heaterTempRateCPerMin>0.15f); // no second EMA can retain the old negative sign
  controlHeater(37.0f,431020);
  assert(pin==HIGH && heaterPidDemandMs==0 && botao_aquecedor_onoff);

}
'''
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'test.cpp';p.write_text(harness)
    subprocess.run(['g++','-std=c++11',str(p),'-o',str(Path(d)/'test')],check=True)
    subprocess.run([str(Path(d)/'test')],check=True)
print('Heater duty, recovery, trend braking, relay pause and safety checks passed.')
