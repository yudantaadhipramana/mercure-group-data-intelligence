"""
ETL 14 — PREPARE DASHBOARD JSON: compact aggregated payload for the Next.js app.
Includes forecast, anomaly, insights, and role-aware summaries.
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


def fmt_bn(v):
    return f"Rp {v:.2f} bn"


def fmt_k(v):
    return f"Rp {v/1000:.1f}k"


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    data = {}

    # KPI summary
    kpi = q("""
        SELECT SUM(total_revenue) AS total_revenue, SUM(ebitda) AS ebitda,
               AVG(occupancy_pct) AS occupancy, AVG(adr) AS adr, AVG(revpar) AS revpar,
               SUM(fnb_net_revenue) AS fnb_revenue,
               SUM(fnb_cogs)/NULLIF(SUM(fnb_net_revenue),0)*100 AS food_cost_pct,
               SUM(fnb_discount) AS discounts, SUM(fnb_transactions) AS transactions,
               SUM(room_revenue) AS room_revenue
        FROM mart_kpi_daily
    """).iloc[0].to_dict()

    data["kpi"] = [
        {"metric": "Total Revenue", "value": fmt_bn(kpi["total_revenue"]/1e9), "context": "Group consolidated"},
        {"metric": "EBITDA", "value": fmt_bn(kpi["ebitda"]/1e9), "context": f"Margin {kpi['ebitda']/kpi['total_revenue']*100:.1f}%"},
        {"metric": "Occupancy", "value": f"{kpi['occupancy']*100:.1f}%", "context": "Avg. across hotels"},
        {"metric": "ADR", "value": fmt_k(kpi["adr"]), "context": "Average daily rate"},
        {"metric": "RevPAR", "value": fmt_k(kpi["revpar"]), "context": "Revenue per available room"},
        {"metric": "F&B Revenue", "value": fmt_bn(kpi["fnb_revenue"]/1e9), "context": "Net F&B sales"},
        {"metric": "Food Cost %", "value": f"{kpi['food_cost_pct']:.1f}%", "context": f"Target <{P.HEALTHY_FOOD_COST}%"},
        {"metric": "Transactions", "value": f"{int(kpi['transactions']):,}", "context": "F&B transactions"},
    ]

    # daily trend (monthly rollup for cleaner chart)
    daily = q("""SELECT full_date AS date, SUM(total_revenue) AS revenue, SUM(ebitda) AS ebitda,
                        AVG(occupancy_pct) AS occupancy
                 FROM mart_kpi_daily GROUP BY 1 ORDER BY 1""")
    daily["date"] = pd.to_datetime(daily["date"])
    monthly = daily.resample("ME", on="date").agg({"revenue": "sum", "ebitda": "sum", "occupancy": "mean"}).reset_index()
    monthly["month"] = monthly["date"].dt.strftime("%Y-%m")
    data["daily_trend"] = monthly.to_dict("records")

    # property performance
    prop = q("""SELECT property_name, business_type, SUM(total_revenue) AS revenue,
                       SUM(ebitda) AS ebitda, AVG(occupancy_pct) AS occupancy, AVG(adr) AS adr
                FROM mart_kpi_daily GROUP BY 1, 2 ORDER BY 3 DESC""")
    prop["revenue_bn"] = (prop["revenue"] / 1e9).round(2)
    prop["ebitda_bn"] = (prop["ebitda"] / 1e9).round(2)
    prop["occupancy_pct"] = (prop["occupancy"] * 100).round(1)
    data["properties"] = prop.to_dict("records")

    # F&B by category
    fnb_cat = q("""SELECT cat.category_name AS category, SUM(f.net_sales) AS net_sales,
                          SUM(f.cogs_amount) AS cogs, COUNT(DISTINCT f.transaction_id) AS transactions
                    FROM fact_fnb_sales f
                    JOIN dim_product p ON p.product_id=f.product_id
                    JOIN dim_product_category cat ON cat.category_id=p.category_id
                    GROUP BY 1 ORDER BY 2 DESC""")
    fnb_cat["sales_bn"] = (fnb_cat["net_sales"] / 1e9).round(3)
    fnb_cat["food_cost_pct"] = (fnb_cat["cogs"] / fnb_cat["net_sales"] * 100).round(1)
    data["fnb_category"] = fnb_cat.to_dict("records")

    # finance
    fin = q("""SELECT a.account_type, SUM(e.amount) AS amount FROM fact_expense e
               JOIN dim_account a ON a.account_id=e.account_id GROUP BY 1""")
    fin["amount_bn"] = (fin["amount"] / 1e9).round(2)
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

    # forecast
    fc = pd.read_csv(os.path.join(P.FC_DIR, "forecast_90d.csv"))
    data["forecast"] = fc.to_dict("records")

    # anomaly summary (top 10)
    an = pd.read_csv(os.path.join(P.AD_DIR, "anomalies.csv"))
    data["anomalies"] = an.head(10).to_dict("records")

    # insights
    insights_path = os.path.join(OUT_DIR, "insights.json")
    if os.path.exists(insights_path):
        with open(insights_path, "r", encoding="utf-8") as fh:
            data["insights"] = json.load(fh)
    else:
        data["insights"] = []

    with open(os.path.join(OUT_DIR, "dashboard_data.json"), "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str)
    print("[14] dashboard_data.json written to", OUT_DIR)


if __name__ == "__main__":
    main()
