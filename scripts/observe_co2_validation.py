#!/usr/bin/env python3
"""Read-only fixed-window validation of captured CO2 telemetry; no serial access."""
import argparse
import hashlib
import json
from pathlib import Path
import time


def summarize(path, seconds=600, min_steps=1):
    raw = path.read_bytes()
    rows = []
    host = None
    boot = None
    boots = []
    for line in raw.decode(errors='replace').splitlines():
        a = line.split(',')
        if a[0] == 'HOST_TIME':
            host = float(a[1])
        elif a[0] == 'BOOT_COUNT':
            boot = a[1]
            boots.append(boot)
        elif len(a) == 26 and a[0] == 'DATA' and a[1].isdigit() and host is not None:
            rows.append((host, boot, a))
    if not rows:
        return {'complete': False, 'samples': 0, 'source': str(path)}
    first = next((r for r in rows if r[2][3] == '1' and int(r[2][20]) >= min_steps
                  and 49000 <= int(r[2][2]) <= 51000), None)
    last = rows[-1]
    a = last[2]
    result = {'complete': bool(first and last[0]-first[0] >= seconds),
              'source': str(path), 'snapshot_sha256': hashlib.sha256(raw).hexdigest(),
              'boots': boots, 'min_steps': min_steps, 'window_seconds': seconds,
              'elapsed_window_seconds': round(last[0]-first[0], 2) if first else None,
              'latest': {'host_time': last[0], 'ppm': int(a[2]) if a[3] == '1' else None,
                         'raw_ppm': int(a[2]), 'co2_enabled': a[7] == '1',
                         'heater_enabled': a[8] == '1', 'range_lock': a[24] == '1',
                         'steps': int(a[20]), 'last_ms': int(a[13])}}
    if first:
        window = [r for r in rows if first[0] <= r[0] <= first[0]+seconds]
        valid = [r for r in window if r[2][3] == '1' and 0 < int(r[2][2]) <= 65535]
        values = [int(r[2][2]) for r in valid]
        in_band = sum(49000 <= v <= 51000 for v in values)
        result['window'] = {'start_host_time': first[0], 'end_host_time': window[-1][0],
                            'samples': len(window), 'valid_samples': len(valid),
                            'invalid_samples': len(window)-len(valid),
                            'min_ppm': min(values) if values else None,
                            'max_ppm': max(values) if values else None,
                            'mean_ppm': round(sum(values)/len(values), 2) if values else None,
                            'in_band_fraction_of_valid': in_band/len(valid) if valid else 0,
                            'in_band_fraction_of_all': in_band/len(window),
                            'all_controls_enabled': all(r[2][7] == '1' and r[2][8] == '1' for r in window),
                            'any_range_lock': any(r[2][24] == '1' for r in window),
                            'same_boot': all(r[1] == first[1] for r in window)}
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('log', type=Path)
    p.add_argument('--minutes', type=float, default=10)
    p.add_argument('--min-steps', type=int, default=1)
    p.add_argument('--report', type=Path)
    p.add_argument('--watch', action='store_true')
    p.add_argument('--deadline-minutes', type=float, default=30)
    args = p.parse_args()
    started = time.monotonic()
    while True:
        result = summarize(args.log, args.minutes*60, args.min_steps)
        if args.report:
            args.report.write_text(json.dumps(result, indent=2)+'\n')
        print(json.dumps(result), flush=True)
        if result['complete'] or not args.watch:
            break
        if time.monotonic()-started >= args.deadline_minutes*60:
            raise SystemExit('Window incomplete by deadline; no actuator command sent.')
        time.sleep(30)
