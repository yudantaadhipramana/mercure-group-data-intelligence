"""
ETL 00b — MASTER DATA BUILDER.

Creates the canonical master tables (surrogate-keyed) and the alias→canonical
mapping tables, derived from the *staged* data so the mappings cover 100% of the
raw strings actually present — plus the parameterised canonical entities.

Outputs (04_master_data/, parquet):
  dim_date, dim_property, dim_business_unit, dim_department, dim_product,
  dim_product_category, dim_customer_segment, dim_channel, dim_room_type,
  dim_account, dim_supplier,
  map_property_alias, map_product_alias, map_account_code, map_category_alias
"""
from __future__ import annotations
import sys, os, re
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P


# ------------------------------------------------------------------ normalizer
def norm_key(s) -> str:
    """Aggressive canonical key: upper, strip, collapse spaces/punct. (Gacoan-style)."""
    if s is None or (isinstance(s, float) and np.isnan(s)):
        return ""
    s = str(s).upper().strip()
    s = re.sub(r"[^A-Z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


# ------------------------------------------------------------------ date dim
def build_dim_date() -> pd.DataFrame:
    rows = []
    d = P.START_DATE
    end = P.FC_END                                     # include forecast horizon
    while d <= end:
        hol = P.HOLIDAYS.get(d, "")
        lw = P.is_long_weekend(d)
        rows.append(dict(
            date_key=int(d.strftime("%Y%m%d")),
            full_date=d.isoformat(),
            year=d.year, quarter=(d.month - 1) // 3 + 1, month=d.month,
            month_name=d.strftime("%B"), day_of_week=d.weekday(),
            day_name=d.strftime("%A"), is_weekend=int(d.weekday() >= 5),
            is_holiday_flag=int(bool(hol or lw)), holiday_name=hol,
            day_of_year=d.timetuple().tm_yday, week_of_year=int(d.strftime("%W")),
        ))
        d += pd.Timedelta(days=1)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------ property dim + map
def build_property(df_pms: pd.DataFrame, df_pos: pd.DataFrame, df_fin: pd.DataFrame,
                   df_inv: pd.DataFrame, df_pro: pd.DataFrame, df_bud: pd.DataFrame):
    """Collect raw property strings from every source, map to canonical."""
    canonical = {p[0]: dict(property_id=p[0], property_name=p[1], business_type="Hotel",
                            city=p[2], region=p[3], rooms=p[4], cls=p[5]) for p in P.PROPERTIES}
    canonical.update({u[0]: dict(property_id=u[0], property_name=u[1], business_type="F&B",
                                 city=u[2], region="Java", rooms=None, cls="F&B") for u in P.FNB_UNITS})

    # alias seeds keyed by NORMALIZED string (case-insensitive lookup)
    alias_map: dict[str, str] = {}
    for pid_, name, city, *_ in P.PROPERTIES:
        for a in [name, P.NAME_SHORT.get(name, name), f"MG {city}",
                  name.replace(" ", "-"), f"MG {P.CITY_SHORT[city]}"]:
            alias_map[norm_key(a)] = pid_
        alias_map[norm_key(name.split()[-1])] = pid_      # last token, e.g. "JAKARTA"
    for uid_, name, city, *_ in P.FNB_UNITS:
        for a in [name, name.replace(" ", "-"), f"MG {city}"]:
            alias_map[norm_key(a)] = uid_
        alias_map[norm_key(name.split()[-1])] = uid_

    frames = [df_pms, df_pos, df_fin, df_inv, df_pro, df_bud]
    observed = set()
    for df in frames:
        if df is not None and "property" in df.columns:
            observed |= set(df["property"].dropna().unique())

    unmapped = []
    for raw in sorted(observed):
        k = norm_key(raw)
        pid = alias_map.get(k)
        if pid is None:
            # city-token containment match (e.g. "MERCURE GRAND BDG" ⊃ "BDG")
            for cid, cv in canonical.items():
                ck = norm_key(cv["city"])
                if ck and (ck in k or ck.replace(" ", "") in k.replace(" ", "")):
                    pid = cid
                    break
        if pid is None:
            unmapped.append(raw)
        else:
            alias_map[raw] = pid          # keep the raw spelling as a mapping key too

    dim = pd.DataFrame([dict(property_id=k, property_name=v["property_name"],
                             business_type=v["business_type"], city=v["city"], region=v["region"],
                             rooms=v["rooms"], property_class=v["cls"])
                        for k, v in canonical.items()])
    mp = pd.DataFrame([{"raw_alias": a, "property_id": i} for a, i in sorted(alias_map.items())])
    return dim, mp, sorted(observed), unmapped


# ------------------------------------------------------------------ product dim + map
def build_product(df_pos: pd.DataFrame, df_inv: pd.DataFrame):
    canonical = []
    for i, (cat, name, price, cost) in enumerate(P.MENU, start=1):
        canonical.append(dict(product_id=f"P{i:03d}", product_name=name,
                              category_id=f"C{P.CATEGORIES.index(cat)+1:03d}",
                              category=cat, base_price=float(price), unit_cost_ratio=float(cost)))
    by_key = {norm_key(c["product_name"]): c["product_id"] for c in canonical}
    cat_by_key = {norm_key(c["product_name"]): c["category"] for c in canonical}

    frames = [df for df in [df_pos, df_inv] if df is not None]
    observed = set()
    for df in frames:
        if "product_name" in df.columns:
            observed |= set(df["product_name"].dropna().unique())

    alias_map: dict[str, str] = {}
    unmapped = []
    for raw in sorted(observed):
        k = norm_key(raw)
        pid = by_key.get(k)
        if pid is None:
            # token-overlap fallback: canonical name tokens ⊆ alias tokens
            toks = set(k.split())
            best, best_n = None, 0
            for ck, cid in by_key.items():
                n = len(set(ck.split()) & toks)
                if n > best_n:
                    best, best_n = cid, n
            if best and best_n >= 2:
                pid = best
        if pid is None:
            unmapped.append(raw)
        else:
            alias_map[raw] = pid

    dim = pd.DataFrame(canonical)
    mp = pd.DataFrame([{"raw_alias": a, "product_id": i} for a, i in sorted(alias_map.items())])
    return dim, mp, sorted(observed), unmapped


# ------------------------------------------------------------------ account / category maps
def build_account():
    rows = [dict(account_id=f"A{c}", account_code=c, account_name=n,
                 account_type=t, department_id=d)
            for c, n, t, d in P.ACCOUNTS]
    return pd.DataFrame(rows)


def build_maps(df_fin: pd.DataFrame, df_pos: pd.DataFrame):
    acc = build_account()
    by_name = {norm_key(r.account_name): r.account_id for r in acc.itertuples()}
    by_code = {r.account_code: r.account_id for r in acc.itertuples()}
    amap: dict[str, str] = {}
    if df_fin is not None and "account_name" in df_fin.columns:
        for raw in sorted(df_fin["account_name"].dropna().unique()):
            k = norm_key(raw)
            aid = by_name.get(k)
            if aid is None:
                # token overlap on canonical account names
                toks = set(k.split())
                best, best_n = None, 0
                for ck, cid in by_name.items():
                    n = len(set(ck.split()) & toks)
                    if n > best_n:
                        best, best_n = cid, n
                if best and best_n >= 1:
                    aid = best
            if aid:
                amap[raw] = aid
    code_map = {c: i for c, i in by_code.items()}

    cats = [dict(category_id=f"C{i+1:03d}", category_name=c) for i, c in enumerate(P.CATEGORIES)]
    cby = {norm_key(c["category_name"]): c["category_id"] for c in cats}
    cmap: dict[str, str] = {}
    if df_pos is not None and "category" in df_pos.columns:
        for raw in sorted(df_pos["category"].dropna().unique()):
            k = norm_key(raw)
            if k in cby:
                cmap[raw] = cby[k]
    return (acc, pd.DataFrame(cats),
            pd.DataFrame([{"raw_alias": a, "account_id": i} for a, i in amap.items()]),
            pd.DataFrame([{"raw_alias": a, "category_id": i} for a, i in cmap.items()]),
            code_map)


# ------------------------------------------------------------------ small dims
def build_small():
    bu = pd.DataFrame([dict(business_unit_id=i, business_unit_name=n, business_type=t)
                       for i, n, t in P.BUSINESS_UNITS])
    dep = pd.DataFrame([dict(department_id=i, department_name=n) for i, n in P.DEPARTMENTS])
    seg = pd.DataFrame([dict(segment_id=f"SG{i+1:02d}", segment_name=s) for i, s in enumerate(P.SEGMENTS)])
    ch = pd.DataFrame([dict(channel_id=f"CH{i+1:02d}", channel_name=c) for i, c in enumerate(P.CHANNELS)])
    rt = pd.DataFrame([dict(room_type_id=i, room_type_name=n, price_multiplier=m)
                       for i, n, m in P.ROOM_TYPES])
    sup = pd.DataFrame([dict(supplier_id=i, supplier_name=n, city=c, lead_time_days=l,
                             payment_terms_days=p) for i, n, c, l, p in P.SUPPLIERS])
    return bu, dep, seg, ch, rt, sup


# ------------------------------------------------------------------ main
def main():
    os.makedirs(P.MST_DIR, exist_ok=True)

    def load(n):
        p = os.path.join(P.STG_DIR, f"stg_{n}.parquet")
        return pd.read_parquet(p) if os.path.exists(p) else None

    pms, pos, fin, inv, pro, bud = (load("pms"), load("pos"), load("finance"),
                                    load("inventory"), load("procurement"), load("budget"))

    print("[M] dim_date ...", flush=True)
    build_dim_date().to_parquet(os.path.join(P.MST_DIR, "dim_date.parquet"), index=False)

    print("[M] property ...", flush=True)
    dim_p, map_p, obs, unm = build_property(pms, pos, fin, inv, pro, bud)
    dim_p.to_parquet(os.path.join(P.MST_DIR, "dim_property.parquet"), index=False)
    map_p.to_parquet(os.path.join(P.MST_DIR, "map_property_alias.parquet"), index=False)
    print(f"[M]   observed {len(obs)} property strings · mapped {len(map_p)} · unmapped {len(unm)}: {unm[:8]}")

    print("[M] product ...", flush=True)
    dim_pr, map_pr, obs2, unm2 = build_product(pos, inv)
    dim_pr.to_parquet(os.path.join(P.MST_DIR, "dim_product.parquet"), index=False)
    map_pr.to_parquet(os.path.join(P.MST_DIR, "map_product_alias.parquet"), index=False)
    print(f"[M]   observed {len(obs2)} product strings · mapped {len(map_pr)} · unmapped {len(unm2)}: {unm2[:8]}")

    print("[M] account/category ...", flush=True)
    acc, cat, map_a, map_c, code_map = build_maps(fin, pos)
    acc.to_parquet(os.path.join(P.MST_DIR, "dim_account.parquet"), index=False)
    cat.to_parquet(os.path.join(P.MST_DIR, "dim_product_category.parquet"), index=False)
    map_a.to_parquet(os.path.join(P.MST_DIR, "map_account_alias.parquet"), index=False)
    map_c.to_parquet(os.path.join(P.MST_DIR, "map_category_alias.parquet"), index=False)

    print("[M] small dims ...", flush=True)
    bu, dep, seg, ch, rt, sup = build_small()
    for nm, d in [("dim_business_unit", bu), ("dim_department", dep), ("dim_customer_segment", seg),
                  ("dim_channel", ch), ("dim_room_type", rt), ("dim_supplier", sup)]:
        d.to_parquet(os.path.join(P.MST_DIR, f"{nm}.parquet"), index=False)

    print("[M] DONE")


if __name__ == "__main__":
    main()
