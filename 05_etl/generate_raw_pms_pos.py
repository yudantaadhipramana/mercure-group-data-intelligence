"""
PHASE 5 — Synthetic raw data generation: PMS (hotel bookings) + POS (F&B lines).

Business logic (not random noise):
  demand(date) = DOW × month × long-weekend × year-uplift
  bookings ~ Poisson(property base occupancy × rooms × demand / avg LOS)
  room_rate = base ADR × room-type multiplier × demand
  room_revenue = rooms_sold × rate
  F&B covers tied to occupancy (hotel F&B demand-linked) + weekend/holiday
  net_sales = gross − discount − void − refund
Deliberately dirty output: aliases, mixed dates, mixed decimals, whitespace,
case noise, blank rows, nulls, duplicates, invalid codes, orphans.
"""
from __future__ import annotations
import sys, os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P
from raw_writers import fmt_date, fmt_num, messy, maybe_null, blank_row

OUT_PMS = P.RAW_DIRS["pms"]
OUT_POS = P.RAW_DIRS["pos"]

# ============================================================ PMS
def generate_pms() -> pd.DataFrame:
    r = P.rng(101)
    rows = []
    seq = 0
    for d in P.daterange():
        f = P.date_factors(d)
        for pid, name, city, region, rooms, cls, base_occ, base_adr in P.PROPERTIES:
            occ_target = min(0.97, base_occ * f)
            # arrivals this night ∝ occupancy × rooms / avg LOS
            lam = occ_target * rooms / 3.2 * P.POC_BOOKING_RATE
            n = r.poisson(lam)
            if n == 0:
                continue
            for _ in range(n):
                seq += 1
                seg = r.choice(P.SEGMENTS, p=list(P.SEGMENT_WEIGHT.values()))
                ch = r.choice(P.CHANNELS, p=list(P.CHANNEL_WEIGHT.values()))
                rt, rt_name, rt_mult = P.ROOM_TYPES[
                    r.choice(len(P.ROOM_TYPES), p=P.ROOM_TYPE_WEIGHT)]
                los = int(r.integers(1, 7))
                rate = base_adr * 1000 * rt_mult * (0.92 + 0.16 * f)
                rate = float(np.round(rate / 1000) * 1000)
                cx = r.random() < P.SEGMENT_CANX[seg]
                ns = (not cx) and r.random() < P.SEGMENT_NOSHOW[seg]
                status = "Cancelled" if cx else ("No-Show" if ns else "Confirmed")
                pay = r.choice(["Paid", "Unpaid", "Partial"],
                               p=[0.78, 0.12, 0.10]) if status == "Confirmed" else "Unpaid"
                rooms_sold = 0 if status != "Confirmed" else 1
                rev = rooms_sold * rate
                # dirty: alias property name
                alias = r.choice(property_aliases(pid))
                # dirty: impossible dates (check_out before check_in) occasionally
                ci, co = d, d + pd.Timedelta(days=los)
                if r.random() < P.P_BAD_DATE:
                    ci, co = co, ci
                # dirty: date outside the window
                if r.random() < P.P_BAD_DATE * 0.6:
                    ci = ci + pd.Timedelta(days=int(r.integers(-40, 40)))
                    co = ci + pd.Timedelta(days=los)
                seq += 0
                rows.append(dict(
                    booking_id=f"BK{seq:07d}",
                    property=messy(alias, r),
                    booking_date=fmt_date(d, r),
                    check_in=fmt_date(ci, r),
                    check_out=fmt_date(co, r),
                    room_type=messy(rt_name, r) if r.random() < 0.5 else rt_name,
                    guest_segment="" if maybe_null(r) else messy(seg, r),
                    booking_channel="" if maybe_null(r) else messy(ch, r),
                    room_rate=fmt_num(rate, r, 0),
                    room_revenue=fmt_num(rev, r, 0),
                    cancellation_status=status,
                    payment_status=pay,
                ))
                # dirty: duplicate booking id
                if r.random() < P.P_DUP_TXN * 4:
                    rows.append(dict(rows[-1]))
    df = pd.DataFrame(rows)
    # dirty: stray blank column + a few fully blank rows
    df["prop_code"] = ""
    ncols = len(df.columns)
    blanks = pd.DataFrame(np.full((12, ncols), None, dtype=object), columns=df.columns)
    df = pd.concat([df, blanks], ignore_index=True)
    return df


def property_aliases(pid: str) -> list[str]:
    for pid_, name, city, *_ in P.PROPERTIES:
        if pid_ == pid:
            short = P.NAME_SHORT.get(name, name)
            up = name.upper()
            dash = name.replace(" ", "-")
            mg = f"MG {city}"
            return [name, up, short, f"MG {P.CITY_SHORT[city]}", dash, mg]
    return [pid]


# ============================================================ POS
def generate_pos() -> pd.DataFrame:
    r = P.rng(202)
    rows = []
    seq = 0
    # menu index by category
    by_cat: dict[str, list] = {}
    for i, (cat, name, price, cost) in enumerate(P.MENU):
        by_cat.setdefault(cat, []).append((i, name, price, cost))
    outlet_props = {o[0]: o[2] for o in P.OUTLETS}       # outlet -> property id
    outlet_types = {o[0]: o[4] for o in P.OUTLETS}
    outlet_covers = {o[0]: o[5] for o in P.OUTLETS}

    for d in P.daterange():
        f = P.date_factors(d)
        for oid, oname, pid, bu, otype, covers in P.OUTLETS:
            if pid not in property_ids():
                continue
            # hotel outlets are demand-linked to that property's occupancy
            if pid.startswith("H"):
                base_occ = dict((p[0], p[6]) for p in P.PROPERTIES)[pid]
                occ = min(0.97, base_occ * f)
                c = covers * f * (0.55 + 0.45 * occ) * P.POC_COVER_RATE
            else:
                c = covers * f * P.POC_COVER_RATE
            n_tx = max(0, r.poisson(c))
            for _ in range(n_tx):
                seq += 1
                tid = f"TR{seq:08d}"
                n_lines = int(r.integers(1, 5))
                mix = P.OUTLET_TYPE_MIX[otype]
                cats = list(mix.keys())
                w = np.array([mix[c] for c in cats], dtype=float)
                w /= w.sum()
                for ln in range(1, n_lines + 1):
                    cat = r.choice(cats, p=w)
                    mi, name, price, cost = by_cat[cat][r.integers(0, len(by_cat[cat]))]
                    qty = int(max(1, r.integers(1, 4)))
                    if r.random() < P.P_NEG_QTY * 3:
                        qty = -qty
                    gross = price * qty
                    disc = gross * (P.DISCOUNT_RATE * (0.5 + r.random())) if r.random() < 0.35 else 0.0
                    is_void = r.random() < P.VOID_RATE
                    is_ref = (not is_void) and r.random() < P.REFUND_RATE
                    net = 0.0 if is_void else max(0.0, gross - disc - (gross * 0.5 if is_ref else 0.0))
                    alias = product_alias(name, r)
                    # dirty: orphan product / invalid category occasionally
                    if r.random() < P.P_ORPHAN:
                        alias = "UNKNOWN PRODUCT X"
                    cat_out = messy(cat, r)
                    if r.random() < P.P_INVALID_CODE:
                        cat_out = "INVALID_CAT"
                    pay = r.choice(P.PAYMENT_METHODS, p=P.PAYMENT_WEIGHT)
                    rows.append(dict(
                        transaction_id=tid,
                        transaction_date=fmt_date(d, r),
                        outlet=messy(oname, r),
                        product_code=f"PC{mi+1:03d}",
                        product_name=alias,
                        category=cat_out,
                        quantity=qty,
                        gross_sales=fmt_num(gross, r),
                        discount="" if (disc == 0 and maybe_null(r)) else fmt_num(disc, r),
                        net_sales=fmt_num(net, r),
                        payment_method=messy(pay, r),
                        void_flag="y" if is_void else "N",
                        refund_flag="y" if is_ref else "N",
                    ))
                    if r.random() < P.P_DUP_TXN:
                        rows.append(dict(rows[-1]))
                if r.random() < 0.002:
                    rows.append({c: None for c in rows[-1]})
    return pd.DataFrame(rows)


def product_alias(name: str, r: np.random.Generator) -> str:
    v = r.random()
    if v < 0.45:
        return name
    if v < 0.62:
        return name.upper()
    if v < 0.78:
        return name.lower()
    if v < 0.88:
        return name.replace(" ", " - ")
    return name.replace(" ", "  ")          # double space


def property_ids() -> set[str]:
    return {p[0] for p in P.PROPERTIES} | {u[0] for u in P.FNB_UNITS}


# ============================================================ main
def main():
    os.makedirs(OUT_PMS, exist_ok=True)
    os.makedirs(OUT_POS, exist_ok=True)

    print("[gen] PMS bookings ...", flush=True)
    pms = generate_pms()
    pms.to_csv(os.path.join(OUT_PMS, "pms_bookings_raw.csv"), index=False)
    print(f"[gen] PMS rows = {len(pms):,}")

    print("[gen] POS transaction lines ...", flush=True)
    pos = generate_pos()
    pos.to_csv(os.path.join(OUT_POS, "pos_transactions_raw.csv"), index=False)
    print(f"[gen] POS rows = {len(pos):,}")
    print("[gen] DONE")


if __name__ == "__main__":
    main()
