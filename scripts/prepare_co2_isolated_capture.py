#!/usr/bin/env python3
"""Prepare an isolated CO2 measurement build; never uploads or sends a command."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--compile', action='store_true')
a = p.parse_args()
folder = ROOT/'.arduino-build/isolated_capture_sketch'
folder.mkdir(parents=True, exist_ok=True)
source = (ROOT/'temperatura.ino').read_text()
changes = {
    '#define CO2_SENSOR_WARMUP_MS 120000UL': '#define CO2_SENSOR_WARMUP_MS 240000UL',
    'bool manualCo2Pulse(const char *source, uint16_t pulseMs = MANUAL_CO2_PULSE_MS)':
    'bool manualCo2Pulse(const char *source, uint16_t pulseMs = 20)',
}
for old, new in changes.items():
    if source.count(old) != 1:
        raise SystemExit('Source changed: capture patch must be reviewed again.')
    source = source.replace(old, new)
sketch = folder/'isolated_capture_sketch.ino'
sketch.write_text(source)
for name in ('display_font.h', 'co2_dosing.h'):
    shutil.copyfile(ROOT/'firmware/incubadora'/name, folder/name)
report = {'uploaded': False, 'commands_sent': [], 'automatic_resume_after_boot_s': 240,
          'serial_prime_ms': 20, 'changes': changes,
          'source_sha256': hashlib.sha256(sketch.read_bytes()).hexdigest(),
          'production_source_sha256': hashlib.sha256((ROOT/'temperatura.ino').read_bytes()).hexdigest(),
          'model_sha256': hashlib.sha256((folder/'co2_dosing.h').read_bytes()).hexdigest()}
if a.compile:
    cli = shutil.which('arduino-cli') or str(Path.home()/'.local/bin/arduino-cli')
    flags = '-mcall-prologues -fno-inline-small-functions -fno-split-wide-types -fno-tree-scev-cprop -mstrict-X'
    result = subprocess.run([cli, 'compile', '--fqbn', 'arduino:avr:uno',
        '--build-property', 'compiler.c.extra_flags='+flags,
        '--build-property', 'compiler.cpp.extra_flags='+flags,
        '--build-property', 'compiler.c.elf.extra_flags=-Wl,--relax',
        '--libraries', str(ROOT/'arduino-libraries'),
        '--build-path', str(ROOT/'.arduino-build/isolated_capture_binary'), str(folder)],
        capture_output=True, text=True)
    report.update(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
    binary = ROOT/'.arduino-build/isolated_capture_binary/isolated_capture_sketch.ino.hex'
    if result.returncode == 0:
        report['hex_sha256'] = hashlib.sha256(binary.read_bytes()).hexdigest()
    print(result.stdout, end='')
    if result.returncode:
        print(result.stderr)
        raise SystemExit(result.returncode)
manifest = ROOT/'.arduino-build/isolated_capture_prepared.json'
manifest.write_text(json.dumps(report, indent=2)+'\n')
print('Prepared only; no upload or actuator command. Manifest:', manifest)
