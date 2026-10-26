#!/usr/bin/env python3
"""Exercise actual thermal control: recovery, near-target cap and safety."""
from pathlib import Path
import re
import subprocess
import tempfile
s = (Path(__file__).resolve().parents[1] / 'temperatura.ino').read_text()
defines = '\n'.join(line for line in s.splitlines() if line.startswith('#define HEATER') or line.startswith('#define EEPROM_SAFETY_FAULT'))
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
int safetyFault=0;
struct {void update(int,int) {}} EEPROM;
struct {void println(const char*) {}} Serial;
void setHeaterEnabled(bool b) {botao_aquecedor_onoff=b;pin=HIGH;}
void setCo2Enabled(bool b) {botao_co2_onoff=b;}
'''+defines+'\n'+globals_+'\n'+fn+r'''
int main() {
  assert(std::abs((36.0f-1.375f+1.575f)-36.2f)<0.0001f);
  controlHeater(36.2f,4000);
  assert(pin==LOW && heaterPidDemandMs>12000 && heaterPidDemandMs<=30000);
  heaterPidIntegralMs=12000;
  controlHeater(36.2f,5000);
  assert(heaterPidDemandMs>12000 && heaterPidDemandMs<=30000);
  controlHeater(36.6f,6000);
  assert(heaterPidDemandMs<=12000 && heaterCurrentPulseMs<=12000);
  controlHeater(37.1f,6001);
  assert(pin==HIGH && heaterPidDemandMs==0);
  controlHeater(36.2f,8000);
  assert(pin==HIGH); // mandatory 3 s off
  controlHeater(36.2f,9001);
  assert(pin==LOW);
  controlHeater(NAN,9002);
  assert(pin==HIGH && heaterPidDemandMs==0);
  controlHeater(39.0f,9003);
  assert(pin==HIGH && !botao_aquecedor_onoff && !botao_co2_onoff && safetyFault==2);
}
'''
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'test.cpp';p.write_text(harness)
    subprocess.run(['g++','-std=c++11',str(p),'-o',str(Path(d)/'test')],check=True)
    subprocess.run([str(Path(d)/'test')],check=True)
print('Heater recovery, near-target cap, relay pause and safety checks passed.')
