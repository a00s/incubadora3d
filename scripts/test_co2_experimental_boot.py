#!/usr/bin/env python3
"""Verify experimental boot stays unarmed for every saved control combination."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'temperatura.ino').read_text()
a=s.index('    co2RangeWrapLatched = EEPROM.read');b=s.index('    EEPROM.get(EEPROM_CONTADOR',a);boot=s[a:b]
a=s.index('void saveControlState()');b=s.index('\n}',a)+2;save=s[a:b]
code='#include <cassert>\n#include <stdint.h>\n#define CO2_EXPERIMENTAL_START_DISABLED 1\n#define EEPROM_CO2_RANGE_LOCK 28\n#define EEPROM_CONTROL_STATE 29\n#define EEPROM_SAFETY_FAULT 30\n#define CO2_SENSOR_LOCK_MAGIC 0xA5\nstruct {uint8_t bytes[32]={};int read(int a){return bytes[a];}void update(int a,int b){bytes[a]=b;}} EEPROM;\nbool co2RangeWrapLatched=false;uint8_t safetyFault=0,botao_co2_onoff=0,botao_aquecedor_onoff=0,doorResumeControls=0,co2DoorMode=0;\nstruct {bool rawLoggingEnabled=false;} mySensorCO2;\n'+save+'\nvoid restore(){'+boot+'}\nint main(){for(int mask=0;mask<32;mask++){\n EEPROM.bytes[29]=mask;co2DoorMode=0;doorResumeControls=0;restore();\n assert(!botao_co2_onoff && !(EEPROM.bytes[29]&1) && !(doorResumeControls&1));\n assert(botao_aquecedor_onoff==((mask&4)?0:((mask>>1)&1)));\n}}\n'
with tempfile.TemporaryDirectory(prefix='co2-boot-off-') as d:
 p=Path(d);(p/'test.cpp').write_text(code)
 subprocess.run(['g++','-std=c++11',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('CO2 stays OFF for32 saved boot states; heating and door pause preserved.')
