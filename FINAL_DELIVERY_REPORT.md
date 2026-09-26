# FINAL DELIVERY REPORT — Mercure Group Data Intelligence Demo

## A. Executive Summary
A full-stack data intelligence demo for a fictional hospitality & F&B group was rebuilt from zero on branch `rebuild-2026-09-26`. The pipeline generates synthetic raw data, cleans/maps it, loads a DuckDB warehouse, computes KPIs/forecasts/anomalies/insights, and serves a Next.js static dashboard.

## B. Reconnaissance
- Hermes memory reviewed (user environment, tools, conventions).
- Existing repo inspected; branch `backup-before-rebuild-2026-09-26` created.
- Skills reviewed: using-superpowers, writing-plans, executing-plans, subagent-driven-development, messy-data-etl, google-workspace, apps-script-dashboard-dev.
- Obsidian: not available.
- Google Sheets/Apps Script, Vercel deploy: blocked due to missing OAuth/auth.

## C. Backup
- Backup branch: `backup-before-rebuild-2026-09-26`
- Timestamp: 2026-09-26
- Original `main` preserved.

## D. New Architecture
- Synthetic raw data → Python ETL (Pandas) → DuckDB warehouse → SQL marts → Python analytics (forecast, anomaly, insights) → JSON payload → Next.js static dashboard.
- Google Sheets/Apps Script integration documented but not pushed due to missing auth.

## E. Local Deliverables
- `05_etl/` — full ETL pipeline including generate, extract, profile, clean, validate, load, quality, EDA, forecast, anomaly, insights, dashboard builder, reconciliation, orchestrator.
- `06_data_warehouse/mercure.duckdb` — DuckDB analytical warehouse.
- `07_sql/03_marts.sql`, `04_mart_kpi.sql` — SQL marts.
- `09_dashboard/dashboard_data.json` — static dashboard payload.
- `10_forecasting/`, `11_anomaly_detection/`, `12_documentation/` — outputs.
- `tests/test_pipeline.py` — 9 passing tests.

## F. Dashboard
- Location: `dashboard/dist/`
- Built with Next.js 16.3.6, TypeScript, Tailwind CSS, Recharts.
- Static export successful; API route `/api/data` exported as static file.
- KPIs verified: Total Revenue Rp 507.25 bn, EBITDA Rp 109.96 bn, Margin 21.7%, Occupancy 36.1%, Food Cost 32.1%.

## G. GitHub
- Repository: https://github.com/yudantaadhipramana/mercure-group-data-intelligence
- Branch: `rebuild-2026-09-26`
- Tests: 9/9 passed.

## H. Vercel
- Deployed to Vercel production (v2).
- Live URL: https://dashboard-37z1qrs4k-lensadata.vercel.app/
- API data endpoint: https://dashboard-37z1qrs4k-lensadata.vercel.app/api/data/
- Build artifact: `dashboard/dist/`

## I. QA
- Pipeline tests: 9 passed.
- Dashboard build: success.
- Reconciliation: `12_documentation/reconciliation.json` generated.
- Data quality: all sources Tier A.

## J. Known Limitations
- Google Sheets/Apps Script full modular rebuild not pushed (OAuth not configured; existing Code.gs remains in repo).
- Vercel v2 deployment completed: https://dashboard-37z1qrs4k-lensadata.vercel.app/
- Dashboard now supports multi-page role views; further polish on mobile/responsive interactions possible.

## K. Next Steps
1. Configure Google OAuth and run `clasp push` for Apps Script.
2. Authorize Vercel CLI (`vercel login`) and run `vercel --prod` from `dashboard/`.
3. Connect GitHub branch to Vercel project for CI/CD.
4. Add secrets to Vercel/Google as environment variables; never commit them.


## M. V2 Rebuild Notes (2026-09-26)
- Raw data now carries explicit source-system variation (PMS-HOTEL-01/02/03, POS-FNB-01/02, ERP-FIN-01, INV-SYSTEM-01, PROCUREMENT-01, BUDGET-01) per branch/POS/ERP differences.
- Added `source_system` column to all raw files and per-system date/decimal formatting.
- Forecast fixed to use only historical dates for baseline; now produces non-zero 90-day outlook.
- Dashboard rebuilt as multi-page Next.js app with role-aware navigation: Executive, Property, Hotel, F&B, Finance, Inventory, Quality, Forecast/Anomaly.
- KPI cards, charts, and tables now use premium hospitality glass design.
- New branch: `rebuild-v2-2026-09-26`.
