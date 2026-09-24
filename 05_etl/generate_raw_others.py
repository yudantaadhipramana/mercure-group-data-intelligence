"""
PHASE 5 — Synthetic raw data generation: Finance/ERP, Inventory, Procurement, Budget.

Business linkages (not random):
  Finance   : COGS accounts fed from F&B COGS; OPEX as ratio of revenue
  Inventory : consumption derived from POS quantities; waste % of consumption
              opening = prior closing; procurement refills to reorder coverage
  Procurement: unit price drifts with inflation (drives food-cost trend + anomalies)
  Budget    : planned number per property×dept×account×month with property optimism/pessimism
All deliberately dirty.
"""
from __future__ import annotations
import sys, os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P
from raw_writers import fmt_date, fmt_num, messy, maybe_null, blank_row

all_props = [(p[0], p[1], p[2]) for p in P.PROPERTIES] + [(u[0], u[1], u[2]) for u in P.FNB_UNITS]
HOTEL_IDS = [p[0] for p in P.PROPERTIES]
FNB_IDS = [u[0] for u in P.FNB_UNITS]

# ============================================================ FINANCE / ERP
def generate_finance() -> pd.DataFrame:
    """One expense/COGS transaction per property × account × month, plus revenue recognition lines."""
    r = P.rng(303)
    rows = []
    seq = 0
    # monthly revenue per property (reused to scale OPEX) — recompute the same way the
    # hotel/F&B model does so finance is consistent with PMS/POS
    for d in P.daterange():
        pass
    monthly_rev: dict[tuple[str, int, int], float] = {}
    # (computed later from facts; here we approximate with the same demand model so
    #  finance expense lines scale with business activity)
    for pid, *_ in all_props:
        for d in pd.date_range(P.START_DATE, P.END_DATE, freq="MS"):
            f = P.date_factors(d.date())
            if pid in HOTEL_IDS:
                base = dict((p[0], p[4] * p[6] * p[7] * 1000) for p in P.PROPERTIES)[pid]
                rev = base * f * 30 * 0.72
            else:
                rev = 95_000_000 * f * 30
            monthly_rev[(pid, d.year, d.month)] = rev

    for pid, pname, city in all_props:
        alias = property_alias(pid, r)
        for d in pd.date_range(P.START_DATE, P.END_DATE, freq="MS"):
            rev = monthly_rev[(pid, d.year, d.month)]
            for code, aname, atype, dept in P.ACCOUNTS:
                # dirty: skip a few to create gaps; include invalid types occasionally
                if r.random() < 0.02:
                    continue
                atype_out = atype
                if r.random() < P.P_INVALID_CODE:
                    atype_out = r.choice(["Revenu", "OPES", "COG", "rev"])
                amount = 0.0
                if atype == "COGS":
                    amount = rev * (0.09 + 0.05 * r.random())
                elif atype == "OPEX":
                    amount = rev * (P.OPEX_TO_REVENUE / 22) * (0.6 + 0.8 * r.random())
                elif atype == "Revenue":
                    amount = rev * (0.02 + 0.10 * r.random())
                if amount <= 0:
                    continue
                seq += 1
                code_out = code
                if r.random() < P.P_INVALID_CODE:
                    code_out = code + "X"
                rows.append(dict(
                    transaction_id=f"GL{seq:08d}",
                    transaction_date=fmt_date(d.date(), r),
                    property=messy(alias, r),
                    account_code=code_out,
                    account_name=messy(aname, r),
                    department=messy(dict(P.DEPARTMENTS)[dept], r),
                    amount=fmt_num(amount, r),
                    transaction_type=r.choice(["Debit", "Credit"]),
                ))
                if r.random() < P.P_DUP_TXN:
                    rows.append(dict(rows[-1]))
                if r.random() < 0.002:
                    rows.append({c: None for c in rows[-1]})
    # orphans: unknown property
    for i in range(int(len(rows) * P.P_UNKNOWN_PROPERTY * 2)):
        rows[r.integers(0, len(rows))]["property"] = "MG Solo"
    return pd.DataFrame(rows)


# ============================================================ INVENTORY
def generate_inventory() -> pd.DataFrame:
    r = P.rng(404)
    # subset of menu products tracked in inventory
    menu = [(i, cat, name, price, cost) for i, (cat, name, price, cost) in enumerate(P.MENU)]
    tracked = [m for m in menu if r.random() < P.POC_INV_PRODUCT_RATE]
    rows = []
    # daily consumption per product (units) ~ POS-like demand
    for pid, pname, city in all_props:
        alias = property_alias(pid, r)
        stock = {m[0]: max(20.0, r.uniform(30, 90)) for m in tracked}   # opening stock units
        for d in P.daterange():
            f = P.date_factors(d)
            for mi, cat, name, price, cost in tracked:
                cons = max(0.0, r.poisson((4 + 10 * f) * (0.7 + 0.6 * r.random())))
                waste = round(cons * P.WASTE_RATE * r.random(), 1)
                purch = 0.0
                if stock[mi] < cons * P.REORDER_COVERAGE:
                    purch = round(cons * (P.REORDER_COVERAGE + 2) * (0.9 + 0.2 * r.random()), 1)
                open_s = stock[mi]
                close_s = max(0.0, open_s + purch - cons - waste)
                stock[mi] = close_s
                unit_cost = price * cost * (1 + P.INFLATION_DRIFT_YEARLY *
                                            ((d - P.START_DATE).days / 365.0))
                if r.random() < P.P_NEG_QTY:
                    cons = -cons
                rows.append(dict(
                    inventory_date=fmt_date(d, r),
                    property=messy(alias, r),
                    product_code=f"PC{mi+1:03d}",
                    product_name=product_alias(name, r),
                    opening_stock=fmt_num(open_s, r, 1),
                    purchase_qty=fmt_num(purch, r, 1),
                    transfer_qty="" if maybe_null(r, 0.03) else fmt_num(0.0, r, 1),
                    consumption_qty=fmt_num(cons, r, 1),
                    waste_qty=fmt_num(waste, r, 1),
                    closing_stock=fmt_num(close_s, r, 1),
                    stock_value=fmt_num(close_s * unit_cost, r),
                ))
                if r.random() < P.P_DUP_TXN * 0.4:
                    rows.append(dict(rows[-1]))
    return pd.DataFrame(rows)


# ============================================================ PROCUREMENT
def generate_procurement(inventory_source: pd.DataFrame) -> pd.DataFrame:
    r = P.rng(505)
    rows = []
    seq = 0
    sup = P.SUPPLIERS
    purch = inventory_source[inventory_source["purchase_qty"].notna()]
    return None  # placeholder — procurement derived in step below


def generate_procurement_from_inventory(inv: pd.DataFrame) -> pd.DataFrame:
    """One purchase line per (property, product, date) where purchase_qty > 0."""
    r = P.rng(505)
    rows = []
    seq = 0
    inv = inv.copy()
    inv["_d"] = pd.to_datetime(inv["inventory_date"], format="mixed", dayfirst=True, errors="coerce")
    inv["_p"] = inv["purchase_qty"].replace("", np.nan).str.replace(",", "").astype(float)
    sel = inv[inv["_p"] > 0]
    for _, row in sel.iterrows():
        seq += 1
        s = sup_of(r)
        qty = float(row["_p"])
        unit = float(row["_unit_cost"]) if "_unit_cost" in row else 0.0
        base = next((m[3] for m in P.MENU if False), 0.10)
        unit_price = max(1000.0, qty and (float(row.get("stock_value", 0)) / qty) or 0) if False else None
        # unit price reconstructed from stock value / qty when available, else base cost ratio
        if unit_price is None:
            name = str(row["product_name"]).strip().lower()
            ratio = 0.28
            price = 50000.0
            for cat, nm, pr, cost in P.MENU:
                if nm.lower() == name:
                    ratio, price = cost, pr
                    break
            unit_price = price * ratio * (1 + P.INFLATION_DRIFT_YEARLY *
                                          ((row["_d"].date() - P.START_DATE).days / 365.0))
        total = qty * unit_price
        rows.append(dict(
            purchase_id=f"PO{seq:07d}",
            purchase_date=fmt_date(row["_d"].date(), r),
            supplier=messy(s[1], r),
            property=messy(row["property"], r),
            product_code=row["product_code"],
            product_name=row["product_name"],
            quantity=fmt_num(qty, r, 1),
            unit_price=fmt_num(unit_price, r),
            total_amount=fmt_num(total, r),
        ))
        if r.random() < P.P_DUP_TXN:
            rows.append(dict(rows[-1]))
        if r.random() < 0.001:
            rows.append({c: None for c in rows[-1]})
    return pd.DataFrame(rows)


def sup_of(r) -> tuple:
    return P.SUPPLIERS[r.integers(0, len(P.SUPPLIERS))]


# ============================================================ BUDGET
def generate_budget() -> pd.DataFrame:
    r = P.rng(606)
    rows = []
    # property budget temperament: some beat budget, some miss
    temper = {p[0]: float(r.normal(0.0, 0.07)) for p in all_props}
    for pid, pname, city in all_props:
        alias = property_alias(pid, r)
        for d in pd.date_range(P.START_DATE, P.END_DATE, freq="MS"):
            f = P.date_factors(d.date())
            for code, aname, atype, dept in P.ACCOUNTS:
                if r.random() < 0.10:
                    continue
                if pid in HOTEL_IDS:
                    base = dict((p[0], p[4] * p[6] * p[7] * 1000) for p in P.PROPERTIES)[pid]
                    rev = base * f * 30 * 0.72
                else:
                    rev = 95_000_000 * f * 30
                if atype == "Revenue":
                    amt = rev * (1 + temper[pid])
                elif atype == "COGS":
                    amt = rev * 0.115
                else:
                    amt = rev * (P.OPEX_TO_REVENUE / 22)
                rows.append(dict(
                    period=r.choice([d.strftime("%Y-%m"), d.strftime("%b-%Y")]),
                    property=messy(alias, r),
                    department=messy(dict(P.DEPARTMENTS)[dept], r),
                    account=messy(aname, r),
                    budget_amount=fmt_num(amt, r),
                ))
    return pd.DataFrame(rows)


# ============================================================ shared alias helpers
def property_alias(pid: str, r: np.random.Generator) -> str:
    for pid_, name, city, *_ in P.PROPERTIES:
        if pid_ == pid:
            return r.choice([name, name.upper(), P.NAME_SHORT.get(name, name),
                             f"MG {city}", name.replace(" ", "-")])
    for uid, name, city, *_ in P.FNB_UNITS:
        if uid == pid:
            return r.choice([name, name.upper(), name.replace(" ", "-"), f"MG {city}"])
    return pid


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
    return name.replace(" ", "  ")


# ============================================================ main
def main():
    os.makedirs(P.RAW_DIRS["finance"], exist_ok=True)
    os.makedirs(P.RAW_DIRS["inventory"], exist_ok=True)
    os.makedirs(P.RAW_DIRS["procurement"], exist_ok=True)
    os.makedirs(P.RAW_DIRS["budget"], exist_ok=True)

    print("[gen] Finance/ERP ...", flush=True)
    fin = generate_finance()
    fin.to_csv(os.path.join(P.RAW_DIRS["finance"], "erp_transactions_raw.csv"), index=False)
    print(f"[gen] finance rows = {len(fin):,}")

    print("[gen] Inventory ...", flush=True)
    inv = generate_inventory()
    inv.to_csv(os.path.join(P.RAW_DIRS["inventory"], "inventory_daily_raw.csv"), index=False)
    print(f"[gen] inventory rows = {len(inv):,}")

    print("[gen] Procurement ...", flush=True)
    proc = generate_procurement_from_inventory(inv)
    proc.to_csv(os.path.join(P.RAW_DIRS["procurement"], "procurement_raw.csv"), index=False)
    print(f"[gen] procurement rows = {len(proc):,}")

    print("[gen] Budget ...", flush=True)
    bud = generate_budget()
    bud.to_csv(os.path.join(P.RAW_DIRS["budget"], "budget_raw.csv"), index=False)
    print(f"[gen] budget rows = {len(bud):,}")
    print("[gen] DONE")


if __name__ == "__main__":
    main()
