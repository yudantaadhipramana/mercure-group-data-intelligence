"""
ETL 01 — EXTRACT: raw CSV → typed staging parquet.

Responsibilities:
  * read the dirty raw files (never modify them)
  * attach lineage (_source_file, _raw_row)
  * parse the deliberately-mixed date formats (pattern-classified, not guessed)
  * parse the deliberately-mixed decimal separators (ID / EN / plain)
  * drop fully-blank rows and blank columns
  * write staging parquet (typed, trimmed)

Everything is computed; nothing is assumed about the data.
"""
from __future__ import annotations
import sys, os, re
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P

DATE_PATTERNS = [
    (re.compile(r"^\d{4}-\d{2}-\d{2}$"), "%Y-%m-%d"),
    (re.compile(r"^\d{2}/\d{2}/\d{4}$"), "%d/%m/%Y"),
    (re.compile(r"^\d{2}-\d{2}-\d{4}$"), "%m-%d-%Y"),
    (re.compile(r"^\d{2}-[A-Za-z]{3}-\d{4}$"), "%d-%b-%Y"),
    (re.compile(r"^\d{8}$"), "%Y%m%d"),
]
_THOUSANDS_COMMA = re.compile(r"^\d{1,3}(,\d{3})+$")
_THOUSANDS_DOT = re.compile(r"^\d{1,3}(\.\d{3})+$")


def to_iso_date(s: pd.Series) -> pd.Series:
    """Parse mixed-format date strings → ISO date string (NaT → None)."""
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    s = s.astype("string").str.strip()
    for rx, fmt in DATE_PATTERNS:
        m = s.str.match(rx).fillna(False)
        if m.any():
            out[m] = pd.to_datetime(s[m], format=fmt, errors="coerce")
    # anything unmatched → coerce (will become NaT and be logged as invalid)
    rest = out.isna() & s.notna() & (s != "")
    if rest.any():
        out[rest] = pd.to_datetime(s[rest], errors="coerce")
    return out.dt.strftime("%Y-%m-%d")


def to_number(s: pd.Series) -> pd.Series:
    """Parse mixed-locale numeric text → float. Blank → NaN."""
    s = s.astype("string").str.strip()

    def conv(x):
        if x is None or (isinstance(x, float) and x != x):
            return np.nan
        try:
            if pd.isna(x):
                return np.nan
        except TypeError:
            pass
        x = str(x)
        if x in ("", "nan", "NaN", "None", "<NA>"):
            return np.nan
        neg = x.startswith("-")
        x = x.lstrip("-+").strip()
        if not re.fullmatch(r"[\d.,]*", x):
            return np.nan
        if "," in x and "." in x:
            if x.rindex(",") > x.rindex("."):       # ID: 1.234.567,89
                x = x.replace(".", "").replace(",", ".")
            else:                                    # EN: 1,234,567.89
                x = x.replace(",", "")
        elif "," in x:
            if _THOUSANDS_COMMA.match(x):            # 1,234,567
                x = x.replace(",", "")
            else:                                    # 1234,56
                x = x.replace(",", ".")
        elif "." in x:
            if _THOUSANDS_DOT.match(x):              # 1.234.567
                x = x.replace(".", "")
        if not x:
            return np.nan
        try:
            v = float(x)
        except ValueError:
            return np.nan
        return -v if neg else v

    return s.map(conv)


def extract_source(name: str, path: str, date_cols, num_cols) -> pd.DataFrame:
    print(f"[01] extract {name}: {os.path.basename(path)}", flush=True)
    df = pd.read_csv(path, dtype=str, keep_default_na=True, encoding="utf-8")
    df["_source_file"] = os.path.basename(path)
    df["_raw_row"] = np.arange(2, len(df) + 2)        # 1-based, header is row 1

    n_raw = len(df)
    # drop fully blank rows (vectorized: count empty cells per row)
    data_cols = [c for c in df.columns if not c.startswith("_")]
    def _is_blank(c):
        v = df[c]
        if v.isna().all():
            return pd.Series(True, index=df.index)
        return v.isna() | (v.astype("string").str.strip() == "")
    blank_mask = pd.concat([_is_blank(c) for c in data_cols], axis=1).all(axis=1)
    n_blank = int(blank_mask.sum())
    df = df[~blank_mask].reset_index(drop=True)

    # drop blank columns (all empty / all null)
    keep = []
    for c in data_cols:
        v = df[c].astype("string").str.strip()
        if not (v.isna().all() or (v == "").all()):
            keep.append(c)
    dropped = [c for c in data_cols if c not in keep]

    for c in keep:
        df[c] = df[c].astype("string").str.strip()
    for c in date_cols:
        if c in df.columns:
            df[c] = to_iso_date(df[c])
    for c in num_cols:
        if c in df.columns:
            df[c] = to_number(df[c])

    print(f"[01]   raw rows {n_raw:,} · blank rows dropped {n_blank} · blank cols dropped {dropped} · kept {len(df):,}")
    return df


def main():
    os.makedirs(P.STG_DIR, exist_ok=True)
    R = P.RAW_DIRS

    jobs = [
        ("pms", os.path.join(R["pms"], "pms_bookings_raw.csv"),
         ["booking_date", "check_in", "check_out"],
         ["room_rate", "room_revenue"]),
        ("pos", os.path.join(R["pos"], "pos_transactions_raw.csv"),
         ["transaction_date"],
         ["quantity", "gross_sales", "discount", "net_sales"]),
        ("finance", os.path.join(R["finance"], "erp_transactions_raw.csv"),
         ["transaction_date"], ["amount"]),
        ("inventory", os.path.join(R["inventory"], "inventory_daily_raw.csv"),
         ["inventory_date"],
         ["opening_stock", "purchase_qty", "transfer_qty", "consumption_qty",
          "waste_qty", "closing_stock", "stock_value"]),
        ("procurement", os.path.join(R["procurement"], "procurement_raw.csv"),
         ["purchase_date"], ["quantity", "unit_price", "total_amount"]),
        ("budget", os.path.join(R["budget"], "budget_raw.csv"),
         [], ["budget_amount"]),
    ]
    for name, path, dates, nums in jobs:
        if not os.path.exists(path):
            print(f"[01] MISSING {path} — skipping")
            continue
        df = extract_source(name, path, dates, nums)
        out = os.path.join(P.STG_DIR, f"stg_{name}.parquet")
        df.to_parquet(out, index=False)
        print(f"[01]   → {out}  ({len(df):,} rows)")
    print("[01] DONE")


if __name__ == "__main__":
    main()
