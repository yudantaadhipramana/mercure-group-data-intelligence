"""
ETL 14 — PREPARE DASHBOARD JSON: compact aggregated payload for the Next.js app.
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

OUT_DIR = P.DASH_DIR

def q(sql):
    with duckdb.connect(P.DB_PATH, read_only=True) as c:
        return c.execute(sql).fetch_df()

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    data = {}
    # KPI summary
    kpi = q("""
        SELECT SUM(total_revenue) AS total_revenue, SUM(ebitda) AS ebitda,
               AVG(occupancy_pct) AS occupancy, AVG(adr) AS adr, AVG(revpar) AS revpar,
               SUM(fnb_net_revenue) AS fnb_revenue,
               SUM(fnb_cogs)/NULLIF(SUM(fnb_net_revenue),0)*100 AS food_cost_pct,
               SUM(fnb_discount) AS discounts, SUM(fnb_transactions) AS transactions
        FROM mart_kpi_daily
    """).iloc[0].to_dict()
    data["kpi"] = {
        "total_revenue": round(float(kpi["total_revenue"]) / 1e9, 2),
        "ebitda": round(float(kpi["ebitda"]) / 1e9, 2),
        "ebitda_margin": round(float(kpi["ebitda"]) / float(kpi["total_revenue"]) * 100, 1),
        "occupancy": round(float(kpi["occupancy"]) * 100, 1),
        "adr": round(float(kpi["adr"]) / 1000, 1),
        "revpar": round(float(kpi["revpar"]) / 1000, 1),
        "fnb_revenue": round(float(kpi["fnb_revenue"]) / 1e9, 2),
        "food_cost_pct": round(float(kpi["food_cost_pct"]), 1),
        "discounts": round(float(kpi["discounts"]) / 1e6, 1),
        "transactions": int(kpi["transactions"])
    }
    # daily trend
    daily = q("""SELECT full_date AS date, SUM(total_revenue) AS revenue, SUM(ebitda) AS ebitda,
                        AVG(occupancy_pct) AS occupancy
                 FROM mart_kpi_daily GROUP BY 1 ORDER BY 1""")
    data["daily_trend"] = daily.to_dict("records")
    # property performance
    prop = q("""SELECT property_name, business_type, SUM(total_revenue) AS revenue, SUM(ebitda) AS ebitda,
                       AVG(occupancy_pct) AS occupancy, AVG(adr) AS adr
                FROM mart_kpi_daily GROUP BY 1, 2 ORDER BY 3 DESC""")
    data["properties"] = prop.to_dict("records")
    # F&B by category
    fnb_cat = q("""SELECT cat.category_name AS category, SUM(f.net_sales) AS net_sales, SUM(f.cogs_amount) AS cogs
                    FROM fact_fnb_sales f
                    JOIN dim_product p ON p.product_id=f.product_id
                    JOIN dim_product_category cat ON cat.category_id=p.category_id
                    GROUP BY 1 ORDER BY 2 DESC""")
    data["fnb_category"] = fnb_cat.to_dict("records")
    # finance
    fin = q("""SELECT a.account_type, SUM(e.amount) AS amount FROM fact_expense e
               JOIN dim_account a ON a.account_id=e.account_id GROUP BY 1""")
    data["finance"] = fin.to_dict("records")
    # inventory
    inv = q("""SELECT SUM(opening_stock) AS opening, SUM(purchase_qty) AS purchase,
                      SUM(consumption_qty) AS consumption, SUM(waste_qty) AS waste,
                      SUM(closing_stock) AS closing, SUM(stock_value) AS stock_value
               FROM fact_inventory""").iloc[0].to_dict()
    data["inventory"] = {k: float(v) for k, v in inv.items()}
    # DQ
    dq = q("SELECT source, quality_score, dq_tier, status FROM dq_source_health")
    data["dq"] = dq.to_dict("records")
    # save
    with open(os.path.join(OUT_DIR, "dashboard_data.json"), "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str)
    print("[14] dashboard_data.json written to", OUT_DIR)

if __name__ == "__main__":
    main()
