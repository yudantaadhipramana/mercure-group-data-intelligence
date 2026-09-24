"""
ETL 08 — LOAD: cleaned parquet → DuckDB warehouse (PostgreSQL-compatible design).

Creates the star schema (mirrors 07_sql/01_warehouse_postgresql.ddl),
loads dims + facts, builds indexes, then creates the mart views.
Referential integrity is enforced by explicit FK checks in 07_validate.py
(DuckDB FK constraints are not enforced at insert time).
"""
from __future__ import annotations
import sys, os, glob
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P

try:
    import duckdb
except ImportError:
    raise SystemExit("duckdb not installed — run: pip install duckdb")


def con():
    return duckdb.connect(P.DB_PATH)


# ------------------------------------------------------------------ DDL
DDL = """
DROP TABLE IF EXISTS fact_budget;      DROP TABLE IF EXISTS fact_expense;
DROP TABLE IF EXISTS fact_purchase;     DROP TABLE IF EXISTS fact_inventory;
DROP TABLE IF EXISTS fact_fnb_sales;    DROP TABLE IF EXISTS fact_room_sales;
DROP TABLE IF EXISTS map_category_alias; DROP TABLE IF EXISTS map_account_alias;
DROP TABLE IF EXISTS map_product_alias;   DROP TABLE IF EXISTS map_property_alias;
DROP TABLE IF EXISTS etl_cleansing_log;   DROP TABLE IF EXISTS etl_batch_run;
DROP TABLE IF EXISTS dim_supplier;      DROP TABLE IF EXISTS dim_account;
DROP TABLE IF EXISTS dim_room_type;     DROP TABLE IF EXISTS dim_channel;
DROP TABLE IF EXISTS dim_customer_segment; DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_product_category; DROP TABLE IF EXISTS dim_department;
DROP TABLE IF EXISTS dim_business_unit; DROP TABLE IF EXISTS dim_property;
DROP TABLE IF EXISTS dim_date;

CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY, full_date DATE NOT NULL UNIQUE,
    year SMALLINT, quarter SMALLINT, month SMALLINT, month_name VARCHAR,
    day_of_week SMALLINT, day_name VARCHAR, is_weekend SMALLINT,
    is_holiday_flag SMALLINT, holiday_name VARCHAR,
    day_of_year SMALLINT, week_of_year SMALLINT);
CREATE TABLE dim_property (
    property_id VARCHAR PRIMARY KEY, property_name VARCHAR, business_type VARCHAR,
    city VARCHAR, region VARCHAR, rooms INTEGER, property_class VARCHAR);
CREATE TABLE dim_business_unit (
    business_unit_id VARCHAR PRIMARY KEY, business_unit_name VARCHAR, business_type VARCHAR);
CREATE TABLE dim_department (
    department_id VARCHAR PRIMARY KEY, department_name VARCHAR);
CREATE TABLE dim_product_category (
    category_id VARCHAR PRIMARY KEY, category_name VARCHAR);
CREATE TABLE dim_product (
    product_id VARCHAR PRIMARY KEY, product_name VARCHAR, category_id VARCHAR,
    base_price DOUBLE, unit_cost_ratio DOUBLE, active_flag SMALLINT);
CREATE TABLE dim_customer_segment (
    segment_id VARCHAR PRIMARY KEY, segment_name VARCHAR);
CREATE TABLE dim_channel (
    channel_id VARCHAR PRIMARY KEY, channel_name VARCHAR);
CREATE TABLE dim_room_type (
    room_type_id VARCHAR PRIMARY KEY, room_type_name VARCHAR, price_multiplier DOUBLE);
CREATE TABLE dim_account (
    account_id VARCHAR PRIMARY KEY, account_code VARCHAR, account_name VARCHAR,
    account_type VARCHAR, department_id VARCHAR);
CREATE TABLE dim_supplier (
    supplier_id VARCHAR PRIMARY KEY, supplier_name VARCHAR, city VARCHAR,
    lead_time_days INTEGER, payment_terms_days INTEGER);

CREATE TABLE fact_room_sales (
    booking_id VARCHAR PRIMARY KEY, date_id INTEGER, property_id VARCHAR,
    room_type_id VARCHAR, segment_id VARCHAR, channel_id VARCHAR,
    los INTEGER, rooms_sold INTEGER, room_nights INTEGER,
    room_revenue DOUBLE, adr_amount DOUBLE, is_cancelled SMALLINT, is_no_show SMALLINT,
    source_file VARCHAR, raw_row INTEGER);
CREATE TABLE fact_fnb_sales (
    transaction_id VARCHAR, line_no INTEGER, date_id INTEGER, property_id VARCHAR,
    outlet_name VARCHAR, product_id VARCHAR, category_id VARCHAR,
    quantity DOUBLE, gross_sales DOUBLE, discount DOUBLE, net_sales DOUBLE,
    unit_price DOUBLE, cogs_amount DOUBLE, gross_profit DOUBLE,
    is_void SMALLINT, is_refund SMALLINT, source_file VARCHAR, raw_row INTEGER,
    PRIMARY KEY (transaction_id, line_no));
CREATE TABLE fact_inventory (
    date_id INTEGER, property_id VARCHAR, product_id VARCHAR,
    opening_stock DOUBLE, purchase_qty DOUBLE, transfer_qty DOUBLE,
    consumption_qty DOUBLE, waste_qty DOUBLE, closing_stock DOUBLE,
    unit_cost DOUBLE, stock_value DOUBLE, inventory_variance DOUBLE,
    PRIMARY KEY (date_id, property_id, product_id));
CREATE TABLE fact_purchase (
    purchase_line_id VARCHAR PRIMARY KEY, date_id INTEGER, property_id VARCHAR,
    product_id VARCHAR, supplier_id VARCHAR,
    quantity DOUBLE, unit_price DOUBLE, total_amount DOUBLE);
CREATE TABLE fact_expense (
    expense_id VARCHAR PRIMARY KEY, date_id INTEGER, property_id VARCHAR,
    department_id VARCHAR, account_id VARCHAR,
    amount DOUBLE, transaction_type VARCHAR, is_cogs SMALLINT,
    source_file VARCHAR, raw_row INTEGER);
CREATE TABLE fact_budget (
    date_id INTEGER, property_id VARCHAR, department_id VARCHAR, account_id VARCHAR,
    budget_amount DOUBLE, budget_year INTEGER, budget_month INTEGER,
    PRIMARY KEY (date_id, property_id, department_id, account_id));

CREATE TABLE map_property_alias (raw_alias VARCHAR PRIMARY KEY, property_id VARCHAR);
CREATE TABLE map_product_alias  (raw_alias VARCHAR PRIMARY KEY, product_id VARCHAR);
CREATE TABLE map_account_alias  (raw_alias VARCHAR PRIMARY KEY, account_id VARCHAR);
CREATE TABLE map_category_alias (raw_alias VARCHAR PRIMARY KEY, category_id VARCHAR);
CREATE TABLE etl_cleansing_log (
    log_id INTEGER PRIMARY KEY, rule VARCHAR, source VARCHAR,
    records_affected INTEGER, before_example VARCHAR, after_example VARCHAR);
CREATE TABLE etl_batch_run (
    run_id INTEGER PRIMARY KEY, started_at VARCHAR, ended_at VARCHAR, stage VARCHAR,
    rows_in BIGINT, rows_out BIGINT, status VARCHAR);
"""

INDEXES = """
CREATE INDEX idx_room_date   ON fact_room_sales(date_id);
CREATE INDEX idx_room_prop    ON fact_room_sales(property_id);
CREATE INDEX idx_fnb_date     ON fact_fnb_sales(date_id);
CREATE INDEX idx_fnb_prop     ON fact_fnb_sales(property_id);
CREATE INDEX idx_fnb_prod     ON fact_fnb_sales(product_id);
CREATE INDEX idx_fnb_outlet   ON fact_fnb_sales(outlet_name);
CREATE INDEX idx_inv_prop     ON fact_inventory(property_id);
CREATE INDEX idx_inv_prod     ON fact_inventory(product_id);
CREATE INDEX idx_pur_date     ON fact_purchase(date_id);
CREATE INDEX idx_exp_date     ON fact_expense(date_id);
CREATE INDEX idx_exp_prop     ON fact_expense(property_id);
CREATE INDEX idx_exp_acc      ON fact_expense(account_id);
CREATE INDEX idx_bud_prop     ON fact_budget(property_id);
"""

# ------------------------------------------------------------------ load helper
def load_csv_table(c, table: str, csv_path: str, columns: list[str] | None = None):
    cols = "" if columns is None else f"({', '.join(columns)})"
    c.execute(f"COPY {table} {cols} FROM '{csv_path}' (HEADER, DELIMITER ',');")
    n = c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"[08] {table}: {n:,} rows")
    return n


def main():
    os.makedirs(P.DWH_DIR, exist_ok=True)
    c = con()
    print("[08] creating schema ...", flush=True)
    c.execute(DDL)
    for stmt in [s.strip() for s in INDEXES.split(";") if s.strip()]:
        c.execute(stmt)
    print("[08] schema + indexes ready", flush=True)

    M = P.MST_DIR
    for f in sorted(glob.glob(os.path.join(M, "dim_*.parquet")) + glob.glob(os.path.join(M, "map_*.parquet"))):
        tbl = os.path.basename(f)[:-8]
        df = pd.read_parquet(f)
        c.register("_tmp", df)
        c.execute(f"INSERT INTO {tbl} SELECT * FROM _tmp")
        c.unregister("_tmp")
        print(f"[08] {tbl}: {len(df):,} rows")

    # facts from cleaned
    C = P.CLN_DIR
    facts = {
        "fact_room_sales": "clean_pms.parquet",
        "fact_fnb_sales": "clean_pos.parquet",
        "fact_inventory": "clean_inventory.parquet",
        "fact_purchase": "clean_procurement.parquet",
    }
    for tbl, fn in facts.items():
        p = os.path.join(C, fn)
        if not os.path.exists(p):
            print(f"[08] MISSING {p}")
            continue
        df = pd.read_parquet(p)
        c.register("_tmp", df)
        c.execute(f"INSERT INTO {tbl} SELECT * FROM _tmp")
        c.unregister("_tmp")
        print(f"[08] {tbl}: {len(df):,} rows")

    # fact_expense from cleaned finance
    p = os.path.join(C, "clean_finance.parquet")
    if os.path.exists(p):
        df = pd.read_parquet(p)
        df["is_cogs"] = 0
        c.register("_tmp", df)
        c.execute("""INSERT INTO fact_expense
                     SELECT transaction_id, date_id, property_id, department_id, account_id,
                            amount, transaction_type, is_cogs, source_file, raw_row
                     FROM _tmp""")
        c.unregister("_tmp")
        print(f"[08] fact_expense: {len(df):,} rows")

    # fact_budget
    p = os.path.join(C, "clean_budget.parquet")
    if os.path.exists(p):
        df = pd.read_parquet(p)
        c.register("_tmp", df)
        c.execute("""INSERT INTO fact_budget
                     SELECT date_id, property_id, department_id, account_id,
                            budget_amount, budget_year, budget_month
                     FROM _tmp""")
        c.unregister("_tmp")
        print(f"[08] fact_budget: {len(df):,} rows")

    # cleansing log
    p = os.path.join(C, "cleansing_log.parquet")
    if os.path.exists(p):
        df = pd.read_parquet(p).reset_index(drop=True)
        df["log_id"] = df.index + 1
        c.register("_tmp", df)
        c.execute("""INSERT INTO etl_cleansing_log
                     SELECT log_id, rule, source, records_affected, before_example, after_example
                     FROM _tmp""")
        c.unregister("_tmp")
        print(f"[08] etl_cleansing_log: {len(df):,} rows")

    c.close()
    print("[08] DONE")


if __name__ == "__main__":
    main()
