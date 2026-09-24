"""
ETL orchestrator — runs the full pipeline in order.

  python 05_etl/run_all.py            full pipeline (skip raw generation)
  python 05_etl/run_all.py --gen      also regenerate raw data first

Phase gates: each stage prints PASS/FAIL; a failure aborts the run.
"""
from __future__ import annotations
import os, sys, time, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def sh(cmd: str) -> int:
    t0 = time.time()
    print(f"\n{'='*72}\n>>> {cmd}\n{'='*72}", flush=True)
    rc = subprocess.call(cmd, shell=True, cwd=HERE)
    print(f"<<< rc={rc} ({time.time()-t0:.1f}s)", flush=True)
    return rc


def main():
    if "--gen" in sys.argv:
        for s in ["python generate_raw_pms_pos.py", "python generate_raw_others.py"]:
            if sh(s) != 0:
                raise SystemExit(f"FAILED: {s}")

    stages = [
        "python 01_extract.py",           # raw → staging
        "python 02_profile.py",           # profile + dirty findings
        "python 00_build_master.py",      # master dims + alias maps
        "python 03_clean_map.py",         # clean · standardize · map → cleaned
        "python 07_validate.py",          # DQ framework + gate
        "pip install duckdb --quiet",     # ensure engine
        "python 08_load.py",              # cleaned → warehouse + marts
        "python 09_quality_report.py",    # DQ score per source → mart
        "python 10_eda.py",               # EDA
        "python 11_forecast.py",          # 90-day forecast
        "python 12_anomaly.py",           # anomaly detection
        "python 13_insights.py",          # AI insight layer
        "python 14_build_dashboards.py",  # 6 HTML dashboards
        "python 15_excel_workbook.py",    # 18-sheet demo workbook
        "python 16_reconcile.py",         # Python ↔ SQL ↔ dashboard
    ]
    for s in stages:
        if sh(s) != 0:
            raise SystemExit(f"FAILED: {s}")
    print("\n" + "=" * 72)
    print("PIPELINE COMPLETE")
    print("=" * 72)


if __name__ == "__main__":
    main()
