#!/usr/bin/env python3
"""Check actual EEPROM setters and boot restore without connecting to the Uno."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'temperatura.ino').read_text()

def function(signature):
    start = source.index(signature)
    end = source.index('{', start) + 1
    depth = 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    return source[start:end]

start = source.index('    co2RangeWrapLatched = EEPROM.read')
end = source.index('    EEPROM.get(EEPROM_CONTADOR', start)
boot = source[start:end]
code = '#include "' + str(ROOT / 'firmware/incubadora/co2_dosing.h') + '"\n' + r'''
#include <cassert>
#define EEPROM_CO2_RANGE_LOCK 28
#define EEPROM_CONTROL_STATE 29
#define EEPROM_SAFETY_FAULT 30
#define CO2_SENSOR_LOCK_MAGIC 0xA5
#define HEATER 6
#define CO2PUMP 7
#define HIGH 1
#define LOW 0
#define HEATER_PID_INITIAL_INTEGRAL_MS 10000
struct {
 uint8_t bytes[32]={}; int writes=0;
 int read(int address){return bytes[address];}
 void update(int address,int value){bytes[address]=value;writes++;}
} EEPROM;
bool co2RangeWrapLatched=false;
uint8_t safetyFault=0,botao_co2_onoff=0,botao_aquecedor_onoff=0;
uint8_t doorResumeControls=0,co2DoorMode=0;
uint16_t lastCo2PulseMs=0,heaterPidDemandMs=0;
unsigned long heaterLastTransitionAt=0;
float heaterPidIntegralMs=10000;
struct {bool rawLoggingEnabled=false;} mySensorCO2;
Co2DoseModel co2DoseModel;
int pins[8]={1,1,1,1,1,1,1,1};
int digitalRead(int pin){return pins[pin];}
void digitalWrite(int pin,int value){pins[pin]=value;}
unsigned long millis(){return 100000;}
''' + function('void saveControlState()') + '\n' + function('bool setCo2Enabled(') + '\n' + function('void setHeaterEnabled(') + '\nvoid restore(){' + boot + r'''}
int main(){
 // Both actual setters persist each of the four ON/OFF combinations.
 for(int co2=0;co2<2;co2++)for(int heat=0;heat<2;heat++){
  co2DoorMode=0;co2RangeWrapLatched=false;safetyFault=0;
  assert(setCo2Enabled(co2));setHeaterEnabled(heat);
  const uint8_t saved=co2|(heat<<1);
  assert(EEPROM.bytes[29]==saved);
  for(int powerCuts=0;powerCuts<5;powerCuts++){
   botao_co2_onoff=!co2;botao_aquecedor_onoff=!heat;
   const int writes=EEPROM.writes;
   restore();
   assert(botao_co2_onoff==co2&&botao_aquecedor_onoff==heat);
   assert(EEPROM.bytes[29]==saved&&EEPROM.writes==writes);
  }
 }
 // Existing door pause/resume data must also survive, without boot overwriting it.
 for(int mask=0;mask<32;mask++){
  EEPROM.bytes[29]=mask;co2DoorMode=0;doorResumeControls=0;
  const int writes=EEPROM.writes;restore();
  assert(EEPROM.bytes[29]==mask&&EEPROM.writes==writes);
  assert(botao_co2_onoff==((mask&4)?0:(mask&1)));
  assert(botao_aquecedor_onoff==((mask&4)?0:((mask>>1)&1)));
  if(mask&4)assert(doorResumeControls==((mask>>3)&3));
 }
 // The existing persistent range lock retains priority; restoring does not clear it.
 EEPROM.bytes[29]=3;EEPROM.bytes[28]=0xA5;co2DoorMode=0;
 restore();assert(!botao_co2_onoff&&botao_aquecedor_onoff);
 assert(EEPROM.bytes[29]==3&&EEPROM.bytes[28]==0xA5);
}
'''
with tempfile.TemporaryDirectory(prefix='incubadora-persistence-') as folder:
    cpp=Path(folder)/'test.cpp';exe=Path(folder)/'test'
    cpp.write_text(code)
    subprocess.run(['g++','-std=c++11',str(cpp),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print('Actual EEPROM setters and boot: four ON/OFF states, repeated power cycles, door data and existing lock passed.')
