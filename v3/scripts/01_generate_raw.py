"""
Generate realistic multi-source heterogeneous raw CSV files for Mercure Group v3.
Each source system has its own column names, date formats, and number formats.
Data is intentionally heterogeneous and moderately sized for fast ETL demo.
"""
import os, random, datetime, string
import numpy as np
import pandas as pd
from datetime import date, timedelta

import params_v3 as P

random.seed(42)
np.random.seed(42)


def fmt_idr(x, style="id"):
    v = abs(x)
    if style == "id":
        return f"Rp {v:,.0f}".replace(",", ".").replace(".", ",", 1)
    elif style == "en":
        return f"IDR {v:,.2f}"
    elif style == "plain":
        return f"{v:.0f}"


def fmt_date(d, style="ymd"):
    if style == "ymd":
        return d.strftime("%Y-%m-%d")
    elif style == "dmy":
        return d.strftime("%d/%m/%Y")
    elif style == "mdy":
        return d.strftime("%m/%d/%Y")
    elif style == "yymmdd":
        return d.strftime("%y%m%d")
    elif style == "ddmmyyyy":
        return d.strftime("%d%m%Y")
    elif style == "dot":
        return d.strftime("%d.%m.%Y")
    elif style == "dash_yyyy_mm_dd":
        return d.strftime("%Y-%m-%d")


def add_noise(val, noise=0.05):
    return val * (1 + random.uniform(-noise, noise))


def make_pms(properties):
    rows = []
    for p in properties:
        base_rooms = p[4]
        for d in [P.START_DATE + timedelta(days=i) for i in range((P.END_DATE - P.START_DATE).days + 1)]:
            dow_factor = P.DOW_FACTOR[d.weekday()] * P.MONTH_FACTOR[d.month] * P.YEAR_UPLIFT.get(d.year, 1.0)
            if d in P.HOLIDAYS:
                dow_factor *= 1.25
            n_confirmed = min(base_rooms, max(1, int(base_rooms * random.uniform(0.55, 0.85) * dow_factor)))
            for _ in range(n_confirmed):
                los = max(1, int(np.random.choice([1, 2, 3, 4, 5], p=[0.35, 0.30, 0.20, 0.10, 0.05])))
                rt = random.choice(P.ROOM_TYPES)
                rate = int(add_noise(750000, 0.10))
                seg = random.choice(P.SEGMENTS)
                ch = random.choice(P.CHANNELS)
                revenue = rate
                rows.append({"property_code": p[0], "booking_date": fmt_date(d), "check_in": fmt_date(d), "check_out": fmt_date(d + timedelta(days=los)),
                             "room_type": rt[1], "guest_segment": seg, "channel": ch, "status": "confirmed", "room_rate_idr": fmt_idr(rate, "plain"),
                             "room_revenue_idr": fmt_idr(revenue, "plain")})
    return pd.DataFrame(rows)


def make_pms_hotel02(properties):
    rows = []
    for p in properties:
        base_rooms = p[4]
        for d in [P.START_DATE + timedelta(days=i) for i in range((P.END_DATE - P.START_DATE).days + 1)]:
            dow_factor = P.DOW_FACTOR[d.weekday()] * P.MONTH_FACTOR[d.month] * P.YEAR_UPLIFT.get(d.year, 1.0)
            if d in P.HOLIDAYS:
                dow_factor *= 1.25
            n_confirmed = min(base_rooms, max(1, int(base_rooms * random.uniform(0.55, 0.85) * dow_factor)))
            for _ in range(n_confirmed):
                los = max(1, int(np.random.choice([1, 2, 3, 4, 5], p=[0.35, 0.30, 0.20, 0.10, 0.05])))
                rt = random.choice(P.ROOM_TYPES)
                rate = int(add_noise(750000, 0.10))
                seg = random.choice(P.SEGMENTS)
                ch = random.choice(P.CHANNELS)
                revenue = rate
                rows.append({"hotel_name": p[1].upper(), "arrival_date": fmt_date(d, "dmy"), "departure_date": fmt_date(d + timedelta(days=los), "dmy"),
                             "room_category": rt[1], "market_segment": seg, "distribution_channel": ch, "reservation_status": "confirmed", "adr": fmt_idr(rate, "en"),
                             "revenue": fmt_idr(revenue, "id")})
    return pd.DataFrame(rows)


def make_pms_hotel03(properties):
    rows = []
    for p in properties:
        base_rooms = p[4]
        for d in [P.START_DATE + timedelta(days=i) for i in range((P.END_DATE - P.START_DATE).days + 1)]:
            dow_factor = P.DOW_FACTOR[d.weekday()] * P.MONTH_FACTOR[d.month] * P.YEAR_UPLIFT.get(d.year, 1.0)
            if d in P.HOLIDAYS:
                dow_factor *= 1.25
            n_confirmed = min(base_rooms, max(1, int(base_rooms * random.uniform(0.55, 0.85) * dow_factor)))
            for _ in range(n_confirmed):
                los = max(1, int(np.random.choice([1, 2, 3, 4, 5], p=[0.35, 0.30, 0.20, 0.10, 0.05])))
                rt = random.choice(P.ROOM_TYPES)
                rate = int(add_noise(750000, 0.10))
                seg = random.choice(P.SEGMENTS)
                ch = random.choice(P.CHANNELS)
                revenue = rate
                rows.append({"Hotel": f"MG {p[2]}", "Type": rt[1], "Date In": fmt_date(d, "mdy"), "Date Out": fmt_date(d + timedelta(days=los), "mdy"),
                             "Segment": seg[:3].upper(), "Channel": ch, "Cancelled": "C", "Rate": f"{rate:,.2f}", "Rev": f"{revenue:,.2f}"})
    return pd.DataFrame(rows)


def make_pos_fn01():
    rows = []
    for o in P.OUTLETS:
        for d in [P.START_DATE + timedelta(days=i) for i in range((P.END_DATE - P.START_DATE).days + 1)]:
            base_tx = random.randint(40, 120)
            for _ in range(base_tx):
                m = random.choice(P.MENU)
                qty = random.randint(1, 4)
                price = m[4]
                gross = qty * price
                disc = gross * random.uniform(0, 0.15) if random.random() < 0.3 else 0
                net = gross - disc
                rows.append({"outlet_name": o[1], "date": fmt_date(d, "dmy"), "item_code": f"PC{random.randint(1,999):03d}", "item_name": m[1], "category": m[0], "qty": qty,
                             "gross": f"{gross:,.0f}".replace(",", ".").replace(".", ",", 1), "disc": f"{disc:,.0f}".replace(",", ".").replace(".", ",", 1), "net": f"{net:,.0f}".replace(",", ".").replace(".", ",", 1),
                             "void": "N", "refund": "N", "source_system": "POS-FNB-01"})
    return pd.DataFrame(rows)


def make_pos_fn02():
    rows = []
    for o in P.OUTLETS:
        for d in [P.START_DATE + timedelta(days=i) for i in range((P.END_DATE - P.START_DATE).days + 1)]:
            base_tx = random.randint(40, 120)
            for _ in range(base_tx):
                m = random.choice(P.MENU)
                qty = random.randint(1, 4)
                price = m[4]
                gross = qty * price
                disc = gross * random.uniform(0, 0.15) if random.random() < 0.3 else 0
                net = gross - disc
                rows.append({"outlet": o[1], "transaction_date": fmt_date(d, "ymd"), "sku": f"PC{random.randint(1,999):03d}", "product": m[1], "product_group": m[0], "quantity": qty,
                             "gross_sales": gross, "discount": disc, "net_sales": net, "is_void": "N", "is_refund": "N", "source_system": "POS-FNB-02"})
    return pd.DataFrame(rows)


def make_finance():
    rows = []
    for p in P.PROPERTIES + P.FNB_UNITS:
        for d in [P.START_DATE + timedelta(days=i) for i in range(0, (P.END_DATE - P.START_DATE).days + 1, 7)]:
            for a in P.ACCOUNTS:
                if a[3] in ("D02",) and p[0].startswith("P"):
                    continue
                base = random.uniform(1e6, 3e6)
                if a[2] == "Revenue":
                    base = random.uniform(20e6, 80e6)
                rows.append({"branch": p[1], "date": fmt_date(d, "ymd"), "gl_account": a[0], "account_name": a[1], "amount": f"{base:,.2f}", "source_system": "ERP-FIN-01"})
    return pd.DataFrame(rows)


def make_inventory():
    rows = []
    for p in P.PROPERTIES + P.FNB_UNITS:
        for m in P.MENU:
            for d in [P.START_DATE + timedelta(days=i) for i in range(0, (P.END_DATE - P.START_DATE).days + 1, 14)]:
                opening = random.randint(50, 200)
                purchase = random.randint(10, 60)
                transfer = random.randint(-20, 20)
                consumption = random.randint(20, 80)
                waste = random.randint(0, 10)
                closing = opening + purchase + transfer - consumption - waste
                stock_value = closing * m[3] * 5000
                rows.append({"branch": p[1], "date": fmt_date(d, "ymd"), "sku": f"PC{random.randint(1,999):03d}", "product": m[1], "opening": opening, "purchase": purchase, "transfer": transfer,
                             "consumption": consumption, "waste": waste, "closing": closing, "stock_value": f"{stock_value:,.2f}", "source_system": "INV-SYSTEM-01"})
    return pd.DataFrame(rows)


def make_procurement():
    rows = []
    for p in P.PROPERTIES + P.FNB_UNITS:
        for m in P.MENU:
            for d in [P.START_DATE + timedelta(days=i) for i in range(0, (P.END_DATE - P.START_DATE).days + 1, 14)]:
                qty = random.randint(20, 100)
                unit = random.uniform(4500, 6500)
                total = qty * unit
                rows.append({"branch": p[1], "po_date": fmt_date(d, "dmy"), "sku": f"PC{random.randint(1,999):03d}", "product": m[1], "qty": qty, "unit_price": f"{unit:,.2f}", "total": f"{total:,.2f}", "source_system": "PROCUREMENT-01"})
    return pd.DataFrame(rows)


def make_budget():
    rows = []
    for p in P.PROPERTIES + P.FNB_UNITS:
        for a in P.ACCOUNTS:
            base = random.uniform(1.5e6, 6e6) * 30
            if a[2] == "Revenue":
                base = random.uniform(8e6, 25e6) * 30
            for m in range(1, 13):
                y = 2026
                d = date(y, m, 1)
                rows.append({"branch": p[1], "period": fmt_date(d, "ymd"), "account_code": a[0], "account_name": a[1], "budget_amount": f"{base:,.2f}", "source_system": "BUDGET-01"})
    return pd.DataFrame(rows)


def main():
    os.makedirs(P.RAW_DIR, exist_ok=True)
    # Each PMS source handles a distinct subset of hotels to demonstrate multi-source
    # without double-counting.
    make_pms(P.PROPERTIES[:2]).to_csv(f"{P.RAW_DIR}/RAW_PMS_PMS-HOTEL-01.csv", index=False)
    make_pms_hotel02(P.PROPERTIES[2:4]).to_csv(f"{P.RAW_DIR}/RAW_PMS_PMS-HOTEL-02.csv", index=False)
    make_pms_hotel03(P.PROPERTIES[4:]).to_csv(f"{P.RAW_DIR}/RAW_PMS_PMS-HOTEL-03.csv", index=False)
    make_pos_fn01().to_csv(f"{P.RAW_DIR}/RAW_POS_POS-FNB-01.csv", index=False)
    make_pos_fn02().to_csv(f"{P.RAW_DIR}/RAW_POS_POS-FNB-02.csv", index=False)
    make_finance().to_csv(f"{P.RAW_DIR}/RAW_FINANCE_ERP-FIN-01.csv", index=False)
    make_inventory().to_csv(f"{P.RAW_DIR}/RAW_INVENTORY_INV-SYSTEM-01.csv", index=False)
    make_procurement().to_csv(f"{P.RAW_DIR}/RAW_PROCUREMENT_PROCUREMENT-01.csv", index=False)
    make_budget().to_csv(f"{P.RAW_DIR}/RAW_BUDGET_BUDGET-01.csv", index=False)
    print("Raw files generated:", os.listdir(P.RAW_DIR))


if __name__ == "__main__":
    main()
