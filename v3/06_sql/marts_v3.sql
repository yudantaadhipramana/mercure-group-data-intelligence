CREATE OR REPLACE VIEW mart_kpi_daily AS
SELECT
    d.full_date,
    d.date_key,
    p.property_id,
    p.property_name,
    p.region,
    p.class AS hotel_class,
    p.business_type,
    COALESCE(rs.rooms_sold, 0) AS rooms_sold,
    p.rooms AS rooms_available,
    COALESCE(rs.rooms_sold, 0)::DOUBLE / NULLIF(p.rooms, 0) AS occupancy_pct,
    COALESCE(rs.room_revenue, 0) AS room_revenue,
    COALESCE(rs.room_revenue / NULLIF(rs.rooms_sold, 0), 0) AS adr,
    COALESCE(rs.room_revenue / NULLIF(p.rooms, 0), 0) AS revpar,
    COALESCE(fs.fnb_net_revenue, 0) AS fnb_net_revenue,
    COALESCE(fs.fnb_gross, 0) AS fnb_gross,
    COALESCE(fs.fnb_discount, 0) AS fnb_discount,
    COALESCE(fs.fnb_transactions, 0) AS fnb_transactions,
    COALESCE(fs.fnb_cogs, 0) AS fnb_cogs,
    COALESCE(fin.total_expense, 0) AS total_expense,
    COALESCE(fin.total_revenue, 0) - COALESCE(fin.total_expense, 0) AS ebitda,
    COALESCE(room_rev.room_revenue, 0) + COALESCE(fs.fnb_net_revenue, 0) AS total_revenue,
    COALESCE(fnb_cogs_pct.cogs_pct, 0) AS food_cost_pct,
    COALESCE(inv.waste_qty, 0) AS waste_qty
FROM dim_date d
CROSS JOIN dim_property p
LEFT JOIN (
    SELECT date_id, property_id, SUM(rooms_sold) AS rooms_sold, SUM(room_revenue) AS room_revenue
    FROM fact_room_sales
    GROUP BY 1, 2
) rs ON rs.date_id = d.date_key AND rs.property_id = p.property_id
LEFT JOIN (
    SELECT date_id, property_id, SUM(net_sales) AS fnb_net_revenue, SUM(gross_sales) AS fnb_gross, SUM(discount) AS fnb_discount,
           COUNT(DISTINCT transaction_id) AS fnb_transactions, SUM(cogs_amount) AS fnb_cogs
    FROM fact_fnb_sales
    GROUP BY 1, 2
) fs ON fs.date_id = d.date_key AND fs.property_id = p.property_id
LEFT JOIN (
    SELECT date_id, property_id,
           SUM(CASE WHEN a.account_type IN ('Operating Expense', 'COGS') THEN e.amount ELSE 0 END) AS total_expense,
           SUM(CASE WHEN a.account_type = 'Revenue' THEN e.amount ELSE 0 END) AS total_revenue
    FROM fact_expense e
    JOIN dim_account a ON a.account_id = e.account_id
    GROUP BY 1, 2
) fin ON fin.date_id = d.date_key AND fin.property_id = p.property_id
LEFT JOIN (
    SELECT date_id, property_id, SUM(room_revenue) AS room_revenue
    FROM fact_room_sales
    GROUP BY 1, 2
) room_rev ON room_rev.date_id = d.date_key AND room_rev.property_id = p.property_id
LEFT JOIN (
    SELECT date_id, property_id, AVG(cogs_pct) AS cogs_pct
    FROM (SELECT date_id, property_id, SUM(cogs_amount)/NULLIF(SUM(net_sales),0)*100 AS cogs_pct FROM fact_fnb_sales GROUP BY 1,2)
    GROUP BY 1, 2
) fnb_cogs_pct ON fnb_cogs_pct.date_id = d.date_key AND fnb_cogs_pct.property_id = p.property_id
LEFT JOIN (
    SELECT date_id, property_id, SUM(waste_qty) AS waste_qty
    FROM fact_inventory
    GROUP BY 1, 2
) inv ON inv.date_id = d.date_key AND inv.property_id = p.property_id;
