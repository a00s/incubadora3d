#!/usr/bin/env python3
"""Accelerate chamber scenarios using the actual firmware C++ dosing functions.
The chamber, delay, mixing, leakage and noise are hypothetical plants.
Initial nonlinear response samples come from the physical experiment; other
valve responses and perturbations test extrapolation beyond that calibration.
"""
from pathlib import Path
import subprocess, tempfile, json, hashlib, argparse, re
parser=argparse.ArgumentParser()
parser.add_argument("--report",type=Path)
parser.add_argument("--seed",type=int,default=20261105)
parser.add_argument("--source",type=Path)
parser.add_argument("--header",type=Path)
parser.add_argument("--cold-grid",action="store_true")
parser.add_argument("--explore",action="store_true")
parser.add_argument("--transport-max-s",type=int,default=300,help="Hypothetical transport bound, not a measured sensor delay.")
parser.add_argument("--require-safe-grid",action="store_true")
parser.add_argument("--two-chambers",action="store_true",help="Separate mixer and main chamber; exploratory, not calibrated.")
parser.add_argument("--mixer-fraction",type=float,default=0.1,help="Assumed fraction of total gas volume in mixer.")
parser.add_argument("--sensor-node",choices=("mixer","chamber"),default="mixer")
args=parser.parse_args()
if not 0 < args.mixer_fraction < 1: parser.error("mixer fraction must be between zero and one")
if not 0 <= args.transport_max_s <= 300: parser.error("transport maximum must be 0..300 seconds")
source=(args.source or (Path(__file__).resolve().parents[1]/'temperatura.ino')).read_text()
def function(sig):
    a=source.index(sig); b=source.index('{',a); i=b+1; depth=1
    while depth:
        depth+=(source[i]=='{')-(source[i]=='}');i+=1
    return source[a:i]
a=source.index('      int32_t pulseMs;')
selection=source[a:source.index('      co2_before_pump = CO2i;',a)]
a=source.index('    bool responseWaitComplete =')
gates=source[a:source.index('    int32_t pulseLimit',a)]
harness=r'''
#include <cstdint>
#include <cstdio>
#include <cstdlib>
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
#define CO2_STABLE_TIME_MS 30000UL
#define CO2_DOSE_OBSERVATION_MS 300000UL
struct Silent { template<class T> void print(T){} } Serial;
int32_t CO2i,co2RatePpmMin,lastCo2PulseMs,max_co2_increase,co2ProjectedPpm;
int32_t co2GainEstimatePpmPerMsX100;
const int32_t CO2_MIN_GAIN_ESTIMATE_X100=50;
uint8_t co2DoorMode,co2ResponseLagSeconds;
bool co2RatePpmMinReady,co2GainValidatedThisBoot,co2LastResponseWeak,co2DoseResponsePending;
bool co2DoseSettled=false;uint16_t co2NoisePpm=10;uint16_t co2ResponseWaitSeconds=600;int32_t co2DoseLossPpmMin=0;
unsigned long co2LastPulseAt,co2MaxRiseAt;
int32_t co2RateHistoryPpm[16];uint8_t co2RateHistoryCount=0,co2RateHistoryNext=0;
unsigned long co2RateHistoryTime[16],co2StableSince=0;bool co2TrendReady=false;
''' + (function('int32_t co2PulseGrowthMs(') if 'int32_t co2PulseGrowthMs(' in source else '')+function('bool co2ResponseWaitComplete(')+(function('void measureCo2Noise(') if 'void measureCo2Noise(' in source else '')+(function('void learnCo2Response(') if 'void learnCo2Response(' in source else '')+(function('int32_t calcularDelayProporcional(') if 'int32_t calcularDelayProporcional(' in source else '')+r'''
int choose(unsigned long currentTime) {
  int32_t co2ProjectedPpm=CO2i;
  PULSE_LIMIT
''' + selection + r'''
  return pulseMs;
}
bool ready(unsigned long currentTime,bool validCo2,int contador_pomp,bool co2TrendReady) {
''' + gates + r'''
 return doseResponseReady;
}
// Exact two well-mixed tanks in series: pure CO2 enters the mixer,
// displaces the same gas volume into the chamber, then out of the system.
// q is injected gas volume / total chamber volume, not a time delay.
void fillTanks(double &mixer,double &chamber,double q) {
 const double f=MIXER_FRACTION, pure=1000000.0;
 double e1=std::exp(-q/f),e2=std::exp(-q/(1-f));
 double upstream=mixer-pure;
 chamber=pure+(chamber-pure)*e2+upstream*(std::abs(2*f-1)<1e-9?q/(1-f)*e2:f/(2*f-1)*(e1-e2));
 mixer=pure+upstream*e1;
}
void exchangeTanks(double &mixer,double &chamber,double seconds,double tau) {
 const double f=MIXER_FRACTION;
 double mean=f*mixer+(1-f)*chamber;
 double difference=(mixer-chamber)*std::exp(-seconds/tau);
 mixer=mean+(1-f)*difference;chamber=mean-f*difference;
}
void checkTankPhysics() {
 double a=50000,b=2000,mean=MIXER_FRACTION*a+(1-MIXER_FRACTION)*b;
 exchangeTanks(a,b,20,30);
 if(std::abs(MIXER_FRACTION*a+(1-MIXER_FRACTION)*b-mean)>1e-6 || a<b)std::abort();
 a=b=400;fillTanks(a,b,0);if(std::abs(a-400)>1e-6||std::abs(b-400)>1e-6)std::abort();
 fillTanks(a,b,0.01);if(!(400<b&&b<a&&a<1000000))std::abort();
 fillTanks(a,b,100);if(std::abs(a-1000000)>1e-6||std::abs(b-1000000)>1e-6)std::abort();
}
void run(const char* name,double gain0,double gain1,double loss,int lag,bool depletion,bool door,bool swap=false,double mixing=30,double noise=0,bool dropout=false,double valve_dead_ms=0,double initial_ppm=45000,int shape=0) {
 MODEL_RESET
 co2NoisePpm=10;co2DoseSettled=false;
 CO2i=initial_ppm;co2RatePpmMin=0;lastCo2PulseMs=0;max_co2_increase=0;
 co2GainEstimatePpmPerMsX100=1200;co2DoorMode=0;co2ResponseLagSeconds=120;
 co2RatePpmMinReady=false;co2GainValidatedThisBoot=false;co2LastResponseWeak=false;co2DoseResponsePending=false;
 co2LastPulseAt=co2MaxRiseAt=0;co2RateHistoryCount=co2RateHistoryNext=0;co2StableSince=0;co2TrendReady=false;
 double injected=0,mixed=0,mixerPpm=initial_ppm,sensorPeak=initial_ppm;
 double ppm=initial_ppm,pending=0,baseline=initial_ppm,peak=ppm,minLast=1e9,maxLast=0;
 int firstBand=-1,doorBand=-1;
 bool rangeLocked=false;
 int doses=0,largest=0;unsigned long stable=0,previousDose=0;int shortest=999999;
 std::vector<double> delivery(15000,0),history;
 for(int t=0;t<28800;t+=2) {
   unsigned long now=(unsigned long)t*1000;
   bool doorOpen=door && t>=14400 && t<14430;
   if(door && t==14400) {ppm=35000;co2DoorMode=2;co2DoseResponsePending=false;co2DoseSettled=false;}
   if(door && t==14430) {co2DoorMode=4;co2DoseSettled=false;lastCo2PulseMs=0;MODEL_RESET}
   if(swap && t==14400) {lastCo2PulseMs=0;co2DoseResponsePending=false;co2DoseSettled=false;MODEL_RESET}
   pending+=delivery[t/2];double rise=pending*(1-std::exp(-2.0/mixing));pending-=rise;mixed+=rise;
   if(TWO_CHAMBERS) {
     fillTanks(mixerPpm,ppm,rise/1000000.0);
     exchangeTanks(mixerPpm,ppm,2,mixing);
     mixerPpm=std::max(400.0,mixerPpm-loss*2);
     ppm=std::max(400.0,ppm-loss*2);
   } else ppm=std::max(400.0,ppm+rise-loss*2);
   bool valid=!(dropout && t>=18000 && t<18180);
   double sensorPpm=TWO_CHAMBERS && SENSOR_IN_MIXER?mixerPpm:ppm;
   sensorPeak=std::max(sensorPeak,sensorPpm);
   CO2i=std::lround(sensorPpm+noise*std::sin(t*1.71));history.push_back(CO2i);
   if(!valid) {INVALID_MODEL co2DoseResponsePending=false;co2DoseSettled=false;lastCo2PulseMs=0;co2LastPulseAt=now;stable=0;}
   updateRollingTrend(now,valid);stable=co2StableSince;
   if(co2DoseResponsePending && CO2i-baseline>max_co2_increase) {max_co2_increase=CO2i-baseline;co2MaxRiseAt=now;}
   if(co2DoorMode>=3 && CO2i>=49000)co2DoorMode=0;
   if(CO2i>=60000)rangeLocked=true;
   if(valid) {
     if(!RANGE_NOISE && !co2DoseResponsePending && co2DoorMode==0 && history.size()>1) {
       int delta=CO2i-history[history.size()-2];
       co2NoisePpm=co2NoisePpm-co2NoisePpm/4+(delta>0?delta/2:0);
       if(co2NoisePpm<10)co2NoisePpm=10;
     }
     MODEL_LEARN
   }
   if(t>=120 && !doorOpen && !rangeLocked && CO2i<49500 && ready(now,valid,now-co2LastPulseAt>=60000?0:30,stable && now-stable>=30000)) {
     int pulse=choose(now);lastCo2PulseMs=pulse;baseline=CO2i;max_co2_increase=0;
     co2DoseResponsePending=true;co2DoseSettled=false;co2LastPulseAt=co2MaxRiseAt=now;stable=co2StableSince=0;co2TrendReady=false;
     if(co2DoorMode==4)co2DoorMode=3;
     double gain=depletion?gain0+(gain1-gain0)*t/28800.0:(t<14400?gain0:gain1);
     if(shape==2 && t>=3600 && t<5400)gain=0; // Valve contact outage, then repair.
     double added=std::max(0.0,pulse-valve_dead_ms)*gain;
     if(shape) {
       const double tx[]={0,60,80,160,207,320,1000};
       const double ry[]={0,0,82,1659,12228,20726,70000};
       double x=std::max(0.0,pulse-valve_dead_ms);int j=1;
       while(j<6 && tx[j]<x)++j;
       added=(ry[j-1]+(x-tx[j-1])*(ry[j]-ry[j-1])/(tx[j]-tx[j-1]))*gain/60;
     }
     // Delivery is consumed at the beginning of a step. Never schedule into
     // the already-consumed current bucket (zero delay used to lose all gas).
     delivery[t/2+std::max(1,(lag+1)/2)]+=added;injected+=added;
     doses++;largest=std::max(largest,pulse);
     if(previousDose)shortest=std::min(shortest,int((now-previousDose)/1000));previousDose=now;
   }
   if(ppm>=49000 && ppm<=51000) {if(firstBand<0)firstBand=t; if(door && t>=14430 && doorBand<0)doorBand=t-14430;}
   peak=std::max(peak,ppm);
   if(t>25200) {minLast=std::min(minLast,ppm);maxLast=std::max(maxLast,ppm);}
 }
 double future=0;for(size_t i=28800/2;i<delivery.size();++i)future+=delivery[i];
 if(std::abs(injected-mixed-pending-future)>1e-5*std::max(1.0,injected)) {fprintf(stderr,"Gas conservation failed: %s\n",name);std::abort();}
 printf("{\"scenario\":\"%s\",\"peak_ppm\":%.0f,\"sensor_peak_ppm\":%.0f,\"last_hour_min\":%.0f,\"last_hour_max\":%.0f,\"doses\":%d,\"max_pulse_ms\":%d,\"min_interval_s\":%d,\"gain_start\":%.2f,\"gain_end\":%.2f,\"loss_ppm_s\":%.3f,\"lag_s\":%d,\"mixing_s\":%.1f,\"noise_ppm\":%.1f,\"dropout\":%d,\"valve_dead_ms\":%.1f,\"shape\":%d,\"initial_ppm\":%.0f,\"first_band_s\":%d,\"door_recovery_s\":%d}\n",name,peak,sensorPeak,minLast,maxLast,doses,largest,shortest,gain0,gain1,loss,lag,mixing,noise,dropout,valve_dead_ms,shape,initial_ppm,firstBand,doorBand);
}
int main(){
 checkTankPhysics();
 run("zero_lag_normal",12,12,0.2,0,false,false);
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
 run("start_2000_normal",12,12,0.2,60,false,false,false,30,0,false,0,2000);
 run("start_2000_dead_valve",12,12,0.2,60,false,false,false,30,0,false,20,2000);
 run("start_2000_low_pressure",2,2,0.2,120,false,false,false,30,0,false,20,2000);
 run("start_2000_high_pressure",100,100,0.2,120,false,false,false,30,0,false,0,2000);
 run("start_2000_dead_valve_60ms",12,12,0.2,60,false,false,false,30,0,false,60,2000);
 run("observed_nonlinear_start",60,60,0.05,4,false,false,false,15,2,false,0,2000,1);
 run("observed_nonlinear_door",60,60,0.05,4,false,true,false,15,2,false,0,45000,1);
 run("observed_nonlinear_swap",60,120,0.05,4,false,true,true,15,2,false,0,2000,1);
 run("observed_contact_repair",60,60,0.5,4,false,false,false,15,2,false,0,2000,2);
 std::mt19937 rng(SIM_SEED);
 auto unit=[&](){return double(rng())/rng.max();};
 for(int i=0;i<2000;i++) {
   int mode=i%5; double g0=0.5+unit()*149.5;
   double g1=mode==0?g0:(mode==1?g0*(0.05+0.9*unit()):0.5+149.5*unit());
   double loss=0.01+unit()*2.99;int lag=int(unit()*(TRANSPORT_MAX_S/2+1))*2;
   double mixing=10+unit()*110;double noise=i%3==0?unit()*80:0;
   char name[80];snprintf(name,sizeof(name),"grid_%d_mode_%d",i,mode);
   run(name,g0,g1,loss,lag,mode==1,mode==2,mode==2||mode==3,mixing,noise,i%4==0,i%6==0?unit()*80:0,GRID_INITIAL_PPM,i%2);
 }
}
'''
trend_start=source.index('      co2RateHistoryPpm[co2RateHistoryNext] = CO2i;')
trend_end=source.index('      if (lastMinuteTime ==',trend_start)
rolling_trend='void updateRollingTrend(unsigned long currentTime,bool valid) {\nif(valid) {\n'+source[trend_start:trend_end]+'} else {co2RateHistoryCount=co2RateHistoryNext=0;co2RatePpmMinReady=false;co2TrendReady=false;co2StableSince=0;}\n}\n'
harness=harness.replace('void run(const char* name',rolling_trend+'void run(const char* name',1)
history_size=re.search(r'const uint8_t CO2_RATE_HISTORY_SIZE = (\d+);',source).group(1)
harness=harness.replace('#define CO2_TOLERANCE_PPM', '#define CO2_RATE_HISTORY_SIZE '+history_size+'\n#define CO2_TOLERANCE_PPM',1)
curve_model='co2_dosing.h' in source
harness=harness.replace('SIM_SEED',str(args.seed)).replace('TRANSPORT_MAX_S',str(args.transport_max_s))
harness=harness.replace('RANGE_NOISE','true' if 'void measureCo2Noise(' in source else 'false')
harness=harness.replace('PULSE_LIMIT', re.search(r'    int32_t pulseLimit =[^;]+;',source).group(0) if curve_model else 'int32_t pulseLimit=std::min<int32_t>(1000,20+((50000-CO2i)>>4));')
harness=harness.replace('MODEL_LEARN', 'learnCo2Response(now);' if 'void learnCo2Response(' in source else '')
initial_wait=int(re.search(r'uint16_t co2ResponseWaitSeconds = (\d+);',source).group(1)) if curve_model else 600
harness=harness.replace('MODEL_RESET', 'co2DoseModel.reset();co2ResponseWaitSeconds='+str(initial_wait)+';' if curve_model else '')
harness=harness.replace('INVALID_MODEL', 'co2DoseModel.fresh=true;co2ResponseWaitSeconds=600;' if curve_model else '')
if curve_model:
    header=args.header or (Path(__file__).resolve().parents[1]/'firmware/incubadora/co2_dosing.h')
    harness='#include '+json.dumps(str(header))+'\nCo2DoseModel co2DoseModel;\n'+harness
harness=harness.replace('TWO_CHAMBERS',str(args.two_chambers).lower()).replace('MIXER_FRACTION',repr(args.mixer_fraction)).replace('SENSOR_IN_MIXER',str(args.sensor_node=='mixer').lower())
harness=harness.replace('GRID_INITIAL_PPM', '2000' if args.cold_grid else '45000')
# Keep compiled harness configuration tied to the real firmware macros.
for macro in ('CO2_TARGET_PPM','CO2_CONTROL_MIN_PPM','CO2_TOLERANCE_PPM',
              'CO2_STABLE_TIME_MS','CO2_MAX_RISING_RATE_PPM_PER_MIN','CO2_RESPONSE_LAG_MIN_MS',
              'CO2_RESPONSE_LAG_MAX_MS','CO2_DOSE_OBSERVATION_MS'):
    definition=re.search(r'^#define '+macro+r' (.+)$',source,re.M).group(1)
    harness=re.sub(r'^#define '+macro+r' .+$',lambda _: '#define '+macro+' '+definition,harness,flags=re.M)
with tempfile.TemporaryDirectory(prefix='co2-scenarios-') as folder:
    cpp=Path(folder)/'sim.cpp';exe=Path(folder)/'sim'
    cpp.write_text(harness)
    subprocess.run(['g++','-std=c++11','-O2',str(cpp),'-o',str(exe)],check=True)
    result=subprocess.run([str(exe)],capture_output=True,text=True)
    if result.returncode: raise RuntimeError(result.stderr or f"Simulation exited with {result.returncode}")
    rows=[json.loads(line) for line in result.stdout.splitlines()]


# Bounds apply only to the defined hypothetical plant, not every possible valve.
for row in rows:
    assert row['min_interval_s']>=int(re.search(r'#define CO2_RESPONSE_LAG_MIN_MS (\d+)', source).group(1))//1000, row
    if not args.explore and not row['scenario'].startswith(('grid_', 'start_2000_','observed_')) and row['scenario'] not in ('cylinder_swap','empty','large_leak'):
        assert row['peak_ppm']<=51000, row
        assert row['last_hour_min']>=49000, row
# Unknown pressure change cannot be anticipated without a pause/notification.
assert next(r for r in rows if r['scenario']=='empty')['last_hour_max']<49000

if curve_model and not args.explore:
    for row in rows:
        if row['scenario'].startswith('observed_'):
            assert row['peak_ppm']<=51000, row
            assert 0<=row['first_band_s']<=3600, row
            if row['door_recovery_s']>=0: assert row['door_recovery_s']<=3600, row

grid=[r for r in rows if r['scenario'].startswith('grid_')]
if args.require_safe_grid:
    assert all(r['peak_ppm']<=51000 for r in grid if not r['scenario'].endswith('mode_4'))

summary={
    'firmware_sha256':hashlib.sha256(source.encode()).hexdigest(),
    'dosing_header_sha256':hashlib.sha256(header.read_bytes()).hexdigest() if curve_model else None,
    'simulator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'chamber_model':{'two_chambers':args.two_chambers,'mixer_volume_fraction_assumed':args.mixer_fraction if args.two_chambers else None,'sensor_node':args.sensor_node if args.two_chambers else 'single chamber','calibrated':False,'notes':'Transport, dispersion and chamber exchange are separate assumptions. Gas balance and tank limiting cases checked. Firmware timing still includes its legacy cycle counter.'},
    'grid_initial_ppm':2000 if args.cold_grid else 45000,
    'seed':args.seed,'scenario_count':len(rows),'simulated_hours':len(rows)*8,
    'model':'Real C++ dose selection, response timing and model header. Hypothetical chamber: transport lag + exponential mixing + constant loss; linear/dead-time and nonlinear valve plants. Nonlinear plant includes measured 207/320ms responses not used as dose presets. 30s door pause; sensor failure; valve contact outage then restoration. This is not a physical validation.',
    'parameter_ranges':{'gain_ppm_ms':[0.5,150],'loss_ppm_s':[0.01,3],'transport_delay_s':[0,args.transport_max_s],'mixing_time_constant_s':[10,120],'noise_ppm':[0,80],'valve_dead_time_ms':[0,80]},
    'grid_modes':{'0':'constant flow','1':'gradual depletion','2':'door + notified cylinder swap','3':'notified swap','4':'unannounced swap'},
    'grid_results':{},'named_scenarios':[r for r in rows if not r['scenario'].startswith('grid_')],
    'worst_notified_peaks':sorted([r for r in grid if not r['scenario'].endswith('mode_4')],key=lambda r:r['peak_ppm'],reverse=True)[:8],
    'worst_peaks':sorted(grid,key=lambda r:r['peak_ppm'],reverse=True)[:12],
}
for mode in range(5):
    group=[r for r in grid if r['scenario'].endswith('mode_'+str(mode))]
    summary['grid_results'][str(mode)]={'count':len(group),'peak_above_51000':sum(r['peak_ppm']>51000 for r in group),'last_hour_below_49000':sum(r['last_hour_min']<49000 for r in group),'last_hour_within_49000_51000':sum(r['last_hour_min']>=49000 and r['last_hour_max']<=51000 for r in group)}
reached=sorted(r['first_band_s'] for r in grid if r['first_band_s']>=0)
summary['grid_recovery']={
    'not_reached_in_8h':len(grid)-len(reached),
    'median_first_band_s':reached[len(reached)//2] if reached else None,
    'p90_first_band_s':reached[min(len(reached)-1,int(len(reached)*0.9))] if reached else None,
    'first_band_is_not_stability':True,
}
assert all(r['max_pulse_ms']<=1000 for r in rows)
text=json.dumps(summary,indent=2)+'\n'
if args.report: args.report.write_text(text)
print(text)
