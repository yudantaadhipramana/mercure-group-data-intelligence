#!/usr/bin/env python
"""
Regenerate raw sources with new product alias mapping, then staging, master, clean, validate.
This script is a quick repair path after product category was corrected.
"""
import subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P

steps = [
    "python generate_raw_pms_pos.py",
    "python generate_raw_others.py",
    "python 01_extract.py",
    "python 02_profile.py",
    "python 00_build_master.py",
    "python 07_validate.py",
]
for s in steps:
    print(f"\n>>> {s}")
    rc = subprocess.call(s, shell=True)
    if rc != 0:
        print(f"FAILED {s} rc={rc}")
        sys.exit(rc)
print("REPAIR COMPLETE")
