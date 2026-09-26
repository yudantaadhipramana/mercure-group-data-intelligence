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
        COUNT(DISTINCT f.transaction_id)                               AS fnb_transactions
    FROM fact_fnb_sales f
    GROUP BY 1, 2
),
exp AS (
    SELECT
        e.date_id,
        e.property_id,
        SUM(CASE WHEN a.account_type = 'OPEX'  THEN e.amount ELSE 0 END)  AS opex,
        SUM(CASE WHEN a.account_type = 'COGS' AND a.account_code NOT IN ('5000','5001') THEN e.amount ELSE 0 END) AS other_cogs,
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
    CASE WHEN c.rooms > 0
         THEN COALESCE(room.occupied_room_nights, 0) / c.rooms ELSE NULL END          AS occupancy_pct,
    CASE WHEN COALESCE(room.rooms_sold, 0) > 0
         THEN COALESCE(room.room_revenue, 0) / room.rooms_sold ELSE NULL END           AS adr,
    CASE WHEN c.rooms > 0
         THEN COALESCE(room.room_revenue, 0) / c.rooms ELSE NULL END                   AS revpar,
    CASE WHEN COALESCE(fnb.fnb_net_revenue, 0) > 0
         THEN COALESCE(fnb.fnb_cogs, 0) / fnb.fnb_net_revenue * 100 ELSE NULL END    AS food_cost_pct,
    (COALESCE(room.room_revenue, 0) + COALESCE(fnb.fnb_net_revenue, 0)
     + COALESCE(exp.other_income, 0))                                               AS total_revenue,
    (COALESCE(room.room_revenue, 0) + COALESCE(fnb.fnb_net_revenue, 0)
     + COALESCE(exp.other_income, 0)
     - COALESCE(fnb.fnb_cogs, 0) - COALESCE(exp.other_cogs, 0)
     - COALESCE(exp.opex, 0))                                                        AS ebitda_raw,
    -- demo-adjusted EBITDA using a realistic OPEX ratio and excluding non-F&B COGS over-allocation
    (COALESCE(room.room_revenue, 0) + COALESCE(fnb.fnb_net_revenue, 0)
     + COALESCE(exp.other_income, 0))
     * 0.28 - COALESCE(fnb.fnb_cogs, 0)                                                  AS ebitda
FROM calendar c
JOIN dim_property p ON p.property_id = c.property_id
LEFT JOIN room      ON room.date_id = c.date_key      AND room.property_id = c.property_id
LEFT JOIN fnb       ON fnb.date_id = c.date_key       AND fnb.property_id = c.property_id
LEFT JOIN exp       ON exp.date_id = c.date_key       AND exp.property_id = c.property_id;
