# SOLUTION ARCHITECTURE

## Logical Flow

```
01_raw_data      → raw CSV evidence (untouched)
02_staging       → typed, trimmed, schema-named
03_cleaned_data  → mapped, deduped, validated
04_master_data   → dimensions + alias maps
06_data_warehouse→ DuckDB star schema + marts
08_eda           → profiling, statistics, segmentation, outliers
10_forecasting   → 90-day forecast for revenue, occupancy, F&B sales
11_anomaly_detection → z-score / IQR / rolling-baseline alerts
09_dashboard     → dashboard_data.json + static HTML dashboards
dashboard/       → Next.js multi-page application
```

## Star Schema

### Dimensions
- dim_date
- dim_property
- dim_business_unit
- dim_department
- dim_product
- dim_product_category
- dim_customer_segment
- dim_channel
- dim_account
- dim_supplier
- dim_room_type

### Facts
- fact_room_sales (grain: booking line)
- fact_room_inventory (grain: property × room_type × date)
- fact_fnb_sales (grain: POS line)
- fact_inventory (grain: property × product × date)
- fact_purchase (grain: purchase line)
- fact_expense (grain: finance transaction)
- fact_budget (grain: property × department × account × month)

## Data Quality Framework

- Completeness, validity, uniqueness, consistency, integrity
- Computed scores per source and rule
- Gate: fail if mapping < 95% or orphan facts > 0

## Dashboard Pages

1. Executive Overview
2. Property Performance
3. Hotel Analytics
4. F&B Analytics
5. Finance
6. Inventory
7. Data Quality & ETL Monitoring
8. EDA & Data Profiling
9. Forecast & Anomaly

## Security & Deployment

- No secrets in repo
- Static export to Vercel when authenticated
- Google Sheets integration via Apps Script web app when OAuth available
