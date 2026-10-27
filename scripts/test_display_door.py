#!/usr/bin/env python3
"""Check every text write from the actual display renderer while the door is open."""
from pathlib import Path
import subprocess
import re
import tempfile

source=(Path(__file__).resolve().parents[1]/'temperatura.ino').read_text()
# Verify the real font advances used to keep one changed cell off its neighbors.
fonts=(Path(__file__).resolve().parents[1]/'firmware/incubadora/display_font.h').read_text()
for font,advance in [('incubadora_font_7x13',7),('incubadora_font_inr16',13)]:
    body=re.search(font+r'\[\d+\].*?= \{(.*?)\};',fonts,re.S).group(1)
    data=list(map(int,re.findall(r'\d+',body)));pos=21
    while data[pos+1]:
        bits=int.from_bytes(bytes(data[pos+2:pos+6]),'little')
        dx=((bits>>sum(data[4:8]))&((1<<data[8])-1))-(1<<(data[8]-1))
        assert dx==advance,(font,chr(data[pos]),dx)
        pos+=data[pos+1]

def function(name):
    start=source.index(name); opening=source.index('{',start); depth=1; end=opening+1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[start:end]
names=['void setDisplayBackground(', 'void setDisplayForeground(', 'void updateActivityIcons(',
       'void serviceActivityIconAnimation(', 'void drawHealthIndicator(', 'void drawDisplayFrame(', 'void formatTenths(',
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
#include <tuple>
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
unsigned long fakeMillis=100000;
unsigned long millis() {return fakeMillis;}
float chamberTemperatureC=37.0f;bool lastCo2ReadingValid=true;
struct {float readTemperature() {return 30.0f;}} dhtint;
int digitalRead(int) {return 1;}
int iconDraws=0;
void drawCo2Icon(uint8_t,uint8_t,bool,bool,uint8_t) {iconDraws++;}
void drawHeaterIcon(uint8_t,uint8_t,bool,bool,uint8_t) {iconDraws++;}
void drawFanIcon(uint8_t,uint8_t,bool,bool,uint8_t) {iconDraws++;}
const int layout[5][4]={{5,40,13,18},{5,74,7,12},{66,74,7,12},{73,101,7,13},{73,120,7,12}};
struct Display {
 int baseline=0;
 std::string fields[5]={std::string(14,' '),std::string(14,' '),std::string(14,' '),std::string(14,' '),std::string(14,' ')};
 std::vector<std::tuple<int,int,int,int>> boxes;
 std::vector<std::tuple<int,int,char>> glyphs;
 std::vector<std::pair<int,std::string>> writes;
 int getWidth() {return 128;} int getHeight() {return 160;}
 int getStrWidth(const char *s) {return strlen(s)*7;}
 void clearScreen() {for(auto &f:fields)f=std::string(14,' ');}
 void setColor(int,int,int,int) {} void setFont(int) {}
 void setPrintPos(int,int y) {baseline=y;}
 void print(const char *s) {writes.push_back({baseline,s});}
 void drawBox(int x,int y,int w,int h) {
  assert(x>=0 && y>=0 && x+w<=128 && y+h<=160);boxes.push_back({x,y,w,h});
  for(int f=0;f<5;f++) {
   int top=layout[f][1]-(f==0?17:10);
   if(y<=top && y+h>top)for(int i=0;i<14;i++) {
    int origin=layout[f][0]+i*layout[f][2];
    if(origin>=x && origin<x+w)fields[f][i]=' ';
   }
  }
 }
 void drawGlyph(int x,int y,int dir,char c) {
  assert(dir==0 && x>=0 && x<128 && y>=0 && y<160);
  glyphs.push_back({x,y,c});writes.push_back({y,std::string(1,c)});
  for(int f=0;f<5;f++)if(y==layout[f][1] && x>=layout[f][0] && (x-layout[f][0])%layout[f][2]==0)
   fields[f][(x-layout[f][0])/layout[f][2]]=c;
 }
 void drawFrame(int x,int y,int w,int h) {drawBox(x,y,w,h);}
 void drawLine(int x,int y,int a,int b) {assert(x>=0 && x<128 && a>=0 && a<128 && y>=0 && y<160 && b>=0 && b<160);}
 void drawHLine(int x,int y,int w) {assert(x>=0 && y>=0 && x+w<=128 && y<160);}
 void reset() {writes.clear();boxes.clear();glyphs.clear();iconDraws=0;}
 bool has(const char *s) {
  for(auto &w:writes)if(w.second==s)return true;
  for(auto &f:fields)if(f.substr(0,strlen(s))==s)return true;
  return false;
 }
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
 assert(ucg.boxes.size()==1 && ucg.boxes[0]==std::make_tuple(33,64,7,12));
 assert(ucg.glyphs.size()==2 && std::get<2>(ucg.glyphs[0])=='8');
 ucg.reset();renderDisplay(37.08,30,true);assert(ucg.glyphs.empty() && ucg.boxes.empty());
 renderDisplay(36.99,30,true);ucg.reset();renderDisplay(37.0,30,true);
 assert(ucg.has("37.00 C") && ucg.boxes.size()==3 && ucg.glyphs.size()==6);
 ucg.reset();renderDisplay(-37.08,30,true);assert(ucg.has("-37.08 C"));
 ucg.reset();renderDisplay(NAN,30,false);assert(ucg.has("--.-- C"));
 // Refresh a changed chamber reading inside the input-service cycle, without a CO2 poll.
 co2DoorMode=0;renderDisplay(37.0,30,true);ucg.reset();
 activityIconFrame=0;lastActivityIconFrameAt=fakeMillis;chamberTemperatureC=37.08f;
 for(int i=0;i<3;i++){fakeMillis+=160;serviceActivityIconAnimation();}
 assert(ucg.has("37.00 C") && ucg.glyphs.empty());
 fakeMillis+=160;serviceActivityIconAnimation();assert(ucg.has("37.08 C"));
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
 // Every numeric field preserves unchanged glyphs and erases only changed cells.
 co2DoorMode=0;CO2i=50000;co2RatePpmMin=-100;lossCm3HourX10=240;
 renderDisplay(37.0,30,true);ucg.reset();CO2i=50001;renderDisplay(37.0,30,true);
 assert(ucg.has("50001") && ucg.boxes.size()==1 && ucg.glyphs.size()==1);
 assert(ucg.boxes[0]==std::make_tuple(57,23,13,18));
 ucg.reset();renderDisplay(37.0,30.1,true);
 assert(ucg.has("30.1 C") && ucg.boxes.size()==1 && ucg.glyphs.size()==1);
 assert(ucg.boxes[0]==std::make_tuple(87,64,7,12));
 ucg.reset();co2RatePpmMin=-101;renderDisplay(37.0,30.1,true);
 assert(ucg.has("-101") && ucg.boxes.size()==1 && ucg.glyphs.size()==1);
 assert(ucg.boxes[0]==std::make_tuple(94,91,7,13));
 ucg.reset();lossCm3HourX10=241;renderDisplay(37.0,30.1,true);
 assert(ucg.has("24.1*") && ucg.boxes.size()==1 && ucg.glyphs.size()==1);
 assert(ucg.boxes[0]==std::make_tuple(94,110,7,12));
 ucg.reset();renderDisplay(37.0,30.1,true);assert(ucg.boxes.empty() && ucg.glyphs.empty());
 // Recoloring an unchanged numeric value paints it without a blank flash.
 lossStable=true;ucg.reset();renderDisplay(37.0,30.1,true);
 assert(ucg.boxes.empty() && !ucg.glyphs.empty());
 // Shrinking a numeric string erases the old suffix.
 co2RatePpmMin=-9;ucg.reset();renderDisplay(37.0,30.1,true);
 assert(ucg.fields[3].substr(0,4)=="-9  ");
}

'''
with tempfile.TemporaryDirectory(prefix='incubadora-display-') as folder:
    cpp=Path(folder)/'display.cpp'; binary=Path(folder)/'display-test';cpp.write_text(harness)
    subprocess.run(['g++','-std=c++11','-Wall','-Wextra','-Werror',str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
print('Numeric partial redraw, font metrics, refresh cadence and door isolation checks passed.')
