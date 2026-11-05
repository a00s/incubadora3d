#!/usr/bin/env python3
"""Accelerated chamber scenarios executing extracted firmware C++ dose logic.
Plant is hypothetical: pure transport delay + 30 s mixing, constant leakage.
This checks algorithms, not the physical valve/sensor calibration.
"""
from pathlib import Path
import subprocess, tempfile, json, hashlib, argparse, re
parser=argparse.ArgumentParser()
parser.add_argument("--report",type=Path)
args=parser.parse_args()
source=(Path(__file__).resolve().parents[1]/'temperatura.ino').read_text()
def function(sig):
    a=source.index(sig); b=source.index('{',a); i=b+1; depth=1
    while depth:
        depth+=(source[i]=='{')-(source[i]=='}');i+=1
    return source[a:i]
a=source.index('      int32_t pulseMs;')
selection=source[a:source.index('      co2_before_pump = CO2i;',a)]
a=source.index('    bool responseWaitComplete =')
gates=source[a:source.index('    co2ProjectedPpm = CO2i;',a)]
harness=r'''
#include <cstdint>
#include <cstdio>
#include <cmath>
#include <vector>
#include <algorithm>
#include <random>
#define F(x) x
#define DELAY_MINIMO 20
#define MANUAL_CO2_PULSE_MS 5
#define DELAY_MAXIMO 1000
#define CO2_TARGET_PPM 50000L
#define CO2_CONTROL_MIN_PPM 49000L
#define CO2_TOLERANCE_PPM 1000L
#define CO2_MAX_RISING_RATE_PPM_PER_MIN 50L
#define CO2_RESPONSE_LAG_MIN_MS 90000UL
#define CO2_RESPONSE_LAG_MAX_MS 180000UL
#define CO2_DOSE_OBSERVATION_MS 300000UL
struct Silent { template<class T> void print(T){} } Serial;
int32_t CO2i,co2RatePpmMin,lastCo2PulseMs,max_co2_increase;
int32_t co2GainEstimatePpmPerMsX100;
const int32_t CO2_MIN_GAIN_ESTIMATE_X100=50;
uint8_t co2DoorMode,co2ResponseLagSeconds;
bool co2RatePpmMinReady,co2GainValidatedThisBoot,co2LastResponseWeak,co2DoseResponsePending;
unsigned long co2LastPulseAt,co2MaxRiseAt;
''' + function('bool co2ResponseWaitComplete(')+function('int32_t calcularDelayProporcional(')+r'''
int choose(unsigned long currentTime) {
  int32_t co2ProjectedPpm=CO2i;
  int32_t pulseLimit=std::min<int32_t>(1000,20+((50000-CO2i)>>4));
''' + selection + r'''
  return pulseMs;
}
bool ready(unsigned long currentTime,bool validCo2,int contador_pomp,bool co2TrendReady) {
''' + gates + r'''
 return doseResponseReady;
}
void run(const char* name,double gain0,double gain1,double loss,int lag,bool depletion,bool door,bool swap=false,double mixing=30,double noise=0,bool dropout=false,double valve_dead_ms=0) {
 CO2i=45000;co2RatePpmMin=0;lastCo2PulseMs=0;max_co2_increase=0;
 co2GainEstimatePpmPerMsX100=1200;co2DoorMode=0;co2ResponseLagSeconds=120;
 co2RatePpmMinReady=false;co2GainValidatedThisBoot=false;co2LastResponseWeak=false;co2DoseResponsePending=false;
 co2LastPulseAt=co2MaxRiseAt=0;
 double ppm=45000,pending=0,baseline=45000,peak=ppm,minLast=1e9,maxLast=0;
 bool rangeLocked=false;
 int doses=0,largest=0;unsigned long stable=0,previousDose=0;int shortest=999999;
 std::vector<double> delivery(15000,0),history;
 for(int t=0;t<28800;t+=2) {
   unsigned long now=(unsigned long)t*1000;
   if(door && t==14400) {ppm=35000;co2DoorMode=4;co2DoseResponsePending=false;}
   if(swap && t==14400) {lastCo2PulseMs=0;co2DoseResponsePending=false;}
   pending+=delivery[t/2];double rise=pending*(1-std::exp(-2.0/mixing));pending-=rise;
   ppm=std::max(400.0,ppm+rise-loss*2);
   bool valid=!(dropout && t>=18000 && t<18180);
   CO2i=std::lround(ppm+noise*std::sin(t*1.71));history.push_back(CO2i);
   if(!valid) {co2DoseResponsePending=false;lastCo2PulseMs=0;co2LastPulseAt=now;stable=0;}
   co2RatePpmMinReady=history.size()>15;
   co2RatePpmMin=co2RatePpmMinReady?std::lround((CO2i-history[history.size()-16])*2):0;
   if(co2RatePpmMinReady && co2RatePpmMin<=CO2_MAX_RISING_RATE_PPM_PER_MIN) {if(!stable)stable=now;}else stable=0;
   if(co2DoseResponsePending && CO2i-baseline>max_co2_increase) {max_co2_increase=CO2i-baseline;co2MaxRiseAt=now;}
   if(co2DoorMode>=3 && CO2i>=49000)co2DoorMode=0;
   if(CO2i>=60000)rangeLocked=true;
   if(t>=120 && !rangeLocked && CO2i<49500 && ready(now,valid,now-co2LastPulseAt>=60000?0:30,stable && now-stable>=30000)) {
     int pulse=choose(now);lastCo2PulseMs=pulse;baseline=CO2i;max_co2_increase=0;
     co2DoseResponsePending=true;co2LastPulseAt=co2MaxRiseAt=now;stable=0;
     if(co2DoorMode==4)co2DoorMode=3;
     double gain=depletion?gain0+(gain1-gain0)*t/28800.0:(t<14400?gain0:gain1);
     delivery[(t+lag)/2]+=std::max(0.0,pulse-valve_dead_ms)*gain;
     doses++;largest=std::max(largest,pulse);
     if(previousDose)shortest=std::min(shortest,int((now-previousDose)/1000));previousDose=now;
   }
   peak=std::max(peak,ppm);
   if(t>25200) {minLast=std::min(minLast,ppm);maxLast=std::max(maxLast,ppm);}
 }
 printf("{\"scenario\":\"%s\",\"peak_ppm\":%.0f,\"last_hour_min\":%.0f,\"last_hour_max\":%.0f,\"doses\":%d,\"max_pulse_ms\":%d,\"min_interval_s\":%d,\"gain_start\":%.2f,\"gain_end\":%.2f,\"loss_ppm_s\":%.3f,\"lag_s\":%d,\"mixing_s\":%.1f,\"noise_ppm\":%.1f,\"dropout\":%d,\"valve_dead_ms\":%.1f}\n",name,peak,minLast,maxLast,doses,largest,shortest,gain0,gain1,loss,lag,mixing,noise,dropout,valve_dead_ms);
}
int main(){
 run("fresh_high_flow",100,100,0.2,120,false,false);
 run("normal",12,12,0.2,60,false,false);
 run("depleting",12,2,0.2,120,true,false);
 run("delayed",40,40,0.2,180,false,false);
 run("door",12,12,0.2,120,false,true);
 run("cylinder_swap",2,100,0.2,120,false,false);
 run("paused_cylinder_swap",2,100,0.2,120,false,false,true);
 run("long_delay",40,40,0.2,240,false,false);
 run("large_leak",12,12,3,120,false,false);
 run("empty",0,0,0.2,120,false,false);
 run("door_cylinder_swap",2,100,0.2,120,false,true,true);
 std::mt19937 rng(20261105);
 auto unit=[&](){return double(rng())/rng.max();};
 for(int i=0;i<2000;i++) {
   int mode=i%5; double g0=0.5+unit()*149.5;
   double g1=mode==0?g0:(mode==1?g0*(0.05+0.9*unit()):0.5+149.5*unit());
   double loss=0.01+unit()*2.99;int lag=int(unit()*151)*2;
   double mixing=10+unit()*110;double noise=i%3==0?unit()*80:0;
   char name[80];snprintf(name,sizeof(name),"grid_%d_mode_%d",i,mode);
   run(name,g0,g1,loss,lag,mode==1,mode==2,mode==2||mode==3,mixing,noise,i%4==0,i%6==0?unit()*20:0);
 }
}
'''
# Keep compiled harness configuration tied to the real firmware macros.
for macro in ('CO2_TARGET_PPM','CO2_CONTROL_MIN_PPM','CO2_TOLERANCE_PPM',
              'CO2_MAX_RISING_RATE_PPM_PER_MIN','CO2_RESPONSE_LAG_MIN_MS',
              'CO2_RESPONSE_LAG_MAX_MS','CO2_DOSE_OBSERVATION_MS'):
    definition=re.search(r'^#define '+macro+r' (.+)$',source,re.M).group(1)
    harness=re.sub(r'^#define '+macro+r' .+$',lambda _: '#define '+macro+' '+definition,harness,flags=re.M)
with tempfile.TemporaryDirectory(prefix='co2-scenarios-') as folder:
    cpp=Path(folder)/'sim.cpp';exe=Path(folder)/'sim'
    cpp.write_text(harness)
    subprocess.run(['g++','-std=c++11','-O2',str(cpp),'-o',str(exe)],check=True)
    result=subprocess.run([str(exe)],check=True,capture_output=True,text=True)
    rows=[json.loads(line) for line in result.stdout.splitlines()]


# Bounds apply only to the defined hypothetical plant, not every possible valve.
for row in rows:
    assert row['min_interval_s']>=300, row
    if not row['scenario'].startswith('grid_') and row['scenario'] not in ('cylinder_swap','empty','large_leak'):
        assert row['peak_ppm']<=51000, row
        assert row['last_hour_min']>=49000, row
# Unknown pressure change cannot be anticipated without a pause/notification.
assert next(r for r in rows if r['scenario']=='cylinder_swap')['peak_ppm']>51000
assert next(r for r in rows if r['scenario']=='empty')['last_hour_max']<49000
assert next(r for r in rows if r['scenario']=='large_leak')['last_hour_min']<49000

grid=[r for r in rows if r['scenario'].startswith('grid_')]
summary={
    'firmware_sha256':hashlib.sha256(source.encode()).hexdigest(),
    'seed':20261105,'scenario_count':len(rows),'simulated_hours':len(rows)*8,
    'model':'Hypothetical pure transport lag + exponential mixing + constant leakage. No physical calibration. Actual C++ dose selection and gates extracted from firmware; sensor/trend/door plant modeled.',
    'parameter_ranges':{'gain_ppm_ms':[0.5,150],'loss_ppm_s':[0.01,3],'transport_delay_s':[0,300],'mixing_time_constant_s':[10,120],'noise_ppm':[0,80],'valve_dead_time_ms':[0,20]},
    'grid_modes':{'0':'constant flow','1':'gradual depletion','2':'door + notified cylinder swap','3':'notified swap','4':'unannounced swap'},
    'grid_results':{},'named_scenarios':rows[:11],
    'worst_notified_peaks':sorted([r for r in grid if not r['scenario'].endswith('mode_4')],key=lambda r:r['peak_ppm'],reverse=True)[:8],
    'worst_peaks':sorted(grid,key=lambda r:r['peak_ppm'],reverse=True)[:12],
}
for mode in range(5):
    group=[r for r in grid if r['scenario'].endswith('mode_'+str(mode))]
    summary['grid_results'][str(mode)]={'count':len(group),'peak_above_51000':sum(r['peak_ppm']>51000 for r in group),'last_hour_below_49000':sum(r['last_hour_min']<49000 for r in group),'last_hour_within_49000_51000':sum(r['last_hour_min']>=49000 and r['last_hour_max']<=51000 for r in group)}
assert all(r['max_pulse_ms']<=1000 for r in rows)
text=json.dumps(summary,indent=2)+'\n'
if args.report: args.report.write_text(text)
print(text)
