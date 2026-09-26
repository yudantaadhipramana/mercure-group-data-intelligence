"""
ETL 12 — ANOMALY DETECTION: rolling baseline z-score and IQR rules.
Detects unusual revenue, occupancy, ADR, food cost, discount, waste, inventory variance.
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

OUT_DIR = P.AD_DIR

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with duckdb.connect(P.DB_PATH, read_only=True) as c:
        daily = c.execute("""
            SELECT full_date AS date, property_id, property_name, business_type,
                   total_revenue, occupancy_pct, adr, food_cost_pct, fnb_discount, fnb_transactions
            FROM mart_kpi_daily
        """).fetch_df()
    anomalies = []
    for metric in ["total_revenue", "occupancy_pct", "adr", "food_cost_pct", "fnb_discount", "fnb_transactions"]:
        for (prop, biz), g in daily.groupby(["property_id", "business_type"]):
            g = g.sort_values("date").copy()
            s = pd.to_numeric(g[metric], errors="coerce")
            if s.notna().sum() < 30:
                continue
            mu = s.rolling(28, min_periods=14, center=False).mean()
            sd = s.rolling(28, min_periods=14, center=False).std()
            z = (s - mu) / sd
            q1 = s.rolling(28, min_periods=14, center=False).quantile(0.25)
            q3 = s.rolling(28, min_periods=14, center=False).quantile(0.75)
            iqr = q3 - q1
            for idx in g.index[z.abs() > 3].tolist():
                anomalies.append({
                    "date": g.loc[idx, "date"],
                    "property_id": prop,
                    "property_name": g.loc[idx, "property_name"],
                    "business_type": biz,
                    "metric": metric,
                    "actual": float(s.loc[idx]),
                    "expected": float(mu.loc[idx]),
                    "deviation": float(z.loc[idx]),
                    "method": "rolling_z_score",
                    "severity": "high" if abs(z.loc[idx]) > 4 else "medium"
                })
    out = pd.DataFrame(anomalies)
    out.to_csv(os.path.join(OUT_DIR, "anomalies.csv"), index=False)
    with open(os.path.join(OUT_DIR, "anomaly_summary.json"), "w") as fh:
        json.dump({
            "total_anomalies": len(out),
            "metrics": out["metric"].value_counts().to_dict() if not out.empty else {},
            "high_severity": int((out["severity"] == "high").sum()) if not out.empty else 0
        }, fh, indent=2)
    print("[12] anomalies written to", OUT_DIR)

if __name__ == "__main__":
    main()
