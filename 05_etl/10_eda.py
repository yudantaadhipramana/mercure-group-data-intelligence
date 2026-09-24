"""
ETL 10 — EDA: Exploratory Data Analysis on the warehouse marts.

Sections:
  1. Dataset overview (rows, columns, types, missing, duplicates)
  2. Distribution (revenue, transactions, occupancy, ADR, F&B sales, food cost)
  3. Time series (daily revenue, monthly revenue, occupancy, F&B sales)
  4. Segmentation (property, department, category, channel, segment)
  5. Outliers (unusually high/low revenue, occupancy, food cost, transactions)

Output: 08_eda/eda_report.md + charts (PNG) + eda_summary.json
Every figure is computed from the warehouse — nothing is asserted by hand.
"""
from __future__ import annotations
import sys, os, json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import params as P

try:
    import duckdb
except ImportError:
    raise SystemExit("duckdb required")

OUT = P.EDA_DIR
plt.rcParams.update({
    "figure.facecolor": P.WARM_WHITE, "axes.facecolor": P.WARM_WHITE,
    "axes.edgecolor": P.SOFT_GRAY, "axes.labelcolor": P.CHARCOAL,
    "xtick.color": P.CHARCOAL, "ytick.color": P.CHARCOAL,
    "axes.titlecolor": P.NAVY, "font.family": "DejaVu Sans", "font.size": 9,
})


def q(sql: str) -> pd.DataFrame:
    with duckdb.connect(P.DB_PATH, read_only=True) as c:
        return c.execute(sql).fetch_df()


def describe(s: pd.Series) -> dict:
    s = pd.to_numeric(s, errors="coerce").dropna()
    if len(s) == 0:
        return {}
    q_ = s.quantile([.01, .05, .25, .5, .75, .95, .99])
    return dict(count=int(len(s)), mean=float(s.mean()), std=float(s.std()),
                min=float(s.min()), p01=float(q_[.01]), p05=float(q_[.05]),
                q1=float(q_[.25]), median=float(s.median()), q3=float(q_[.75]),
                p95=float(q_[.95]), p99=float(q_[.99]), max=float(s.max()),
                skew=float(s.skew()))


def save_fig(fig, name: str):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return p


def main():
    os.makedirs(OUT, exist_ok=True)
    R: dict = {}
    md = ["# EDA — Mercure Group Data Intelligence (Powered by LensaData)",
          "", "Every figure below is computed from the warehouse marts.",
          "Synthetic demonstration — all values fictional.", ""]

    # ---------------- 1. overview
    md.append("## 1. Dataset Overview")
    tables = ["dim_date", "dim_property", "dim_product", "dim_account",
              "fact_room_sales", "fact_fnb_sales", "fact_inventory",
              "fact_purchase", "fact_expense", "fact_budget"]
    md.append("\n| Table | Rows |")
    md.append("|---|---|")
    counts = {}
    with duckdb.connect(P.DB_PATH, read_only=True) as c:
        for t in tables:
            n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            counts[t] = int(n)
            md.append(f"| `{t}` | {n:,} |")
    R["table_rows"] = counts

    # ---------------- 2. distributions
    md.append("\n## 2. Distributions")
    dist_specs = [
        ("room_revenue", "SELECT room_revenue AS v FROM fact_room_sales WHERE rooms_sold=1"),
        ("adr", "SELECT adr_amount AS v FROM fact_room_sales WHERE rooms_sold=1"),
        ("fnb_net_sales", "SELECT net_sales AS v FROM fact_fnb_sales WHERE is_void=0"),
        ("fnb_check_size", """SELECT SUM(net_sales) AS v FROM fact_fnb_sales
                              WHERE is_void=0 GROUP BY transaction_id"""),
        ("food_cost_pct", """SELECT cogs_amount/NULLIF(net_sales,0)*100 AS v FROM fact_fnb_sales
                             WHERE net_sales>0 AND is_void=0"""),
    ]
    for name, sql in dist_specs:
        s = q(sql)["v"]
        R[f"dist_{name}"] = describe(s)
        md.append(f"\n**{name}**: " + ", ".join(
            f"{k}={v:,.2f}" if isinstance(v, float) else f"{k}={v:,}"
            for k, v in list(R[f"dist_{name}"].items())[:6]))

    fig, axes = plt.subplots(1, 5, figsize=(20, 3.2))
    for ax, (name, sql) in zip(axes, dist_specs):
        s = pd.to_numeric(q(sql)["v"], errors="coerce").dropna()
        ax.hist(s.clip(upper=s.quantile(.99)), bins=40, color=P.NAVY, alpha=.85)
        ax.set_title(name, color=P.NAVY, fontsize=10)
        ax.grid(alpha=.25)
    save_fig(fig, "dist_distributions.png")
    md.append("\n![distributions](dist_distributions.png)")

    # ---------------- 3. time series
    md.append("\n## 3. Time Series")
    daily = q("""SELECT full_date, SUM(total_revenue) AS revenue, AVG(occupancy_pct) AS occupancy,
                        AVG(adr) AS adr
                 FROM mart_kpi_daily GROUP BY 1 ORDER BY 1""")
    R["daily_rows"] = int(len(daily))
    fig, axes = plt.subplots(3, 1, figsize=(15, 8), sharex=True)
    axes[0].plot(daily["full_date"], daily["revenue"] / 1e9, color=P.NAVY, lw=.8)
    axes[0].set_title("Daily Group Revenue (Rp bn)", color=P.NAVY)
    axes[1].plot(daily["full_date"], daily["occupancy"], color=P.GOLD, lw=.8)
    axes[1].set_title("Daily Occupancy %", color=P.NAVY)
    axes[2].plot(daily["full_date"], daily["adr"] / 1000, color=P.CHARCOAL, lw=.8)
    axes[2].set_title("Daily ADR (Rp k)", color=P.NAVY)
    for ax in axes:
        ax.grid(alpha=.25)
    save_fig(fig, "ts_daily.png")
    md.append("\n![daily](ts_daily.png)")

    monthly = q("""SELECT year, month, SUM(total_revenue) AS revenue, SUM(fnb_net_revenue) AS fnb
                   FROM mart_kpi_daily GROUP BY 1, 2 ORDER BY 1, 2""")
    monthly["ym"] = monthly["year"].astype(str) + "-" + monthly["month"].astype(str).str.zfill(2)
    fig, ax = plt.subplots(figsize=(15, 3.6))
    ax.bar(monthly["ym"], monthly["revenue"] / 1e9, color=P.NAVY, label="Total Revenue")
    ax.bar(monthly["ym"], monthly["fnb"] / 1e9, color=P.GOLD, label="F&B Net Revenue")
    ax.set_title("Monthly Revenue (Rp bn)", color=P.NAVY)
    ax.legend(frameon=False, fontsize=8)
    ax.tick_params(axis="x", rotation=70, labelsize=7)
    ax.grid(axis="y", alpha=.25)
    save_fig(fig, "ts_monthly.png")
    md.append("\n![monthly](ts_monthly.png)")
    R["monthly"] = monthly[["ym", "revenue", "fnb"]].to_dict("records")

    # ---------------- 4. segmentation
    md.append("\n## 4. Segmentation")
    segs = {
        "property": """SELECT property_name AS k, SUM(total_revenue) AS v FROM mart_kpi_daily
                       GROUP BY 1 ORDER BY 2 DESC""",
        "channel": """SELECT c.channel_name AS k, SUM(r.room_revenue) AS v FROM fact_room_sales r
                      JOIN dim_channel c ON c.channel_id=r.channel_id GROUP BY 1 ORDER BY 2 DESC""",
        "segment": """SELECT s.segment_name AS k, SUM(r.room_revenue) AS v FROM fact_room_sales r
                      JOIN dim_customer_segment s ON s.segment_id=r.segment_id GROUP BY 1 ORDER BY 2 DESC""",
        "category": """SELECT cat.category_name AS k, SUM(f.net_sales) AS v FROM fact_fnb_sales f
                       JOIN dim_product p ON p.product_id=f.product_id
                       JOIN dim_product_category cat ON cat.category_id=p.category_id
                       GROUP BY 1 ORDER BY 2 DESC""",
    }
    for name, sql in segs.items():
        d = q(sql)
        R[f"seg_{name}"] = d.to_dict("records")
        md.append(f"\n**By {name}**: " + ", ".join(
            f"{r.k}={r.v/1e9:,.2f}bn" for r in d.head(8).itertuples()))
        fig, ax = plt.subplots(figsize=(10, 3.2))
        ax.barh(d["k"][::-1], d["v"][::-1] / 1e9, color=P.NAVY)
        ax.set_title(f"Revenue by {name} (Rp bn)", color=P.NAVY, fontsize=10)
        ax.grid(axis="x", alpha=.25)
        save_fig(fig, f"seg_{name}.png")
        md.append(f"\n![seg {name}](seg_{name}.png)")

    # ---------------- 5. outliers
    md.append("\n## 5. Outliers (statistical)")
    outs = {}
    for name, sql in [
        ("daily_revenue", "SELECT full_date AS k, SUM(total_revenue) AS v FROM mart_kpi_daily GROUP BY 1"),
        ("occupancy", "SELECT full_date AS k, AVG(occupancy_pct) AS v FROM mart_kpi_daily GROUP BY 1"),
        ("food_cost", """SELECT full_date AS k, SUM(fnb_cogs)/NULLIF(SUM(fnb_net_revenue),0)*100 AS v
                         FROM mart_kpi_daily GROUP BY 1"""),
        ("fnb_transactions", "SELECT full_date AS k, SUM(fnb_transactions) AS v FROM mart_kpi_daily GROUP BY 1"),
    ]:
        d = q(sql).dropna()
        v = pd.to_numeric(d["v"], errors="coerce")
        z = (v - v.mean()) / v.std()
        d["z"] = z
        hi = d[z > 3]
        lo = d[z < -3]
        outs[name] = dict(high=hi.to_dict("records"), low=lo.to_dict("records"))
        md.append(f"\n**{name}**: {len(hi)} high outliers (z>3), {len(lo)} low (z<-3)")
    R["outliers"] = outs

    with open(os.path.join(OUT, "eda_summary.json"), "w", encoding="utf-8") as fh:
        json.dump(R, fh, indent=2, default=str)
    with open(os.path.join(OUT, "eda_report.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md))
    print("[10] EDA written to", OUT)


if __name__ == "__main__":
    main()
