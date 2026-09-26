"""
Run all pipeline stages and build outputs.
"""
from __future__ import annotations
import os, sys, subprocess, time

HERE = os.path.dirname(os.path.abspath(__file__))

def sh(cmd):
    print("\n" + "="*72 + "\n>>> " + cmd + "\n" + "="*72)
    t0 = time.time()
    rc = subprocess.call(cmd, shell=True, cwd=HERE)
    print(f"<<< rc={rc} ({time.time()-t0:.1f}s)")
    return rc

def main():
    if "--gen" in sys.argv:
        sh("python generate_raw_pms_pos.py")
        sh("python generate_raw_others.py")

    stages = [
        "python 01_extract.py",
        "python 02_profile.py",
        "python 00_build_master.py",
        "python 03_clean_map.py",
        "python 07_validate.py",
        "pip install duckdb --quiet",
        "python 08_load.py",
        "python 09_quality_report.py",
        "python 10_eda.py",
        "python 11_forecast.py",
        "python 12_anomaly.py",
        "python 13_insights.py",
        "python 14_build_dashboard.py",
        "python 15_reconcile.py",
    ]
    for s in stages:
        if sh(s) != 0:
            raise SystemExit(f"FAILED: {s}")
    print("\n" + "="*72)
    print("PIPELINE COMPLETE")
    print("="*72)

if __name__ == "__main__":
    main()
