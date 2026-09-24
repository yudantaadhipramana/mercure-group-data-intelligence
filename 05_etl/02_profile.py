"""
ETL 02 — PROFILE: profile every staged source.

Output: 02_staging/profile.json — row counts, columns, types, missingness,
duplicates, distinct counts, numeric summaries, and a "dirty findings" inventory
(the concrete problems the cleansing stage must fix).
Nothing here repairs anything — profiling measures first.
"""
from __future__ import annotations
import sys, os, json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P

SOURCES = ["pms", "pos", "finance", "inventory", "procurement", "budget"]


def profile_one(name: str, df: pd.DataFrame) -> dict:
    cols = [c for c in df.columns if not c.startswith("_")]
    out = {
        "source": name,
        "rows": int(len(df)),
        "columns": len(cols),
        "column_names": cols,
        "missing": {},
        "missing_pct": {},
        "distinct": {},
        "duplicate_rows": int(df.duplicated(subset=cols).sum()),
        "numeric_summary": {},
        "dirty_findings": [],
    }
    for c in cols:
        s = df[c]
        out["missing"][c] = int(s.isna().sum())
        out["missing_pct"][c] = round(float(s.isna().mean() * 100), 2)
        out["distinct"][c] = int(s.nunique(dropna=True))
        if pd.api.types.is_numeric_dtype(s):
            out["numeric_summary"][c] = {
                k: (None if pd.isna(v) else float(v))
                for k, v in s.describe().items()
            }
    f = out["dirty_findings"]
    # --- property / string cardinality anomalies
    if "property" in df:
        n = df["property"].nunique(dropna=True)
        if n > 12:
            f.append({"rule": "PROPERTY_ALIAS", "detail": f"{n} distinct property strings (expected ≤11)",
                      "records_affected": int(len(df))})
    if "product_name" in df:
        n = df["product_name"].nunique(dropna=True)
        if n > 70:
            f.append({"rule": "PRODUCT_ALIAS", "detail": f"{n} distinct product strings (expected ≤60)",
                      "records_affected": int(len(df))})
    if "category" in df:
        bad = set(df["category"].dropna().unique()) - set(P.CATEGORIES) - {"INVALID_CAT"}
        if bad:
            f.append({"rule": "INVALID_CATEGORY", "values": sorted(bad)[:10],
                      "records_affected": int(df["category"].isin(bad).sum())})
    # --- duplicates on ids
    for idc in (["booking_id"], ["transaction_id"], ["purchase_id"]):
        if all(c in df.columns for c in idc):
            d = int(df.duplicated(subset=idc).sum())
            if d:
                f.append({"rule": "DUPLICATE_ID", "key": idc[0], "records_affected": d})
    # --- numeric problems
    for c, rule in [("quantity", "NEGATIVE_QTY"), ("consumption_qty", "NEGATIVE_QTY"),
                    ("net_sales", "NEGATIVE_AMOUNT")]:
        if c in df and pd.api.types.is_numeric_dtype(df[c]):
            n = int((df[c] < 0).sum())
            if n:
                f.append({"rule": rule, "column": c, "records_affected": n})
    # --- date problems
    for c in ["check_in", "check_out", "transaction_date", "inventory_date", "purchase_date"]:
        if c in df:
            n = int(df[c].isna().sum())
            if n:
                f.append({"rule": "UNPARSABLE_DATE", "column": c, "records_affected": n})
    if "check_in" in df and "check_out" in df:
        ci = pd.to_datetime(df["check_in"], errors="coerce")
        co = pd.to_datetime(df["check_out"], errors="coerce")
        n = int((co < ci).sum())
        if n:
            f.append({"rule": "CHECKOUT_BEFORE_CHECKIN", "records_affected": n})
    return out


def main():
    prof = {}
    for name in SOURCES:
        p = os.path.join(P.STG_DIR, f"stg_{name}.parquet")
        if not os.path.exists(p):
            print(f"[02] missing {p} — skipping")
            continue
        df = pd.read_parquet(p)
        prof[name] = profile_one(name, df)
        print(f"[02] profile {name}: {len(df):,} rows · {prof[name]['duplicate_rows']:,} dup rows · "
              f"{len(prof[name]['dirty_findings'])} finding classes", flush=True)
    out = os.path.join(P.STG_DIR, "profile.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(prof, fh, indent=2)
    print(f"[02] → {out}")
    print("[02] DONE")


if __name__ == "__main__":
    main()
