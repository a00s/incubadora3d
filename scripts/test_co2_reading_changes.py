#!/usr/bin/env python3
"""Test the actual reading block: big deltas log, absolute high CO2 still locks."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root/'temperatura.ino').read_text()
start = source.index('    int32_t sensorPpm = mySensorCO2.getppm();')
end = source.index('    unsigned long currentTime = millis();', start)
reading = source[start:end]
code = r'''
#include <stdint.h>
#include <cassert>
#define F(x) x
#define CO2_SENSOR_LOCK_PPM 60000L
#define CO2_SENSOR_LOCK_MAGIC 0xA5
#define CO2_SENSOR_WARMUP_MS 120000UL
#define EEPROM_CO2_RANGE_LOCK 28
struct {int writes=0;uint8_t bytes[32]={};void update(int a,int v){bytes[a]=v;writes++;}} EEPROM;
struct {template<class T>void print(T){} template<class T>void println(T){}} Serial;
struct {int32_t value=0;bool rawLoggingEnabled=false;int32_t getppm(){return value;}} mySensorCO2;
bool co2RangeWrapLatched=false,co2RawReferenceReady=false,enabled=true;
int32_t CO2i=0,lastCo2RawPpm=0;
int disables=0;
unsigned long clockNow=200000;
unsigned long millis(){return clockNow;}
void setCo2Enabled(bool value){enabled=value;if(!value)disables++;}
void sample(int32_t value){mySensorCO2.value=value;clockNow+=2000;
''' + reading + r'''
}
int main(){
 sample(400);sample(20000);sample(59000);sample(400);
 assert(enabled&&!co2RangeWrapLatched&&EEPROM.writes==0&&disables==0);
 sample(60000);
 assert(!enabled&&co2RangeWrapLatched&&EEPROM.bytes[28]==0xA5&&disables==1);
 sample(785);assert(co2RangeWrapLatched&&!enabled&&disables==1);
 co2RangeWrapLatched=false;enabled=true;sample(-1);
 assert(CO2i==-1&&enabled); //Invalid readings are gated separately, not a fabricated delta lock.
}
'''
with tempfile.TemporaryDirectory(prefix='co2-reading-changes-') as folder:
    cpp=Path(folder)/'test.cpp';exe=Path(folder)/'test'
    cpp.write_text(code)
    subprocess.run(['g++','-std=c++11',str(cpp),'-o',str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print('Actual reading block: +/-15000+ changes do not disable;60000ppm lock retained.')
