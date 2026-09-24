===============================================================================
 MERCURE GROUP — MART VIEWS (single source of truth for every consumer)
 Hospitality & F&B Group Data Intelligence Demo — Powered by LensaData
===============================================================================
Every dashboard, forecast, anomaly check, insight, and the reconciliation
report read these views. Nothing recomputes from raw.

DuckDB-executed; PostgreSQL-portable (identical logic).
===============================================================================

-- ===========================================================================
-- MART 1 — KPI DAILY (group + property grain)
-- ===========================================================================
CREATE OR REPLACE VIEW mart_kpi_daily AS
WITH room AS (
    SELECT
        r.date_id,
        r.property_id,
        SUM(r.room_revenue)                                          AS room_revenue,
        SUM(r.room_nights)                                           AS occupied_room_nights,
        SUM(r.rooms_sold)                                            AS rooms_sold,
        SUM(r.is_cancelled)                                          AS cancellations,
        SUM(r.is_no_show)                                            AS no_shows,
        COUNT(*)                                                     AS bookings
    FROM fact_room_sales r
    GROUP BY 1, 2
),
fnb AS (
    SELECT
        f.date_id,
        f.property_id,
        SUM(f.gross_sales)                                           AS fnb_gross_sales,
        SUM(CASE WHEN f.is_void = 0 AND f.is_refund = 0
                 THEN f.net_sales ELSE 0 END)                         AS fnb_net_revenue,
        SUM(f.cogs_amount)                                           AS fnb_cogs,
        SUM(f.discount)                                              AS fnb_discount,
        SUM(CASE WHEN f.is_void = 1 THEN 1 ELSE 0 END)               AS void_lines,
        COUNT(*)                                                     AS fnb_lines,
        COUNT(DISTINCT f.transaction_id)                             AS fnb_transactions
    FROM fact_fnb_sales f
    GROUP BY 1, 2
),
exp AS (
    SELECT
        e.date_id,
        e.property_id,
        SUM(CASE WHEN a.account_type = 'OPEX'  THEN e.amount ELSE 0 END)  AS opex,
        SUM(CASE WHEN a.account_type = 'COGS'  THEN e.amount ELSE 0 END)  AS other_cogs,
        SUM(CASE WHEN a.account_type = 'Revenue'
                  AND a.account_code IN ('4002','4003','4005','4006')
                 THEN e.amount ELSE 0 END)                            AS other_income
    FROM fact_expense e
    JOIN dim_account a ON a.account_id = e.account_id
    GROUP BY 1, 2
),
calendar AS (
    SELECT d.date_key, d.full_date, d.year, d.month, d.quarter,
           d.is_weekend, d.is_holiday_flag, p.property_id,
           (p.rooms * 1.0)                                           AS rooms
    FROM dim_date d
    CROSS JOIN dim_property p
    WHERE p.business_type = 'Hotel'
)
SELECT
    c.date_key,
    c.full_date,
    c.year, c.month, c.quarter, c.is_weekend, c.is_holiday_flag,
    c.property_id,
    p.property_name,
    p.business_type,
    COALESCE(room.room_revenue, 0)                                   AS room_revenue,
    COALESCE(room.occupied_room_nights, 0)                           AS occupied_room_nights,
    COALESCE(room.rooms_sold, 0)                                     AS rooms_sold,
    COALESCE(room.cancellations, 0)                                  AS cancellations,
    COALESCE(room.no_shows, 0)                                       AS no_shows,
    COALESCE(room.bookings, 0)                                       AS bookings,
    COALESCE(fnb.fnb_gross_sales, 0)                                 AS fnb_gross_sales,
    COALESCE(fnb.fnb_net_revenue, 0)                                 AS fnb_net_revenue,
    COALESCE(fnb.fnb_cogs, 0)                                        AS fnb_cogs,
    COALESCE(fnb.fnb_discount, 0)                                    AS fnb_discount,
    COALESCE(fnb.fnb_transactions, 0)                                AS fnb_transactions,
    COALESCE(fnb.void_lines, 0)                                      AS void_lines,
    COALESCE(fnb.fnb_lines, 0)                                       AS fnb_lines,
    COALESCE(exp.opex, 0)                                            AS opex,
    COALESCE(exp.other_cogs, 0)                                      AS other_cogs,
    COALESCE(exp.other_income, 0)                                    AS other_income,
    -- KPIs (denominator-guarded)
    CASE WHEN c.rooms > 0
         THEN COALESCE(room.occupied_room_nights, 0) / c.rooms ELSE NULL END          AS occupancy_pct,
    CASE WHEN COALESCE(room.rooms_sold, 0) > 0
         THEN COALESCE(room.room_revenue, 0) / room.rooms_sold ELSE NULL END           AS adr,
    CASE WHEN c.rooms > 0
         THEN COALESCE(room.room_revenue, 0) / c.rooms ELSE NULL END                   AS revpar,
    CASE WHEN COALESCE(fnb.fnb_net_revenue, 0) > 0
         THEN COALESCE(fnb.fnb_cogs, 0) / fnb.fnb_net_revenue * 100 ELSE NULL END      AS food_cost_pct,
    (COALESCE(room.room_revenue, 0) + COALESCE(fnb.fnb_net_revenue, 0)
     + COALESCE(exp.other_income, 0))                                                 AS total_revenue,
    (COALESCE(room.room_revenue, 0) + COALESCE(fnb.fnb_net_revenue, 0)
     + COALESCE(exp.other_income, 0)
     - COALESCE(fnb.fnb_cogs, 0) - COALESCE(exp.other_cogs, 0)
     - COALESCE(exp.opex, 0))                                                         AS ebitda
FROM calendar c
JOIN dim_property p ON p.property_id = c.property_id
LEFT JOIN room      ON room.date_id = c.date_key      AND room.property_id = c.property_id
LEFT JOIN fnb       ON fnb.date_id = c.date_key       AND fnb.property_id = c.property_id
LEFT JOIN exp       ON exp.date_id = c.date_key       AND exp.property_id = c.property_id;


-- ===========================================================================
-- MART 2 — HOTEL MONTHLY
-- ===========================================================================
CREATE OR REPLACE VIEW mart_hotel_monthly AS
SELECT
    d.year, d.month, p.property_id, p.property_name, p.city,
    SUM(k.room_revenue)            AS room_revenue,
    SUM(k.occupied_room_nights)    AS occupied_room_nights,
    SUM(k.rooms_sold)              AS rooms_sold,
    SUM(k.bookings)                AS bookings,
    SUM(k.cancellations)           AS cancellations,
    SUM(k.no_shows)                AS no_shows,
    COUNT(*)                       AS days_in_period,
    SUM(k.room_revenue)
        / NULLIF(SUM(k.occupied_room_nights), 0)                              AS adr,
    SUM(k.occupied_room_nights)
        / NULLIF(SUM(CASE WHEN k.business_type = 'Hotel' THEN 1 ELSE 0 END) * 200, 0) AS occupancy_pct,
    SUM(k.room_revenue)
        / NULLIF(SUM(CASE WHEN k.business_type = 'Hotel' THEN 1 ELSE 0 END) * 200, 0) AS revpar,
    SUM(k.cancellations) / NULLIF(SUM(k.bookings), 0) * 100                   AS cancellation_pct,
    SUM(k.no_shows)      / NULLIF(SUM(k.bookings), 0) * 100                   AS noshow_pct
FROM mart_kpi_daily k
JOIN dim_date d     ON d.date_key = k.date_key
JOIN dim_property p ON p.property_id = k.property_id
WHERE p.business_type = 'Hotel'
GROUP BY 1, 2, 3, 4, 5;


-- ===========================================================================
-- MART 3 — F&B MONTHLY (property × outlet × month)
-- ===========================================================================
CREATE OR REPLACE VIEW mart_fnb_monthly AS
SELECT
    d.year, d.month, f.property_id, p.property_name, f.outlet_name,
    cat.category_name                                                AS category,
    SUM(f.gross_sales)                                               AS gross_sales,
    SUM(CASE WHEN f.is_void = 0 AND f.is_refund = 0
             THEN f.net_sales ELSE 0 END)                            AS net_revenue,
    SUM(f.cogs_amount)                                               AS cogs,
    SUM(f.discount)                                                  AS discount,
    SUM(CASE WHEN f.is_void = 1 THEN 1 ELSE 0 END)                   AS void_lines,
    SUM(CASE WHEN f.is_refund = 1 THEN 1 ELSE 0 END)                 AS refund_lines,
    COUNT(*)                                                         AS lines,
    COUNT(DISTINCT f.transaction_id)                                 AS transactions,
    SUM(CASE WHEN f.is_void = 0 AND f.is_refund = 0
             THEN f.net_sales ELSE 0 END)
        / NULLIF(COUNT(DISTINCT f.transaction_id), 0)                AS average_check,
    SUM(f.cogs_amount) / NULLIF(SUM(f.net_sales), 0) * 100           AS food_cost_pct,
    (SUM(CASE WHEN f.is_void = 0 AND f.is_refund = 0 THEN f.net_sales ELSE 0 END)
     - SUM(f.cogs_amount))                                           AS gross_profit
FROM fact_fnb_sales f
JOIN dim_date d       ON d.date_key = f.date_id
JOIN dim_property p   ON p.property_id = f.property_id
JOIN dim_product pr   ON pr.product_id = f.product_id
JOIN dim_product_category cat ON cat.category_id = pr.category_id
GROUP BY 1, 2, 3, 4, 5, 6;


-- ===========================================================================
-- MART 4 — FINANCE MONTHLY (property × account type)
-- ===========================================================================
CREATE OR REPLACE VIEW mart_finance_monthly AS
SELECT
    d.year, d.month, e.property_id, p.property_name,
    a.account_type, a.account_name, dep.department_name,
    SUM(e.amount)                                                    AS amount
FROM fact_expense e
JOIN dim_date d       ON d.date_key = e.date_id
JOIN dim_property p   ON p.property_id = e.property_id
JOIN dim_account a    ON a.account_id = e.account_id
JOIN dim_department dep ON dep.department_id = e.department_id
GROUP BY 1, 2, 3, 4, 5, 6, 7;


-- ===========================================================================
-- MART 5 — BUDGET vs ACTUAL (property × department × account × month)
-- ===========================================================================
CREATE OR REPLACE VIEW mart_budget_vs_actual AS
SELECT
    d.year, d.month, b.property_id, p.property_name,
    dep.department_name, a.account_name, a.account_type,
    SUM(b.budget_amount)                                             AS budget_amount,
    SUM(CASE WHEN a.account_type = 'Revenue' THEN COALESCE(act.amount, 0)
             ELSE 0 END)                                             AS actual_revenue,
    SUM(CASE WHEN a.account_type = 'OPEX' THEN COALESCE(act.amount, 0)
             ELSE 0 END)                                             AS actual_opex,
    SUM(CASE WHEN a.account_type = 'COGS' THEN COALESCE(act.amount, 0)
             ELSE 0 END)                                             AS actual_cogs
FROM fact_budget b
JOIN dim_date d         ON d.date_key = b.date_id
JOIN dim_property p     ON p.property_id = b.property_id
JOIN dim_department dep ON dep.department_id = b.department_id
JOIN dim_account a      ON a.account_id = b.account_id
LEFT JOIN (SELECT date_id, property_id, account_id, SUM(amount) AS amount
           FROM fact_expense GROUP BY 1, 2, 3) act
       ON act.date_id = b.date_id AND act.property_id = b.property_id
      AND act.account_id = b.account_id
GROUP BY 1, 2, 3, 4, 5, 6, 7;


-- ===========================================================================
-- MART 6 — DATA QUALITY / SOURCE HEALTH
-- (populated by 09_quality_report.py — values computed, never hardcoded)
-- ===========================================================================
CREATE OR REPLACE VIEW mart_dq_source_health AS
SELECT
    source, source_system, records_total, records_clean,
    completeness_pct, uniqueness_pct, validity_pct, consistency_pct,
    integrity_pct, duplicate_rate_pct, mapping_completion_pct,
    failed_records, latest_record_date, freshness_days,
    quality_score, dq_tier, status
FROM dq_source_health;
===============================================================================
