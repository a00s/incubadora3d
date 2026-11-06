#!/usr/bin/env python3
"""Exercise the uploaded experimental controller through the real sketch gates."""
from pathlib import Path
import runpy
from co2_firmware_harness import ROOT
runpy.run_path(str(Path(__file__).with_name('test_co2_simple_candidate.py')),
              init_globals={'MODEL_PATH': ROOT/'firmware/incubadora/co2_dosing.h'})
