#!/usr/bin/env python3
"""Simulate the real Uno controller against a fitted delayed plant and stress hypotheses."""
from pathlib import Path
import argparse, hashlib, json, subprocess, tempfile
from co2_firmware_harness import harness, ROOT
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--report',type=Path)
p.add_argument('--seed',type=int,default=20261106)
p.add_argument('--dead-max-ms',type=float,default=8,help='Hypothetical opening dead time; 0 gives the linear plant supported by the trace fit.')
a=p.parse_args()
with tempfile.TemporaryDirectory(prefix='co2-scenarios-') as folder:
    folder=Path(folder)
    (folder/'firmware_harness.h').write_text(harness())
    exe=folder/'simulate'
    subprocess.run(['g++','-std=c++11','-O2','-I'+str(folder),str(ROOT/'scripts/co2_scenarios.cpp'),'-o',str(exe)],check=True)
    out=subprocess.run([str(exe),str(a.seed),str(a.dead_max_ms)],capture_output=True,text=True,check=True)
rows=[json.loads(line) for line in out.stdout.splitlines()]
named=[r for r in rows if not r['scenario'].startswith('grid_')]
grid=[r for r in rows if r['scenario'].startswith('grid_')]
report={
 'seed':a.seed,'dead_time_max_ms':a.dead_max_ms,'scenario_count':len(rows),'simulated_hours':len(rows)*4,
 'hashes':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest() for path in
           [ROOT/'temperatura.ino',ROOT/'firmware/incubadora/co2_dosing.h',Path(__file__),ROOT/'scripts/co2_scenarios.cpp',ROOT/'scripts/co2_firmware_harness.py']},
 'plant':{'fitted_to':'Boot9 four-hour trace; last chronological quarter held out',
          'gain_ppm_per_ms':70.6179,'leak_fraction_per_s':.0004,'delay_s':54,'mixing_tau_s':4,
          'holdout_rmse_ppm':838.0,'physical_calibration':False,
          'notes':'Approximate input/output fit, not isolated valve calibration. Random delay, dead time, pressure, noise and leakage are stress hypotheses. Pending plant gas continues after valve cutoff.'},
 'named_scenarios':named,
 'grid':{'count':len(grid),'range_locks':sum(r['range_locked'] for r in grid),
         'peak_above_51000':sum(r['peak_ppm']>51000 for r in grid),
         'last_hour_within_49000_51000':sum(r['last_hour_min']>=49000 and r['last_hour_max']<=51000 for r in grid),
         'not_reached_in_4h':sum(r['first_band_s']<0 for r in grid)},
 'worst':sorted(grid,key=lambda r:r['peak_ppm'],reverse=True)[:10],
 'limits':'Stress failures are retained. Simulation cannot guarantee unknown cylinder flow, mixing changes or a stuck valve. A notified cylinder change resets learning; an unannounced abrupt pressure change is only observable after gas reaches the sensor.'}
assert all(r['min_interval_s']>=20 for r in rows)
for key in ('fitted_nominal','cold_2000','pressure_half','depleting','door','noise_20'):
    r=next(r for r in named if r['scenario']==key)
    assert r['range_locked']==0 and r['peak_ppm']<52000,r
assert next(r for r in named if r['scenario']=='empty')['last_hour_max']<49000
if a.report:a.report.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
