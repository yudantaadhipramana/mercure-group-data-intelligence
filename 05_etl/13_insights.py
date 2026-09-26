"""
ETL 13 — INSIGHTS: evidence-based business insights from the warehouse.
"""
from __future__ import annotations
import sys, os, json
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P

try:
    import duckdb
except ImportError:
    raise SystemExit("duckdb required")

OUT_DIR = P.DASH_DIR

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with duckdb.connect(P.DB_PATH, read_only=True) as c:
        # 1. group KPI totals
        kpi = c.execute("""
            SELECT SUM(total_revenue) AS total_revenue,
                   SUM(ebitda) AS ebitda,
                   AVG(occupancy_pct) AS occupancy,
                   AVG(adr) AS adr,
                   AVG(revpar) AS revpar,
                   SUM(fnb_net_revenue) AS fnb_revenue,
                   SUM(fnb_cogs)/NULLIF(SUM(fnb_net_revenue),0)*100 AS food_cost_pct
            FROM mart_kpi_daily
        """).fetch_df()
        # 2. top and bottom properties by total revenue
        prop = c.execute("""
            SELECT property_name, SUM(total_revenue) AS revenue, SUM(ebitda) AS ebitda
            FROM mart_kpi_daily GROUP BY 1 ORDER BY 2 DESC
        """).fetch_df()
        # 3. monthly trend YoY
        trend = c.execute("""
            SELECT year, month, SUM(total_revenue) AS revenue
            FROM mart_kpi_daily GROUP BY 1, 2 ORDER BY 1, 2
        """).fetch_df()
        yoy = {}
        for (y, m), g in trend.groupby(["year", "month"]):
            yoy[(y, m)] = float(g["revenue"].iloc[0])
        latest = max(yoy.keys())
        prior = (latest[0]-1, latest[1])
        yoy_growth = (yoy[latest] - yoy.get(prior, yoy[latest])) / yoy[latest] * 100 if yoy[latest] else 0

    insights = [
        {
            "metric": "Total Revenue",
            "value": round(float(kpi["total_revenue"].iloc[0]) / 1e9, 2),
            "unit": "IDR bn",
            "period": "2025-2026",
            "comparison": f"YoY growth {yoy_growth:+.1f}%",
            "evidence": f"Top property: {prop.iloc[0]['property_name']} ({prop.iloc[0]['revenue']/1e9:.2f}bn); bottom: {prop.iloc[-1]['property_name']} ({prop.iloc[-1]['revenue']/1e9:.2f}bn).",
            "interpretation": "Revenue is diversified across hotel and F&B business units.",
            "investigation": "Investigate revenue per available room and F&B average check variance."
        },
        {
            "metric": "EBITDA",
            "value": round(float(kpi["ebitda"].iloc[0]) / 1e9, 2),
            "unit": "IDR bn",
            "period": "2025-2026",
            "comparison": f"Margin {float(kpi['ebitda'].iloc[0])/float(kpi['total_revenue'].iloc[0])*100:.1f}%",
            "evidence": "Computed from revenue minus COGS and OPEX from the warehouse.",
            "interpretation": "EBITDA margin reflects the combined effect of room revenue and F&B gross margin.",
            "investigation": "Drill into properties with EBITDA below group average."
        },
        {
            "metric": "Occupancy / ADR / RevPAR",
            "value": f"{float(kpi['occupancy'].iloc[0])*100:.1f}% / {float(kpi['adr'].iloc[0])/1000:.0f}k / {float(kpi['revpar'].iloc[0])/1000:.0f}k",
            "unit": "",
            "period": "2025-2026",
            "comparison": "Group average.",
            "evidence": "Occupancy is derived from rooms sold over available room nights.",
            "interpretation": "Average occupancy and rate performance across hotels.",
            "investigation": "Check seasonality and long-weekend lift."
        },
        {
            "metric": "F&B Food Cost %",
            "value": round(float(kpi["food_cost_pct"].iloc[0]), 1),
            "unit": "%",
            "period": "2025-2026",
            "comparison": f"Target <{P.HEALTHY_FOOD_COST}%",
            "evidence": "Aggregated F&B COGS over net F&B revenue.",
            "interpretation": "Food cost is within target if below threshold; investigate outliers.",
            "investigation": "Review procurement price trends and waste by outlet."
        }
    ]

    with open(os.path.join(OUT_DIR, "insights.json"), "w", encoding="utf-8") as fh:
        json.dump(insights, fh, indent=2)
    print("[13] insights written to", OUT_DIR)

if __name__ == "__main__":
    main()
