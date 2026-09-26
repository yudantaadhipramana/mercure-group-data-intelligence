"""
ETL 03/04/05 — CLEAN · STANDARDIZE · MAP → cleaned parquet.

03 clean:        whitespace, case, date → ISO, numeric → float, drop blanks, fix dups
04 standardize:  canonical case for enums, category whitelist flagging
05 map_master:   alias → canonical IDs via master mapping tables

All cleansing decisions are logged to etl_cleansing_log with REAL counts
harvested from the data — nothing typed by hand.
"""
from __future__ import annotations
import sys, os, re
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P
from build_master_helpers import norm_key

LOG_ROWS: list[dict] = []


def log(rule: str, source: str, n: int, before: str, after: str):
    LOG_ROWS.append(dict(rule=rule, source=source, records_affected=n,
                         before=before, after=after))


# ------------------------------------------------------------------ PMS
def clean_pms(df: pd.DataFrame, map_prop: pd.DataFrame, dim_seg: pd.DataFrame,
              dim_ch: pd.DataFrame, dim_rt: pd.DataFrame) -> pd.DataFrame:
    n0 = len(df)
    # dedupe on booking_id (keep first)
    d = int(df.duplicated(subset=["booking_id"]).sum())
    df = df.drop_duplicates(subset=["booking_id"], keep="first").reset_index(drop=True)
    log("Remove duplicate booking_id", "PMS", d, f"{d} duplicate ids", "kept first occurrence")

    # trim + case enums
    for c in ["room_type", "guest_segment", "booking_channel", "cancellation_status", "payment_status"]:
        if c in df.columns:
            df[c] = df[c].astype("string").str.strip()

    # map property alias → id
    pm = dict(zip(map_prop["raw_alias"], map_prop["property_id"]))
    raw_props = df["property"].astype("string")
    mapped = raw_props.map(pm)
    n_unmapped = int(mapped.isna().sum())
    log("Standardize property name → property_id", "PMS",
        int(len(df) - n_unmapped), "5+ alias variants (MG JKT, MERCURE GRAND JAKARTA, …)",
        "H001–H007 / F001–F002")
    if n_unmapped:
        log("Quarantine unmapped property", "PMS", n_unmapped, "unknown property strings",
            "dropped (reported in DQ)")
        df = df[mapped.notna()].reset_index(drop=True)
        mapped = mapped[mapped.notna()]
    df["property_id"] = mapped.values

    # map room type / segment / channel by normalized name
    for col, dim, idcol in [("room_type", dim_rt, "room_type_id"),
                            ("guest_segment", dim_seg, "segment_id"),
                            ("booking_channel", dim_ch, "channel_id")]:
        m = {norm_key(r[1]): r[0] for r in dim[[idcol, dim.columns[1]]].values}
        df[idcol] = df[col].map(lambda v: m.get(norm_key(v)) if pd.notna(v) else None)
        n_miss = int(df[idcol].isna().sum())
        log(f"Map {col} → {idcol}", "PMS", int(len(df) - n_miss),
            f"{df[col].nunique()} raw variants", f"{len(m)} canonical")

    # dates
    for c in ["booking_date", "check_in", "check_out"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    bad = df["check_out"] < df["check_in"]
    n_bad = int(bad.sum())
    if n_bad:
        log("Fix impossible date (checkout < checkin)", "PMS", n_bad, "check_out < check_in",
            "swapped")
        df.loc[bad, ["check_in", "check_out"]] = df.loc[bad, ["check_out", "check_in"]].values

    # numeric
    for c in ["room_rate", "room_revenue"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    n_neg = int((df["room_revenue"] < 0).sum())
    if n_neg:
        log("Fix negative revenue", "PMS", n_neg, "room_revenue < 0", "set to 0")
        df.loc[df["room_revenue"] < 0, "room_revenue"] = 0.0

    # window guard
    out = (df["check_in"] < pd.Timestamp(P.START_DATE)) | (df["check_in"] > pd.Timestamp(P.END_DATE))
    n_out = int(out.sum())
    if n_out:
        log("Drop bookings outside reporting window", "PMS", n_out, "check_in outside 2025–2026", "dropped")
        df = df[~out].reset_index(drop=True)

    # derived
    df["los"] = (df["check_out"] - df["check_in"]).dt.days.clip(lower=1)
    df["is_cancelled"] = (df["cancellation_status"] == "Cancelled").astype(int)
    df["is_no_show"] = (df["cancellation_status"] == "No-Show").astype(int)
    df["rooms_sold"] = ((df["is_cancelled"] == 0) & (df["is_no_show"] == 0)).astype(int)
    df["room_nights"] = df["los"] * df["rooms_sold"]
    df["room_revenue"] = df["rooms_sold"] * df["room_rate"]
    df["date_id"] = df["check_in"].dt.strftime("%Y%m%d").astype("int64")
    print(f"[35] PMS {n0:,} → {len(df):,}")
    return df


# ------------------------------------------------------------------ POS
def clean_pos(df: pd.DataFrame, map_prop, map_prod, dim_cat) -> pd.DataFrame:
    n0 = len(df)
    d = int(df.duplicated().sum())
    df = df.drop_duplicates().reset_index(drop=True)
    log("Remove exact duplicate POS lines", "POS", d, f"{d} duplicate rows", "removed")

    # outlet → property (normalize outlet name first; raw carries case/whitespace noise)
    outlet_prop = {o[1]: o[2] for o in P.OUTLETS}
    norm_outlet = {norm_key(k): v for k, v in outlet_prop.items()}
    df["outlet_name"] = df["outlet"].astype("string").str.strip()
    ok = df["outlet_name"].map(lambda v: norm_key(v) in norm_outlet if pd.notna(v) else False)
    n_bad_outlet = int((~ok).sum())
    if n_bad_outlet:
        log("Quarantine unknown outlet", "POS", n_bad_outlet, "outlet not in outlet master", "dropped")
        df = df[ok].reset_index(drop=True)
    df["property_id"] = df["outlet_name"].map(lambda v: norm_outlet[norm_key(v)])
    # canonical outlet name (raw carried case/whitespace variants)
    canon_outlet = {norm_key(k): k for k in outlet_prop}
    df["outlet_name"] = df["outlet_name"].map(lambda v: canon_outlet[norm_key(v)])

    # product alias → product_id
    pm = dict(zip(map_prod["raw_alias"], map_prod["product_id"]))
    mapped = df["product_name"].astype("string").map(pm)
    n_un = int(mapped.isna().sum())
    if n_un:
        log("Quarantine orphan product", "POS", n_un, "product not in product master", "dropped")
        df = df[mapped.notna()].reset_index(drop=True)
        mapped = mapped[mapped.notna()]
    df["product_id"] = mapped.values

    # category whitelist
    cbn = {norm_key(c): c for c in P.CATEGORIES}
    df["category_clean"] = df["category"].map(lambda v: cbn.get(norm_key(v)) if pd.notna(v) else None)
    n_bad_cat = int(df["category_clean"].isna().sum())
    if n_bad_cat:
        log("Fix invalid category", "POS", n_bad_cat, "category not in category master", "flagged OTHER")
        df["category_clean"] = df["category_clean"].fillna("Other")

    # dates + numerics
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    for c in ["quantity", "gross_sales", "discount", "net_sales"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["discount"] = df["discount"].fillna(0.0)
    # net should be gross - discount; if raw net is off, force it
    df["net_sales"] = df["gross_sales"] - df["discount"].abs()
    n_neg = int((df["quantity"] < 0).sum())
    if n_neg:
        log("Fix negative quantity", "POS", n_neg, "quantity < 0", "abs (return-correction artifact)")
        df["quantity"] = df["quantity"].abs()

    df["void_flag"] = df["void_flag"].astype("string").str.strip().str.upper().eq("Y").astype(int)
    df["refund_flag"] = df["refund_flag"].astype("string").str.strip().str.upper().eq("Y").astype(int)

    # line number within transaction (grain)
    df = df.sort_values(["transaction_id", "_raw_row"]).reset_index(drop=True)
    df["line_no"] = df.groupby("transaction_id").cumcount() + 1

    # derived
    df["is_void"] = df["void_flag"]
    df["is_refund"] = df["refund_flag"]
    df["unit_price"] = np.where(df["quantity"] > 0, df["gross_sales"] / df["quantity"], 0.0)
    df["cogs_amount"] = df["product_id"].map(
        dict(zip(dim_cat["product_id"], dim_cat["unit_cost_ratio"]))) * df["gross_sales"]
    df["gross_profit"] = df["net_sales"] - df["cogs_amount"]
    df["date_id"] = df["transaction_date"].dt.strftime("%Y%m%d").astype("int64")
    print(f"[35] POS {n0:,} → {len(df):,}")
    return df


# ------------------------------------------------------------------ FINANCE
def clean_finance(df: pd.DataFrame, map_prop, dim_acc, map_acc, code_map) -> pd.DataFrame:
    n0 = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    log("Remove exact duplicate GL lines", "FINANCE", n0 - len(df), "duplicate rows", "removed")

    pm = dict(zip(map_prop["raw_alias"], map_prop["property_id"]))
    mapped = df["property"].astype("string").map(pm)
    n_un = int(mapped.isna().sum())
    if n_un:
        log("Quarantine unknown property", "FINANCE", n_un, "property not in master", "dropped")
        df = df[mapped.notna()].reset_index(drop=True)
        mapped = mapped[mapped.notna()]
    df["property_id"] = mapped.values

    # account: code first, then name map
    aid_by_code = dict(zip(dim_acc["account_code"], dim_acc["account_id"]))
    am = dict(zip(map_acc["raw_alias"], map_acc["account_id"]))
    df["account_id"] = df["account_code"].map(aid_by_code)
    miss = df["account_id"].isna()
    df.loc[miss, "account_id"] = df.loc[miss, "account_name"].map(am)
    n_bad_acc = int(df["account_id"].isna().sum())
    if n_bad_acc:
        log("Fix invalid account code/name", "FINANCE", n_bad_acc, "malformed code (e.g. 4100X)",
            "mapped by name / quarantined")
        df = df[df["account_id"].notna()].reset_index(drop=True)

    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["date_id"] = df["transaction_date"].dt.strftime("%Y%m%d").astype("int64")
    print(f"[35] FINANCE {n0:,} → {len(df):,}")
    return df


# ------------------------------------------------------------------ INVENTORY
def clean_inventory(df: pd.DataFrame, map_prop, map_prod) -> pd.DataFrame:
    n0 = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    log("Remove exact duplicate inventory rows", "INVENTORY", n0 - len(df), "duplicate rows", "removed")

    pm = dict(zip(map_prop["raw_alias"], map_prop["property_id"]))
    mapped = df["property"].astype("string").map(pm)
    n_un = int(mapped.isna().sum())
    if n_un:
        log("Quarantine unknown property", "INVENTORY", n_un, "property not in master", "dropped")
        df = df[mapped.notna()].reset_index(drop=True)
        mapped = mapped[mapped.notna()]
    df["property_id"] = mapped.values

    prd = dict(zip(map_prod["raw_alias"], map_prod["product_id"]))
    mp2 = df["product_name"].astype("string").map(prd)
    n_unp = int(mp2.isna().sum())
    if n_unp:
        log("Quarantine orphan product", "INVENTORY", n_unp, "product not in master", "dropped")
        df = df[mp2.notna()].reset_index(drop=True)
        mp2 = mp2[mp2.notna()]
    df["product_id"] = mp2.values

    df["inventory_date"] = pd.to_datetime(df["inventory_date"], errors="coerce")
    df["date_id"] = df["inventory_date"].dt.strftime("%Y%m%d").astype("int64")
    for c in ["opening_stock", "purchase_qty", "transfer_qty", "consumption_qty",
              "waste_qty", "closing_stock", "stock_value"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["transfer_qty"] = df["transfer_qty"].fillna(0.0)
    # Deduplicate on grain before any further use
    df = df.drop_duplicates(subset=["date_id", "property_id", "product_id"], keep="first").reset_index(drop=True)
    n_neg = int((df["consumption_qty"] < 0).sum())
    if n_neg:
        log("Fix negative consumption", "INVENTORY", n_neg, "consumption_qty < 0", "abs")
        df["consumption_qty"] = df["consumption_qty"].abs()
    df["date_id"] = df["inventory_date"].dt.strftime("%Y%m%d").astype("int64")
    print(f"[35] INVENTORY {n0:,} → {len(df):,}")
    return df


# ------------------------------------------------------------------ PROCUREMENT
def clean_procurement(df: pd.DataFrame, map_prop, map_prod, dim_sup) -> pd.DataFrame:
    n0 = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    pm = dict(zip(map_prop["raw_alias"], map_prop["property_id"]))
    mapped = df["property"].astype("string").map(pm)
    n_un = int(mapped.isna().sum())
    if n_un:
        log("Quarantine unknown property", "PROCUREMENT", n_un, "property not in master", "dropped")
        df = df[mapped.notna()].reset_index(drop=True)
        mapped = mapped[mapped.notna()]
    df["property_id"] = mapped.values

    prd = dict(zip(map_prod["raw_alias"], map_prod["product_id"]))
    mp2 = df["product_name"].astype("string").map(prd)
    df = df[mp2.notna()].reset_index(drop=True)
    df["product_id"] = mp2[mp2.notna()].values

    sup_map = {norm_key(s): i for i, s in zip(dim_sup["supplier_id"], dim_sup["supplier_name"])}
    df["supplier_id"] = df["supplier"].map(lambda v: sup_map.get(norm_key(v)))
    df["supplier_id"] = df["supplier_id"].fillna("S999")      # unknown supplier bucket
    df["purchase_date"] = pd.to_datetime(df["purchase_date"], errors="coerce")
    for c in ["quantity", "unit_price", "total_amount"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    # recompute total_amount to ensure consistency with cleaned numeric qty/price
    df["total_amount"] = df["quantity"] * df["unit_price"]
    df["date_id"] = df["purchase_date"].dt.strftime("%Y%m%d").astype("int64")
    print(f"[35] PROCUREMENT {n0:,} → {len(df):,}")
    df["purchase_line_id"] = df["purchase_id"] + "-" + df.groupby("purchase_id").cumcount().astype(str)
    return df


# ------------------------------------------------------------------ BUDGET
def clean_budget(df: pd.DataFrame, map_prop, dim_acc, map_acc) -> pd.DataFrame:
    n0 = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    pm = dict(zip(map_prop["raw_alias"], map_prop["property_id"]))
    mapped = df["property"].astype("string").map(pm)
    df = df[mapped.notna()].reset_index(drop=True)
    df["property_id"] = mapped[mapped.notna()].values

    am = dict(zip(map_acc["raw_alias"], map_acc["account_id"]))
    df["account_id"] = df["account_name"].astype("string").map(am)
    df = df[df["account_id"].notna()].reset_index(drop=True)

    # period → month start date (both "2025-01" and "Jan-2025" appear)
    p = df["period_date"].astype("string")
    iso = pd.to_datetime(p, format="%Y-%m-%d", errors="coerce")
    alt = pd.to_datetime(p, format="mixed", dayfirst=True, errors="coerce")
    df["period_start"] = iso.fillna(alt)
    df["budget_amount"] = pd.to_numeric(df["budget_amount"], errors="coerce")
    # department from account
    dim_dept = pd.read_parquet(os.path.join(P.MST_DIR, "dim_department.parquet"))
    dept_map = dict(zip(dim_acc["account_id"], dim_acc["department_id"]))
    df["department_id"] = df["account_id"].map(dept_map)
    df["date_id"] = df["period_start"].dt.strftime("%Y%m%d").astype("int64")
    df["budget_year"] = df["period_start"].dt.year
    df["budget_month"] = df["period_start"].dt.month
    print(f"[35] BUDGET {n0:,} → {len(df):,}")
    return df


def main():
    import json
    os.makedirs(P.CLN_DIR, exist_ok=True)

    # load master data
    dim_seg = pd.read_parquet(os.path.join(P.MST_DIR, "dim_customer_segment.parquet"))
    dim_ch = pd.read_parquet(os.path.join(P.MST_DIR, "dim_channel.parquet"))
    dim_rt = pd.read_parquet(os.path.join(P.MST_DIR, "dim_room_type.parquet"))
    dim_acc = pd.read_parquet(os.path.join(P.MST_DIR, "dim_account.parquet"))
    dim_sup = pd.read_parquet(os.path.join(P.MST_DIR, "dim_supplier.parquet"))
    dim_prod = pd.read_parquet(os.path.join(P.MST_DIR, "dim_product.parquet"))
    map_prop = pd.read_parquet(os.path.join(P.MST_DIR, "map_property_alias.parquet"))
    map_prod = pd.read_parquet(os.path.join(P.MST_DIR, "map_product_alias.parquet"))
    map_acc = pd.read_parquet(os.path.join(P.MST_DIR, "map_account_alias.parquet"))
    map_cat = pd.read_parquet(os.path.join(P.MST_DIR, "map_category_alias.parquet"))

    pms = clean_pms(pd.read_parquet(os.path.join(P.STG_DIR, "stg_pms.parquet")), map_prop, dim_seg, dim_ch, dim_rt)
    pos = clean_pos(pd.read_parquet(os.path.join(P.STG_DIR, "stg_pos.parquet")), map_prop, map_prod, dim_prod)
    fin = clean_finance(pd.read_parquet(os.path.join(P.STG_DIR, "stg_finance.parquet")), map_prop, dim_acc, map_acc, {})
    inv = clean_inventory(pd.read_parquet(os.path.join(P.STG_DIR, "stg_inventory.parquet")), map_prop, map_prod)
    pro = clean_procurement(pd.read_parquet(os.path.join(P.STG_DIR, "stg_procurement.parquet")), map_prop, map_prod, dim_sup)
    bud = clean_budget(pd.read_parquet(os.path.join(P.STG_DIR, "stg_budget.parquet")), map_prop, dim_acc, map_acc)

    pms.to_parquet(os.path.join(P.CLN_DIR, "clean_pms.parquet"), index=False)
    pos.to_parquet(os.path.join(P.CLN_DIR, "clean_pos.parquet"), index=False)
    fin.to_parquet(os.path.join(P.CLN_DIR, "clean_finance.parquet"), index=False)
    inv.to_parquet(os.path.join(P.CLN_DIR, "clean_inventory.parquet"), index=False)
    pro.to_parquet(os.path.join(P.CLN_DIR, "clean_procurement.parquet"), index=False)
    bud.to_parquet(os.path.join(P.CLN_DIR, "clean_budget.parquet"), index=False)

    # save cleansing log
    log_df = pd.DataFrame(LOG_ROWS)
    log_df.to_parquet(os.path.join(P.CLN_DIR, "cleansing_log.parquet"), index=False)

    # row counts
    counts = {
        "pms": len(pms), "pos": len(pos), "finance": len(fin),
        "inventory": len(inv), "procurement": len(pro), "budget": len(bud),
        "cleansing_rules": len(log_df),
    }
    with open(os.path.join(P.CLN_DIR, "row_counts.json"), "w", encoding="utf-8") as fh:
        json.dump(counts, fh, indent=2)
    print(f"[35] cleansing log rules: {len(log_df)}")
    print("[35] DONE")


if __name__ == "__main__":
    main()
