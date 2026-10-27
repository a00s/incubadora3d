#!/usr/bin/env python3
"""Compile real button/door/control functions with GPIO/EEPROM/clock test doubles."""
from pathlib import Path
import re
import subprocess
import tempfile

source = (Path(__file__).resolve().parents[1]/'temperatura.ino').read_text()
def function(signature):
    start=source.index(signature); brace=source.index('{',start); depth=1; end=brace+1
    while depth:
        depth += (source[end]=='{')-(source[end]=='}'); end+=1
    return source[start:end]
names=[
    'void updateDoorState(', 'void saveControlState(', 'bool setCo2Enabled(',
    'void setHeaterEnabled(', 'bool manualCo2Pulse(', 'void clearCo2RangeLock(',
    'void finishHeaterClickSequence(', 'void handleHeaterButtonClick(',
    'void finishCo2ClickSequence(', 'void handleCo2ButtonClick(',
    'void toggleDoorMode(', 'void dispatchHeaterClick(', 'void serviceHeaterButton(',
    'void finishCo2ClickSequenceIfExpired(', 'int32_t calcularDelayProporcional(',
]
functions=[function(n) for n in names]
prototypes='\n'.join(re.sub(r' = MANUAL_CO2_PULSE_MS','',f[:f.index('{')].strip())+';' for f in functions)
notice=function('void drawDoorNotice(')
visible='co2DoorMode == 2'
restore=function('    if (controlState <= 31)')
rise=re.search(r'int32_t increaseSincePump =.*?if \(increaseSincePump > max_co2_increase\) \{.*?\n        \}',source,re.S).group(0)
harness=r'''
#include <stdint.h>
#include <assert.h>
#include <cstring>
#define F(x) x
#define incubadora_font_7x13 0
#define EEPROM_SAFETY_FAULT 30
#define EEPROM_CONTROL_STATE 29
#define EEPROM_CO2_RANGE_LOCK 28
#define CO2PUMP 7
#define HEATER 3
#define HIGH 1
#define LOW 0
#define CO2_CONTROL_MIN_PPM 49000L
#define CO2_CONTROL_MAX_PPM 51000L
#define CO2_TOLERANCE_PPM 1000L
#define DELAY_MINIMO 20
#define MANUAL_CO2_PULSE_MS 5
#define MANUAL_CO2_MAX_PULSE_MS 20
#define POMP_WAITING_TIME 30
struct Store {
  uint8_t bytes[1024] = {};
  void update(int at,int value) {bytes[at]=value;}
  uint8_t read(int at) {return bytes[at];}
} EEPROM;
struct Logger {template<class T> void print(T) {} template<class T> void println(T) {}} Serial;
struct Sensor {bool rawLoggingEnabled=false;} mySensorCO2;
unsigned long clockMs=0, heaterLastTransitionAt=0, co2LastPulseAt=0, co2MaxRiseAt=0;
unsigned long lastValidCo2Time=0, co2StableSince=0, co2AnimationUntil=0;
unsigned long heaterPressedAt=0, co2ClickSequenceStart=0, heaterClickSequenceStart=0;
uint8_t co2ClickCount=0, heaterClickCount=0, co2DoorMode=0;
uint8_t doorResumeControls=0;
bool heaterPressPending=false, heaterButtonStable=false;
uint8_t co2ResponseLagSeconds=120;
bool botao_co2_onoff=true, botao_aquecedor_onoff=true, co2ModeAtClickSequence=false;
bool co2RangeWrapLatched=false, co2DoseResponsePending=true, displayCacheValid=true;
bool co2BaselineReady=false, co2TrendReady=false, co2ReferenceReady=false;
bool co2RawReferenceReady=false, lastCo2ReadingValid=true, co2RatePpmMinReady=true, lossFresh=false;
int safetyFault=0, contador_pomp=0, finished=0, gasPulses=0, pulseDuration=0;
int pins[10]={HIGH,HIGH,HIGH,HIGH,HIGH,HIGH,HIGH,HIGH,HIGH,HIGH};
int32_t CO2i=47000, co2RatePpmMin=0, co2RateAtPulsePpmMin=0, co2_before_pump=45000;
int32_t last_co2i=0, max_co2_increase=0;
uint16_t lastCo2PulseMs=0, heaterPidDemandMs=0;
float heaterPidIntegralMs=0, maxRate=0;
unsigned long millis() {return clockMs;}
void delay(int duration) {pulseDuration=duration;}
void digitalWrite(int pin,int state) {pins[pin]=state; if(pin==CO2PUMP && state==LOW)gasPulses++;}
int digitalRead(int pin) {return pins[pin];}
void finishCo2Loss() {finished++;lossFresh=false;}
'''+prototypes+'\n'+'\n'.join(functions)+r'''
void yellow(unsigned long now) {clockMs=now;finishCo2ClickSequenceIfExpired(now);handleCo2ButtonClick(now);}
void redDown(unsigned long now) {clockMs=now;heaterButtonStable=true;serviceHeaterButton(true,false,now);}
void redPoll(unsigned long now,bool both=false) {clockMs=now;finishCo2ClickSequenceIfExpired(now);serviceHeaterButton(false,both,now);}
void redUp(unsigned long now) {clockMs=now;heaterButtonStable=false;serviceHeaterButton(false,false,now);}
void tapRed(unsigned long now) {redDown(now);redUp(now+100);}
void holdRed(unsigned long now) {
  uint8_t before=co2DoorMode;
  redDown(now);redPoll(now+1999);assert(co2DoorMode==before);
  redPoll(now+2000);redUp(now+2200);
}
void tick(unsigned long now) {clockMs=now;finishCo2ClickSequenceIfExpired(now);}
void restoreControls() {uint8_t controlState=EEPROM.read(EEPROM_CONTROL_STATE);
'''+restore+'''
}
void observeRise(unsigned long currentTime) {'''+rise+'''}
'''+r'''
const char *label=nullptr;
int bodyLeft=-1,bodyRight=-1,openRight=0,hingeX=-1;
struct Display {
 void setFont(int) {} void setPrintPos(int,int) {} void print(const char *s) {label=s;}
 void drawBox(int x,int y,int w,int h) {assert(x>=0 && y>=0 && x+w<=128 && y+h<=160);}
 void drawFrame(int x,int y,int w,int h) {drawBox(x,y,w,h);if(bodyLeft<0){bodyLeft=x;bodyRight=x+w-1;}}
 void drawLine(int x,int y,int a,int b) {if(hingeX<0)hingeX=x;if(x>openRight)openRight=x;if(a>openRight)openRight=a;assert(x>=0 && x<128 && a>=0 && a<128 && y>=0 && y<160 && b>=0 && b<160);}
} ucg;
void setDisplayBackground() {} void setDisplayForeground(int,int,int) {}
'''+notice+'''
void drawVisibleNotice() {if ('''+visible+''') drawDoorNotice();}
'''+r'''
int main() {
  // Short red acts only on release, preserving heating control.
  redDown(100);assert(botao_aquecedor_onoff && heaterPressPending);
  redUp(300);assert(!botao_aquecedor_onoff && co2DoorMode==0);
  tapRed(500);assert(botao_aquecedor_onoff);
  // A hold fires at 2 seconds once, never as a short click as well.
  pins[HEATER]=LOW;
  redDown(1000);redPoll(2999);
  assert(co2DoorMode==0 && botao_co2_onoff && botao_aquecedor_onoff);
  redPoll(3000);
  assert(co2DoorMode==2 && !botao_co2_onoff && !botao_aquecedor_onoff);
  assert(pins[HEATER]==HIGH && pins[CO2PUMP]==HIGH && EEPROM.read(29)==28);
  assert(co2ClickCount==0 && heaterClickCount==0 && !co2DoseResponsePending);
  redPoll(8000);assert(co2DoorMode==2); // Still held: must not toggle again.
  redUp(8100);assert(co2DoorMode==2 && !botao_aquecedor_onoff);
  drawVisibleNotice();assert(strcmp(label,"PORTA ABERTA")==0);
  assert(openRight>bodyRight && hingeX==bodyRight);
  // Independent enable commands and manual pulses cannot bypass the pause.
  assert(!manualCo2Pulse("test",5) && gasPulses==0);
  assert(!setCo2Enabled(true));tapRed(8300);
  assert(!botao_co2_onoff && !botao_aquecedor_onoff);
  yellow(8500);yellow(8700);yellow(8900);tick(11500);
  assert(gasPulses==0 && co2DoorMode==2);
  co2DoorMode=0;botao_co2_onoff=botao_aquecedor_onoff=true;
  restoreControls();assert(co2DoorMode==2 && !botao_co2_onoff && !botao_aquecedor_onoff);
  holdRed(12000);
  assert(co2DoorMode==4 && botao_co2_onoff && botao_aquecedor_onoff && EEPROM.read(29)==3);
  tick(15000);assert(co2DoorMode==4 && gasPulses==0);
  updateDoorState(true);assert(co2DoorMode==4);
  CO2i=49000;updateDoorState(true);assert(co2DoorMode==0);
  label=nullptr;drawVisibleNotice();assert(label==nullptr);
  co2DoorMode=4;CO2i=47000;
  assert(manualCo2Pulse("test",5) && co2DoorMode==3);co2DoorMode=0;
  // Original 3/4/5 yellow pulses are unchanged; fifth still emits immediately.
  for(int clicks=3;clicks<=5;clicks++) {
    unsigned long at=17000+(clicks-3)*5000;int before=gasPulses;
    for(int i=0;i<clicks;i++)yellow(at+i*200);
    assert(gasPulses==before+(clicks==5?1:0));tick(at+3000);
    assert(gasPulses==before+1 && pulseDuration==(clicks==3?5:(clicks==4?10:20)));
    assert(co2DoorMode==0 && botao_aquecedor_onoff);
  }
  yellow(33000);tick(36000);assert(!botao_co2_onoff && co2DoorMode==0);
  tapRed(37000);assert(!botao_aquecedor_onoff);
  yellow(38000);tick(41000);assert(botao_co2_onoff);
  // Old yellow/red/yellow pattern now only invokes normal short-click commands.
  yellow(42000);tapRed(42200);yellow(42400);tick(45000);assert(co2DoorMode==0);
  // Releasing after the threshold still counts as long if a poll was missed.
  heaterPidIntegralMs=11000;
  redDown(46000);redUp(48000);assert(co2DoorMode==2);
  assert(heaterPidIntegralMs==11000);
  holdRed(49000);assert(co2DoorMode==4 && botao_co2_onoff && botao_aquecedor_onoff);
  assert(heaterPidIntegralMs==11000);
  // Simultaneous-button reset gesture cancels a pending hold, not a door toggle.
  redDown(52000);redPoll(53000,true);redPoll(56000);redUp(56100);
  assert(co2DoorMode==4);
  holdRed(58000);safetyFault=2;holdRed(62000);
  assert(co2DoorMode==0 && safetyFault==2 && !botao_co2_onoff && !botao_aquecedor_onoff);
  assert(!(EEPROM.read(29)&4));safetyFault=0;
  botao_co2_onoff=botao_aquecedor_onoff=true;
  holdRed(66000);co2RangeWrapLatched=true;holdRed(70000);
  assert(co2RangeWrapLatched && !botao_co2_onoff && botao_aquecedor_onoff);
  tapRed(74000);tapRed(74200);tapRed(74400);
  assert(!co2RangeWrapLatched && !botao_co2_onoff);
  // Every pre-door combination is restored independently, including after reboot.
  for (int reboot=0;reboot<2;reboot++) for (uint8_t mask=0;mask<4;mask++) {
    co2DoorMode=0;botao_co2_onoff=mask&1;botao_aquecedor_onoff=(mask>>1)&1;
    toggleDoorMode();
    assert(co2DoorMode==2 && !botao_co2_onoff && !botao_aquecedor_onoff);
    assert(EEPROM.read(29)==(4|(mask<<3)));
    if (reboot) {doorResumeControls=0;co2DoorMode=0;restoreControls();}
    toggleDoorMode();
    assert(botao_co2_onoff==bool(mask&1) && botao_aquecedor_onoff==bool(mask&2));
    assert(co2DoorMode==((mask&1)?4:0));
    assert(EEPROM.read(29)==mask);
  }
  // Old firmware stored no resume requests: keep both off on legacy paused boot.
  EEPROM.update(29,4);restoreControls();toggleDoorMode();
  assert(!botao_co2_onoff && !botao_aquecedor_onoff && co2DoorMode==0);
  // Recovery dose math stays bounded; learning ignores fictitious door compensation.
  co2DoorMode=4;co2RatePpmMin=0;
  assert(calcularDelayProporcional(47000,50000,5000,true,80)==60);
  assert(calcularDelayProporcional(47000,50000,20000,true,80)==20);
  co2DoorMode=3;
  assert(calcularDelayProporcional(47000,50000,10000,true,80)==30);
  assert(calcularDelayProporcional(30000,50000,10000,true,80)==80);
  co2DoorMode=0;assert(calcularDelayProporcional(47000,50000,10000,true,80)==20);
  max_co2_increase=0;co2_before_pump=45000;CO2i=44000;observeRise(80000);
  assert(max_co2_increase==0);
  CO2i=45100;observeRise(81000);CO2i=45050;observeRise(82000);
  assert(max_co2_increase==100 && co2MaxRiseAt==81000);
}
'''
with tempfile.TemporaryDirectory(prefix='incubadora-door-') as folder:
    cpp=Path(folder)/'door.cpp'; binary=Path(folder)/'door-test'; cpp.write_text(harness)
    subprocess.run(['g++','-std=c++11','-Wall','-Wextra','-Werror',str(cpp),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
print('Long-press door, short-click isolation, persistence and legacy-button checks passed.')
