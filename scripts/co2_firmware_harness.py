"""Extract the actual Uno admission and timing rules for host tests/simulations."""
from pathlib import Path
import re
ROOT = Path(__file__).resolve().parents[1]

def harness():
    source = (ROOT/'temperatura.ino').read_text()
    def function(signature):
        start = source.index(signature)
        end = source.index('{', start)+1
        depth = 1
        while depth:
            depth += (source[end] == '{')-(source[end] == '}')
            end += 1
        return source[start:end].replace('unsigned long', 'uint32_t')
    start = source.index('    bool responseWaitComplete =')
    gates = source[start:source.index('    int32_t delayProporcional', start)]
    admission = re.search(r'if \((validCo2 && currentTime >= CO2_SENSOR_WARMUP_MS.*?)\) \{\s*int32_t pulseMs\b', source, re.S).group(1)
    macros = '\n'.join(re.findall(r'^#define (?:CO2_|MANUAL_CO2_)[^\n]+', source, re.M))
    # MANUAL_CO2_PULSE_MS is a const int in the sketch.
    macros += '\n#define MANUAL_CO2_PULSE_MS 5\n'
    return '#include "'+str(ROOT/'firmware/incubadora/co2_dosing.h')+'"\n'+r'''
#include <cassert>
#include <cmath>
#include <cstdint>
#include <algorithm>
Co2DoseModel co2DoseModel;
uint32_t co2LastPulseAt=0,co2RecentRiseAt=0,actualNow=0;
int32_t CO2i=48000,lastCo2PulseMs=0;
float co2Rate=0;
bool co2RatePpmMinReady=true,botao_co2_onoff=true;
uint32_t millis(){return actualNow;}
'''+macros+'\n'+function('void updateCo2RecentRise(')+'\n'+function('bool co2ResponseWaitComplete(')+r'''
bool firmwareReady(uint32_t currentTime,bool validCo2=true){
'''+gates+r'''
 return doseResponseReady;
}
uint16_t firmwarePulse(uint32_t currentTime,bool validCo2=true,bool botao_co2_onoff=true,
                       uint8_t co2ClickCount=0,bool heaterPressPending=false){
 actualNow=currentTime;
 bool doseResponseReady=firmwareReady(currentTime,validCo2);
 int32_t delayProporcional=validCo2?co2DoseModel.pulse(currentTime):0;
 return ('''+admission+r''')?delayProporcional:0;
}
void recordAutomatic(uint16_t ms,uint32_t now){
 co2DoseModel.record(ms,now);lastCo2PulseMs=ms;co2LastPulseAt=now+ms;
}
void resetFirmware(){
 co2DoseModel=Co2DoseModel();co2LastPulseAt=co2RecentRiseAt=actualNow=0;
 lastCo2PulseMs=0;co2Rate=0;co2RatePpmMinReady=true;botao_co2_onoff=true;
}
'''
