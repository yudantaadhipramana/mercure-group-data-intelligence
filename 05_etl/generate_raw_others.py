"""
PHASE 5 — Synthetic raw data generation: Finance/ERP, Inventory, Procurement, Budget.
Now with explicit source-system variation.
"""
from __future__ import annotations
import sys, os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P
from raw_writers import fmt_date_for, fmt_num_for, messy, maybe_null

all_props = [(p[0], p[1], p[2]) for p in P.PROPERTIES] + [(u[0], u[1], u[2]) for u in P.FNB_UNITS]
HOTEL_IDS = [p[0] for p in P.PROPERTIES]
FNB_IDS = [u[0] for u in P.FNB_UNITS]


def source_for_finance() -> str:
    return "ERP-FIN-01"


def source_for_inventory() -> str:
    return "INV-SYSTEM-01"


def source_for_procurement() -> str:
    return "PROCUREMENT-01"


def source_for_budget() -> str:
    return "BUDGET-01"


# ============================================================ FINANCE / ERP
def generate_finance() -> pd.DataFrame:
    r = P.rng(303)
    rows = []
    seq = 0
    system = source_for_finance()
    monthly_rev: dict[tuple[str, int, int], float] = {}
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
                    transaction_date=fmt_date_for(d.date(), r, system),
                    property=messy(alias, r),
                    source_system=system,
                    account_code=code_out,
                    account_name=messy(aname, r),
                    department=messy(dict(P.DEPARTMENTS)[dept], r),
                    amount=fmt_num_for(amount, r, system),
                    transaction_type=r.choice(["Debit", "Credit"]),
                ))
                if r.random() < P.P_DUP_TXN:
                    rows.append(dict(rows[-1]))
                if r.random() < 0.002:
                    rows.append({c: None for c in rows[-1]})
    for i in range(int(len(rows) * P.P_UNKNOWN_PROPERTY * 2)):
        rows[r.integers(0, len(rows))]["property"] = "MG Solo"
    return pd.DataFrame(rows)


# ============================================================ INVENTORY
def generate_inventory() -> pd.DataFrame:
    r = P.rng(404)
    menu = [(i, cat, name, price, cost) for i, (cat, name, price, cost) in enumerate(P.MENU)]
    tracked = [m for m in menu if r.random() < P.POC_INV_PRODUCT_RATE]
    rows = []
    system = source_for_inventory()
    for pid, pname, city in all_props:
        alias = property_alias(pid, r)
        stock = {m[0]: max(20.0, r.uniform(30, 90)) for m in tracked}
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
                unit_cost = price * cost * (1 + P.INFLATION_DRIFT_YEARLY * ((d - P.START_DATE).days / 365.0))
                if r.random() < P.P_NEG_QTY:
                    cons = -cons
                rows.append(dict(
                    inventory_date=fmt_date_for(d, r, system),
                    property=messy(alias, r),
                    source_system=system,
                    product_code=f"PC{mi+1:03d}",
                    product_name=product_alias(name, r),
                    opening_stock=fmt_num_for(open_s, r, system, 1),
                    purchase_qty="" if maybe_null(r, 0.03) else fmt_num_for(purch, r, system, 1),
                    transfer_qty="" if maybe_null(r, 0.03) else fmt_num_for(0.0, r, system, 1),
                    consumption_qty=fmt_num_for(cons, r, system, 1),
                    waste_qty=fmt_num_for(waste, r, system, 1),
                    closing_stock=fmt_num_for(close_s, r, system, 1),
                    stock_value=fmt_num_for(close_s * unit_cost, r, system),
                ))
                if r.random() < P.P_DUP_TXN * 0.4:
                    rows.append(dict(rows[-1]))
    return pd.DataFrame(rows)


# ============================================================ PROCUREMENT
def generate_procurement_from_inventory(inv: pd.DataFrame) -> pd.DataFrame:
    r = P.rng(505)
    rows = []
    seq = 0
    system = source_for_procurement()
    sup = P.SUPPLIERS
    inv = inv.copy()
    inv["_d"] = pd.to_datetime(inv["inventory_date"], format="mixed", dayfirst=True, errors="coerce")
    inv["_p"] = inv["purchase_qty"].replace("", np.nan).astype(str).str.replace(",", "").astype(float)
    sel = inv[inv["_p"] > 0]
    for _, row in sel.iterrows():
        seq += 1
        s = sup[r.integers(0, len(sup))]
        qty = float(row["_p"])
        name = str(row["product_name"]).strip().lower()
        ratio = 0.28
        price = 50000.0
        for cat, nm, pr, cost in P.MENU:
            if nm.lower() == name:
                ratio, price = cost, pr
                break
        unit_price = price * ratio * (1 + P.INFLATION_DRIFT_YEARLY * ((row["_d"].date() - P.START_DATE).days / 365.0))
        total = qty * unit_price
        rows.append(dict(
            purchase_id=f"PO{seq:07d}",
            purchase_date=fmt_date_for(row["_d"].date(), r, system),
            supplier=messy(s[1], r),
            source_system=system,
            property=messy(row["property"], r),
            product_code=row["product_code"],
            product_name=row["product_name"],
            quantity=fmt_num_for(qty, r, system, 1),
            unit_price=fmt_num_for(unit_price, r, system),
            total_amount=fmt_num_for(total, r, system),
        ))
        if r.random() < P.P_DUP_TXN:
            rows.append(dict(rows[-1]))
        if r.random() < 0.001:
            rows.append({c: None for c in rows[-1]})
    return pd.DataFrame(rows)


# ============================================================ BUDGET
def generate_budget() -> pd.DataFrame:
    r = P.rng(606)
    rows = []
    system = source_for_budget()
    temperament = {}
    for pid, *_ in all_props:
        temperament[pid] = r.uniform(0.92, 1.08)
    for pid, pname, city in all_props:
        alias = property_alias(pid, r)
        for d in pd.date_range(P.START_DATE, P.END_DATE, freq="MS"):
            f = P.date_factors(d.date())
            base_rev = (dict((p[0], p[4] * p[6] * p[7] * 1000) for p in P.PROPERTIES).get(pid, 95_000_000) * f * 30 * 0.72)
            for code, aname, atype, dept in P.ACCOUNTS:
                if r.random() < 0.02:
                    continue
                if atype == "Revenue":
                    amt = base_rev * (0.02 + 0.10 * r.random())
                elif atype == "COGS":
                    amt = base_rev * (0.09 + 0.05 * r.random())
                else:
                    amt = base_rev * (P.OPEX_TO_REVENUE / 22) * (0.6 + 0.8 * r.random())
                amt = amt * temperament[pid]
                seq = len(rows) + 1
                rows.append(dict(
                    budget_id=f"BD{seq:07d}",
                    period_date=fmt_date_for(d.date(), r, system),
                    property=messy(alias, r),
                    source_system=system,
                    account_code=code,
                    account_name=messy(aname, r),
                    department=messy(dict(P.DEPARTMENTS)[dept], r),
                    budget_amount=fmt_num_for(amt, r, system),
                ))
    return pd.DataFrame(rows)


def property_alias(pid: str, r) -> str:
    for pid_, name, city, *_ in P.PROPERTIES:
        if pid_ == pid:
            short = P.NAME_SHORT.get(name, name)
            variants = [name, name.upper(), short, f"MG {P.CITY_SHORT[city]}", name.replace(" ", "-")]
            return r.choice(variants)
    for uid, uname, city, *_ in P.FNB_UNITS:
        if uid == pid:
            return uname
    return pid


def product_alias(name: str, r) -> str:
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
    for d in [P.RAW_DIRS["finance"], P.RAW_DIRS["inventory"], P.RAW_DIRS["procurement"], P.RAW_DIRS["budget"]]:
        os.makedirs(d, exist_ok=True)
    fin = generate_finance()
    inv = generate_inventory()
    proc = generate_procurement_from_inventory(inv)
    bud = generate_budget()
    fin.to_csv(os.path.join(P.RAW_DIRS["finance"], "erp_transactions_raw.csv"), index=False)
    inv.to_csv(os.path.join(P.RAW_DIRS["inventory"], "inventory_daily_raw.csv"), index=False)
    proc.to_csv(os.path.join(P.RAW_DIRS["procurement"], "procurement_raw.csv"), index=False)
    bud.to_csv(os.path.join(P.RAW_DIRS["budget"], "budget_raw.csv"), index=False)
    print(f"[gen] FIN {len(fin):,} INV {len(inv):,} PROC {len(proc):,} BUD {len(bud):,}")


if __name__ == "__main__":
    main()
