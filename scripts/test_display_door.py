#!/usr/bin/env python3
"""Check every text write from the actual display renderer while the door is open."""
from pathlib import Path
import subprocess
import tempfile

source=(Path(__file__).resolve().parents[1]/'temperatura.ino').read_text()
def function(name):
    start=source.index(name); opening=source.index('{',start); depth=1; end=opening+1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[start:end]
names=['void setDisplayBackground(', 'void setDisplayForeground(', 'void updateActivityIcons(',
       'void drawHealthIndicator(', 'void drawDisplayFrame(', 'void formatTenths(',
       'void formatPpmPerMinute(', 'void drawTextChanges(', 'void drawDoorNotice(', 'void renderDisplay(']
functions=[function(n) for n in names]
prototypes='\n'.join(f[:f.index('{')].strip()+';' for f in functions)
globals_=source[source.index('bool displayCacheValid'):source.index('unsigned long lastValidCo2Time')]
harness=r'''
#include <stdint.h>
#include <cmath>
#include <cstring>
#include <cstdio>
#include <string>
#include <vector>
#include <utility>
#include <assert.h>
using std::isnan;
#define F(x) x
#define PSTR(x) x
#define strcpy_P strcpy
#define strcat_P strcat
#define incubadora_font_7x13 1
#define incubadora_font_inr16 2
#define DISPLAY_FAULT 0
#define DISPLAY_WAIT 1
#define DISPLAY_READY 2
#define CO2_CONTROL_MIN_PPM 49000L
#define CO2_CONTROL_MAX_PPM 51000L
#define CO2_TARGET_PPM 50000L
#define CO2_DISPLAY_NEAR_TOLERANCE_PPM 5000L
#define TEMPERATURE_GOOD_MIN 36.9
#define TEMPERATURE_GOOD_MAX 37.1
#define TEMPERATURE_DISPLAY_NEAR_MIN 36.5
#define TEMPERATURE_DISPLAY_NEAR_MAX 37.5
#define CO2PUMP 7
#define HEATER 3
#define LOW 0
char *ltoa(long v,char *out,int base) {assert(base==10);std::sprintf(out,"%ld",v);return out;}
unsigned long millis() {return 100000;}
int digitalRead(int) {return 1;}
int iconDraws=0;
void drawCo2Icon(uint8_t,uint8_t,bool,bool,uint8_t) {iconDraws++;}
void drawHeaterIcon(uint8_t,uint8_t,bool,bool,uint8_t) {iconDraws++;}
void drawFanIcon(uint8_t,uint8_t,bool,bool,uint8_t) {iconDraws++;}
struct Display {
 int baseline=0;
 std::vector<std::pair<int,std::string>> writes;
 int getWidth() {return 128;} int getHeight() {return 160;}
 int getStrWidth(const char *s) {return strlen(s)*7;}
 void clearScreen() {} void setColor(int,int,int,int) {} void setFont(int) {}
 void setPrintPos(int,int y) {baseline=y;}
 void print(const char *s) {writes.push_back({baseline,s});}
 void drawBox(int x,int y,int w,int h) {assert(x>=0 && y>=0 && x+w<=128 && y+h<=160);}
 void drawFrame(int x,int y,int w,int h) {drawBox(x,y,w,h);}
 void drawLine(int x,int y,int a,int b) {assert(x>=0 && x<128 && a>=0 && a<128 && y>=0 && y<160 && b>=0 && b<160);}
 void drawHLine(int x,int y,int w) {assert(x>=0 && y>=0 && x+w<=128 && y<160);}
 void reset() {writes.clear();iconDraws=0;}
 bool has(const char *s) {for(auto &w:writes)if(w.second==s)return true;return false;}
 void assertOpen() {
  for(auto &w:writes) if(w.first>80) assert(w.first==97 && w.second=="PORTA ABERTA");
  assert(!has("ppm/min") && !has("cm3/h") && iconDraws==0);
 }
} ucg;
bool co2RangeWrapLatched=false, botao_co2_onoff=true, botao_aquecedor_onoff=true, ventilador_status=true;
bool co2RatePpmMinReady=true, lossStable=false, lossFresh=false;
int32_t CO2i=50000, co2RatePpmMin=-100, lossCm3HourX10=240, eeprom_contador_int=12;
uint8_t co2DoorMode=0;
int8_t displayHealthState=DISPLAY_WAIT;
'''+globals_+'\n'+prototypes+'\n'+'\n'.join(functions)+r'''
int main() {
 renderDisplay(37,30,true);
 assert(ucg.has("ppm/min") && ucg.has("cm3/h"));
 ucg.reset();renderDisplay(37.01,30,true);assert(ucg.has("37.01 C"));
 ucg.reset();renderDisplay(37.08,30,true);assert(ucg.has("37.08 C"));
 ucg.reset();renderDisplay(-37.08,30,true);assert(ucg.has("-37.08 C"));
 ucg.reset();renderDisplay(NAN,30,false);assert(ucg.has("--.-- C"));
 co2DoorMode=2;CO2i=44000;
 ucg.reset();renderDisplay(36,30,true);ucg.assertOpen();assert(ucg.has("PORTA ABERTA"));
 assert(ucg.has("44000") && ucg.has("36.00 C"));
 // Repeated live changes must never paint rate/loss text, even transiently.
 CO2i=43000;co2RatePpmMin=-9000;lossCm3HourX10=990;
 ucg.reset();renderDisplay(36.1,30.1,true);ucg.assertOpen();
 assert(ucg.has("43000") && ucg.has("36.10 C"));
 // Alert-color transitions and direct frame reconstruction also stay isolated.
 CO2i=48000;ucg.reset();renderDisplay(36.8,30,true);ucg.assertOpen();
 ucg.reset();drawDisplayFrame();ucg.assertOpen();assert(ucg.has("PORTA ABERTA"));
 ucg.reset();updateActivityIcons();ucg.assertOpen();
 CO2i=-1;ucg.reset();renderDisplay(NAN,30,false);ucg.assertOpen();
 CO2i=48000;
 // Closing restores lower fields and invalidates their old cached values.
 co2DoorMode=4;ucg.reset();renderDisplay(36.8,30,true);
 assert(ucg.has("RECUPERANDO") && ucg.has("ppm/min") && ucg.has("cm3/h"));
 assert(!ucg.has("PORTA ABERTA"));
 co2DoorMode=2;ucg.reset();renderDisplay(36.8,30,true);ucg.assertOpen();
}
'''
with tempfile.TemporaryDirectory(prefix='incubadora-display-') as folder:
    cpp=Path(folder)/'display.cpp'; binary=Path(folder)/'display-test';cpp.write_text(harness)
    subprocess.run(['g++','-std=c++11','-Wall','-Wextra','-Werror',str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
print('Open-door display isolation and live upper-field checks passed.')
