// The controller/gates below are generated from the actual firmware, not reimplemented.
#include "firmware_harness.h"
#include <vector>
#include <random>
#include <cstdio>
struct Result {double peak,low,high,mean;int first,doses,minInterval,locked;};
Result run(double g0,double g1,double lambda,int delay,double mixing,double initial,
           bool gradual=false,bool notified=false,int door=-1,double noise=0,double dead=0,
           bool dropout=false,bool contact=false){
 resetFirmware();double ppm=initial,q=0,peak=initial,lo=1e9,hi=0,total=0;
 std::vector<double> future(7300,0);int first=-1,doses=0,count=0,shortest=999999;
 uint32_t previousDose=0;int previousSensed=(int)initial;bool locked=false;
 for(int t=0;t<14400;t+=2){
  uint32_t now=(uint32_t)t*1000;
  bool opened=door>=0&&t>=door&&t<door+30;
  if(t==door){ppm=2000;co2DoseModel.reset(true);}
  if(t==door+30&&door>=0)co2DoseModel.reset(true);
  if(t==7200&&notified)co2DoseModel.reset(true);
  q+=future[t/2];double rise=q*(1-std::exp(-2/mixing));q-=rise;
  ppm=400+(ppm-400)*std::exp(-lambda*2)+rise;
  int sensed=(int)std::lround(ppm+noise*std::sin(t*1.71));
  if(sensed>=60000)locked=true; // Same persistent concentration cut as the Uno.
  bool valid=!locked&&sensed>0&&sensed<=65535&&!(dropout&&t>=7400&&t<7500);
  CO2i=sensed;co2Rate=(sensed-previousSensed)/2.f;previousSensed=sensed;
  co2DoseModel.update(now,sensed,valid,!opened);
  if(!valid){co2DoseModel.reset(true);co2LastPulseAt=now;lastCo2PulseMs=0;}
  if(valid)updateCo2RecentRise(now);
  uint16_t pulse=firmwarePulse(now,valid,!opened);
  if(pulse){
   double gain=gradual?g0+(g1-g0)*t/14400:(t<7200?g0:g1);
   if(contact&&t>=6000&&t<6600)gain=0;
   future[(t+delay)/2+1]+=gain*std::max(0.0,pulse-dead);
   recordAutomatic(pulse,now);doses++;
   if(previousDose)shortest=std::min(shortest,(int)((now-previousDose)/1000));
   previousDose=now;assert(pulse>=5&&pulse<=1000);
  }
  peak=std::max(peak,ppm);
  if(ppm>=49000&&ppm<=51000&&first<0)first=t;
  if(t>=10800){lo=std::min(lo,ppm);hi=std::max(hi,ppm);total+=ppm;count++;}
 }
 assert(shortest==999999||shortest>=20);
 return {peak,lo,hi,total/count,first,doses,shortest,locked?1:0};
}
void emit(const char*name,Result r){
 printf("{\"scenario\":\"%s\",\"peak_ppm\":%.1f,\"last_hour_min\":%.1f,\"last_hour_max\":%.1f,\"last_hour_mean\":%.1f,\"first_band_s\":%d,\"doses\":%d,\"min_interval_s\":%d,\"range_locked\":%d}\n",name,r.peak,r.low,r.high,r.mean,r.first,r.doses,r.minInterval,r.locked);
}
int main(int argc,char**argv){
 unsigned seed=argc>1?(unsigned)std::strtoul(argv[1],nullptr,10):20261106;
 emit("fitted_nominal",run(70.6179,70.6179,.0004,54,4,48000));
 emit("cold_2000",run(70.6179,70.6179,.0004,54,4,2000));
 emit("delay_30",run(70,70,.0004,30,4,48000));
 emit("delay_70",run(70,70,.0004,70,4,48000));
 emit("mixing_12",run(70,70,.0004,54,12,48000));
 emit("pressure_half",run(70,35,.0004,54,4,48000));
 emit("pressure_double",run(70,140,.0004,54,4,48000));
 emit("depleting",run(100,20,.0006,54,4,48000,true));
 emit("notified_swap",run(35,140,.0004,54,4,48000,false,true));
 emit("door",run(70,70,.0004,54,4,48000,false,false,7200));
 emit("noise_20",run(70,70,.0004,54,4,48000,false,false,-1,20));
 emit("dead_7_hypothesis",run(100,100,.0004,54,4,48000,false,false,-1,0,7));
 emit("high_flow",run(200,200,.0006,54,4,48000));
 emit("empty",run(0,0,.0004,54,4,48000));
 emit("sensor_dropout",run(70,70,.0004,54,4,48000,false,false,-1,0,0,true));
 emit("contact_outage",run(70,70,.0004,54,4,48000,false,false,-1,0,0,false,true));
 double deadMax=argc>2?std::strtod(argv[2],nullptr):8;
 std::mt19937 random(seed);auto u=[&](){return random()/(double)UINT32_MAX;};
 for(int k=0;k<2000;k++){
  double g=35+165*u(),ratio=.2+3.8*u(),lambda=.0002+.0006*u();
  int delay=30+2*(random()%21),mode=k%5;
  char name[48];std::snprintf(name,sizeof(name),"grid_%d_mode_%d",k,mode);
  emit(name,run(g,g*ratio,lambda,delay,2+10*u(),k%2?2000:48000,
       mode==1,mode==2||mode==3,mode==2?7200:-1,20*u(),deadMax*u(),k%13==0,k%17==0));
 }
}
