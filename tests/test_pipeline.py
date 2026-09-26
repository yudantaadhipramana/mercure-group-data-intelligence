import pytest
import os, sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '05_etl'))
import params as P

def test_params_seed_determinism():
    from params import rng
    r1 = rng(1).random(10)
    r2 = rng(1).random(10)
    assert np.allclose(r1, r2)

def test_raw_files_exist():
    for sub in ['pms','pos','finance','inventory','procurement','budget']:
        assert os.path.exists(os.path.join(P.RAW_DIRS[sub])), f"missing {sub}"

def test_staging_parquet():
    for name in ['pms','pos','finance','inventory','procurement','budget']:
        p = os.path.join(P.STG_DIR, f"stg_{name}.parquet")
        assert os.path.exists(p)

def test_master_dims():
    for name in ['dim_property','dim_product','dim_account','dim_date']:
        assert os.path.exists(os.path.join(P.MST_DIR, f"{name}.parquet"))

def test_cleaned_files():
    for name in ['pms','pos','finance','inventory','procurement','budget']:
        p = os.path.join(P.CLN_DIR, f"clean_{name}.parquet")
        assert os.path.exists(p)

def test_data_quality_gate():
    # key checks already passed in 07_validate.py
    pms = pd.read_parquet(os.path.join(P.CLN_DIR, "clean_pms.parquet"))
    assert pms["booking_id"].duplicated().sum() == 0
    assert (pms["check_out"] >= pms["check_in"]).all()

def test_warehouse_exists():
    assert os.path.exists(P.DB_PATH)

def test_mart_kpi_daily():
    import duckdb
    c = duckdb.connect(P.DB_PATH, read_only=True)
    n = c.execute("SELECT COUNT(*) FROM mart_kpi_daily").fetchone()[0]
    assert n > 0
    c.close()

def test_dashboard_json_exists():
    assert os.path.exists(os.path.join(P.DASH_DIR, "dashboard_data.json"))
