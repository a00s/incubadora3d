#!/usr/bin/env python3
"""Simulate the real Uno controller against a fitted delayed plant and stress hypotheses."""
from pathlib import Path
import argparse, hashlib, json, subprocess, tempfile
from co2_firmware_harness import harness, ROOT
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--report',type=Path)
p.add_argument('--model',type=Path,help='Experimental model header; never uploads or replaces the production model.')
p.add_argument('--explore',action='store_true',help='Keep all scenario results, including target/safety failures.')
p.add_argument('--require-no-excess',action='store_true',help='Fail if any scenario reaches60000ppm, including delayed gas after cutoff.')
p.add_argument('--seed',type=int,default=20261106)
p.add_argument('--dead-max-ms',type=float,default=8,help='Hypothetical opening dead time; 0 gives the linear plant supported by the trace fit.')
a=p.parse_args()
with tempfile.TemporaryDirectory(prefix='co2-scenarios-') as folder:
    folder=Path(folder)
    (folder/'firmware_harness.h').write_text(harness(a.model))
    exe=folder/'simulate'
    subprocess.run(['g++','-std=c++11','-O2','-I'+str(folder),str(ROOT/'scripts/co2_scenarios.cpp'),'-o',str(exe)],check=True)
    out=subprocess.run([str(exe),str(a.seed),str(a.dead_max_ms)],capture_output=True,text=True,check=True)
rows=[json.loads(line) for line in out.stdout.splitlines()]
named=[r for r in rows if not r['scenario'].startswith('grid_')]
grid=[r for r in rows if r['scenario'].startswith('grid_')]
report={
 'seed':a.seed,'dead_time_max_ms':a.dead_max_ms,'scenario_count':len(rows),'simulated_hours':len(rows)*4,
 'hashes':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in
           [ROOT/'temperatura.ino',ROOT/'firmware/experimentos/co2_proporcional_simples.h',(a.model.resolve() if a.model else ROOT/'firmware/incubadora/co2_dosing.h'),Path(__file__),ROOT/'scripts/co2_scenarios.cpp',ROOT/'scripts/co2_firmware_harness.py']},
 'plant':{'fitted_to':'Boot9 four-hour trace; last chronological quarter held out',
          'gain_ppm_per_ms':70.6179,'leak_fraction_per_s':.0004,'delay_s':54,'mixing_tau_s':4,
          'holdout_rmse_ppm':838.0,'physical_calibration':False,
          'notes':'Approximate input/output fit, not isolated valve calibration. Random delay, dead time, pressure, noise and leakage are stress hypotheses. Pending plant gas continues after valve cutoff.'},
 'named_scenarios':named,
 'parameter_ranges':{'initial_gain_ppm_ms':[35,200],'after_gain_ratio':[.2,4],'after_gain_ppm_ms':[7,800],'leak_fraction_s':[.0002,.0008],'delay_s':[30,70],'mixing_s':[2,12],'noise_ppm':[0,20],'opening_dead_ms':[0,a.dead_max_ms]},
 'grid':{'count':len(grid),'range_locks':sum(r['range_locked'] for r in grid),
         'peak_above_51000':sum(r['peak_ppm']>51000 for r in grid),
         'last_hour_within_49000_51000':sum(r['last_hour_min']>=49000 and r['last_hour_max']<=51000 for r in grid),
         'not_reached_in_4h':sum(r['first_band_s']<0 for r in grid),
         'unresolved_responses':sum(r['unresolved_response'] for r in grid)},
 'worst':sorted(grid,key=lambda r:r['peak_ppm'],reverse=True)[:10],
 'limits':'Stress failures are retained. Simulation cannot guarantee unknown cylinder flow, mixing changes or a stuck valve. A notified cylinder change resets learning; an unannounced abrupt pressure change is only observable after gas reaches the sensor.'}
report['validation']={
 'safety_failures':[r['scenario'] for r in rows if r['peak_ppm']>=60000 or r['range_locked']],
 'startup_failures':[key for key in ('cold_16000_dead22','cold_6400_dead22') if not 0<=next(r for r in named if r['scenario']==key)['first_band_s']<=1200],
 'experimental_model':str(a.model) if a.model else None}
if a.report:a.report.write_text(json.dumps(report,indent=2)+'\n')
assert all(r['min_interval_s']>=20 for r in rows)
if a.require_no_excess:assert all(r['peak_ppm']<60000 and not r['range_locked'] for r in rows),sorted(rows,key=lambda r:r['peak_ppm'],reverse=True)[:1]
for key in ('fitted_nominal','cold_2000','pressure_half','depleting','door','noise_20'):
    r=next(r for r in named if r['scenario']==key)
    if not a.explore:assert r['range_locked']==0 and r['peak_ppm']<52000,r
assert next(r for r in named if r['scenario']=='empty')['last_hour_max']<49000
for key in ('cold_16000_dead22','cold_6400_dead22'):
    r=next(r for r in named if r['scenario']==key)
    if not a.explore:assert 0 <= r['first_band_s'] <= 1200,r
assert next(r for r in named if r['scenario']=='empty')['unresolved_response']==1

print(json.dumps(report,indent=2))
