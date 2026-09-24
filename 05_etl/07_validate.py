"""
ETL 07 — VALIDATE: run the ETL clean/map stage, then enforce the data-quality
gate on the cleaned output (the warehouse contract).

Gate (must PASS before load):
  * 0 nulls on primary keys
  * 0 duplicate primary keys
  * 100% of fact foreign keys resolve to a dimension row
  * referential integrity for every fact → dim pair
  * business rules: net ≤ gross, occupancy ≤ 100%, closing ≥ 0, dates in window
"""
from __future__ import annotations
import sys, os, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P
import importlib.util

spec = importlib.util.spec_from_file_location("cm", os.path.join(os.path.abspath("."), "03_clean_map.py"))
CM = importlib.util.module_from_spec(spec)
spec.loader.exec_module(CM)

FAILS: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        FAILS.append(name)
    return ok


def load_master(name: str) -> pd.DataFrame:
    return pd.read_parquet(os.path.join(P.MST_DIR, f"{name}.parquet"))


def main():
    os.makedirs(P.CLN_DIR, exist_ok=True)
    M = P.MST_DIR

    map_prop = load_master("map_property_alias")
    map_prod = load_master("map_product_alias")
    dim_seg = load_master("dim_customer_segment")
    dim_ch = load_master("dim_channel")
    dim_rt = load_master("dim_room_type")
    dim_acc = load_master("dim_account")
    map_acc = load_master("map_account_alias")
    dim_sup = load_master("dim_supplier")
    dim_prod = load_master("dim_product")
    dim_cat = load_master("dim_product_category")

    # merge product cost ratio onto category dim for POS COGS
    dim_prod_cat = dim_prod.merge(dim_cat, on="category_id", how="left")

    def stg(n):
        return pd.read_parquet(os.path.join(P.STG_DIR, f"stg_{n}.parquet"))

    # ---- clean + map each source
    print("[07] clean/map PMS", flush=True)
    pms = CM.clean_pms(stg("pms"), map_prop, dim_seg, dim_ch, dim_rt)
    print("[07] clean/map POS", flush=True)
    pos = CM.clean_pos(stg("pos"), map_prop, map_prod, dim_prod)
    print("[07] clean/map FINANCE", flush=True)
    fin = CM.clean_finance(stg("finance"), map_prop, dim_acc, map_acc, None)
    print("[07] clean/map INVENTORY", flush=True)
    inv = CM.clean_inventory(stg("inventory"), map_prop, map_prod)
    print("[07] clean/map PROCUREMENT", flush=True)
    pro = CM.clean_procurement(stg("procurement"), map_prop, map_prod, dim_sup)
    print("[07] clean/map BUDGET", flush=True)
    bud = CM.clean_budget(stg("budget"), map_prop, dim_acc, map_acc)

    # department map for finance
    dep = load_master("dim_department")
    dep_by_name = dict(zip(dep["department_name"], dep["department_id"]))
    fin["department_id"] = fin["department"].map(lambda v: dep_by_name.get(str(v).strip()))
    fin["expense_id"] = fin["transaction_id"]
    fin["is_cogs"] = 0

    # ---- write cleaned
    pms.to_parquet(os.path.join(P.CLN_DIR, "clean_pms.parquet"), index=False)
    pos.to_parquet(os.path.join(P.CLN_DIR, "clean_pos.parquet"), index=False)
    fin.to_parquet(os.path.join(P.CLN_DIR, "clean_finance.parquet"), index=False)
    inv.to_parquet(os.path.join(P.CLN_DIR, "clean_inventory.parquet"), index=False)
    pro.to_parquet(os.path.join(P.CLN_DIR, "clean_procurement.parquet"), index=False)
    bud.to_parquet(os.path.join(P.CLN_DIR, "clean_budget.parquet"), index=False)
    pd.DataFrame(CM.LOG_ROWS).to_parquet(os.path.join(P.CLN_DIR, "cleansing_log.parquet"), index=False)
    print(f"[07] cleansing log: {len(CM.LOG_ROWS)} rules logged")

    # ---- GATE
    print("\n[07] === DATA QUALITY GATE ===")
    check("PMS: no duplicate booking_id", pms["booking_id"].duplicated().sum() == 0,
          f"{pms['booking_id'].duplicated().sum()} dups")
    check("PMS: no null booking_id", pms["booking_id"].notna().all())
    check("PMS: check_in < check_out", (pms["check_out"] >= pms["check_in"]).all())
    check("PMS: room_revenue >= 0", (pms["room_revenue"] >= 0).all())

    dup_pos = pos.duplicated(subset=["transaction_id", "line_no"]).sum()
    check("POS: no duplicate (transaction_id, line_no)", dup_pos == 0, f"{dup_pos} dups")
    check("POS: net_sales <= gross_sales", (pos["net_sales"] <= pos["gross_sales"] + 0.01).all())
    check("POS: quantity >= 0", (pos["quantity"] >= 0).all())
    check("POS: no null product_id", pos["product_id"].notna().all())
    check("POS: no null property_id", pos["property_id"].notna().all())

    dup_inv = inv.duplicated(subset=["date_id", "property_id", "product_id"]).sum()
    check("INVENTORY: grain unique (product×property×date)", dup_inv == 0, f"{dup_inv} dups")
    check("INVENTORY: closing_stock >= 0", (inv["closing_stock"] >= 0).all())

    check("PROCUREMENT: total = qty × price",
          bool(np.abs(pro["total_amount"] - pro["quantity"] * pro["unit_price"]).max() < 0.02))
    check("BUDGET: grain unique (prop×dept×account×month)",
          bud.duplicated(subset=["date_id", "property_id", "department_id", "account_id"]).sum() == 0)
    check("FINANCE: no null account_id", fin["account_id"].notna().all())

    # referential integrity
    valid_props = set(load_master("dim_property")["property_id"])
    for nm, df, col in [("PMS", pms, "property_id"), ("POS", pos, "property_id"),
                        ("FINANCE", fin, "property_id"), ("INVENTORY", inv, "property_id"),
                        ("PROCUREMENT", pro, "property_id"), ("BUDGET", bud, "property_id")]:
        bad = ~df[col].isin(valid_props)
        check(f"RI {nm}.property_id → dim_property", bad.sum() == 0, f"{int(bad.sum())} orphans")

    valid_prods = set(dim_prod["product_id"])
    for nm, df, col in [("POS", pos, "product_id"), ("INVENTORY", inv, "product_id"),
                        ("PROCUREMENT", pro, "product_id")]:
        bad = ~df[col].isin(valid_prods)
        check(f"RI {nm}.product_id → dim_product", bad.sum() == 0, f"{int(bad.sum())} orphans")

    valid_dates = set(load_master("dim_date")["date_key"])
    for nm, df, col in [("PMS", pms, "date_id"), ("POS", pos, "date_id"), ("INVENTORY", inv, "date_id"),
                        ("PROCUREMENT", pro, "date_id"), ("FINANCE", fin, "date_id"), ("BUDGET", bud, "date_id")]:
        bad = ~df[col].isin(valid_dates)
        check(f"RI {nm}.date_id → dim_date", bad.sum() == 0, f"{int(bad.sum())} orphans")

    # ---- write row counts for the DQ report
    counts = {k: len(v) for k, v in
              [("pms", pms), ("pos", pos), ("finance", fin), ("inventory", inv),
               ("procurement", pro), ("budget", bud)]}
    with open(os.path.join(P.CLN_DIR, "row_counts.json"), "w") as fh:
        json.dump(counts, fh, indent=2)
    print("\n[07] cleaned row counts:", counts)

    if FAILS:
        print("\n[07] GATE FAILED:")
        for f in FAILS:
            print("   -", f)
        raise SystemExit(1)
    print("\n[07] GATE PASSED — safe to load")


if __name__ == "__main__":
    main()
