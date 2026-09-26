"""
ETL 11 — FORECAST: 90-day daily forecast for total revenue and F&B net revenue.
Uses a simple multiplicative model with weekly and holiday seasonality.
"""
from __future__ import annotations
import sys, os, json
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P

try:
    import duckdb
except ImportError:
    raise SystemExit("duckdb required")

OUT_DIR = P.FC_DIR

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with duckdb.connect(P.DB_PATH, read_only=True) as c:
        df = c.execute("""
            SELECT full_date AS date, SUM(total_revenue) AS revenue, SUM(fnb_net_revenue) AS fnb
            FROM mart_kpi_daily GROUP BY 1 ORDER BY 1
        """).fetch_df()
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").asfreq("D").fillna(0)
    # Build forecast horizon
    future_dates = pd.date_range(P.FC_START, P.FC_END, freq="D")
    # Simple baseline: last 30-day rolling average plus day-of-week and month factors
    recent = float(df["revenue"].rolling(30, min_periods=1).mean().iloc[-1])
    recent_fnb = float(df["fnb"].rolling(30, min_periods=1).mean().iloc[-1])
    rows = []
    for d in future_dates:
        f = P.DOW_FACTOR[d.weekday()] * P.MONTH_FACTOR[d.month] * (P.YEAR_UPLIFT.get(d.year, 1.12))
        rows.append({
            "date": d.strftime("%Y-%m-%d"),
            "forecast_revenue": round(recent * f / 1e9, 4),
            "forecast_fnb": round(recent_fnb * f / 1e9, 4),
            "scenario": "baseline"
        })
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT_DIR, "forecast_90d.csv"), index=False)
    # summary JSON
    summary = {
        "horizon_days": len(future_dates),
        "start": future_dates[0].strftime("%Y-%m-%d"),
        "end": future_dates[-1].strftime("%Y-%m-%d"),
        "total_forecast_revenue_bn": round(out["forecast_revenue"].sum(), 2),
        "total_forecast_fnb_bn": round(out["forecast_fnb"].sum(), 2)
    }
    with open(os.path.join(OUT_DIR, "forecast_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print("[11] forecast written to", OUT_DIR)

if __name__ == "__main__":
    main()
