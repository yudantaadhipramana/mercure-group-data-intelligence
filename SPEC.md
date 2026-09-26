# Hospitality & F&B Group Data Intelligence Demo — Specification

**Project:** Mercure Group Data Intelligence Demo — Powered by LensaData  
**Tagline:** Tajam Melihat, Sigap Bertindak  
**Version:** 2.0 (full rebuild)  
**Date:** 2026-09-26  
**Status:** Synthetic demonstration  

---

## 1. Objective

Rebuild a complete, end-to-end data intelligence demonstration that shows how LensaData turns fragmented, dirty operational data from a fictional hospitality & F&B group into trusted data, analytics, and decision support.

## 2. Scope

This rebuild covers:

- Synthetic raw data generation (PMS, POS, Finance/ERP, Inventory, Procurement, Budget)
- Data profiling, cleansing, master-data mapping, and ETL
- Data quality framework with computed metrics
- Star-schema data warehouse (DuckDB for local execution; PostgreSQL DDL for production target)
- EDA, forecasting, anomaly detection, and AI insights
- Multi-page Next.js dashboard with executive, property, hotel, F&B, finance, inventory, data quality, EDA, and forecast/anomaly views
- Google Sheets + Apps Script integration layer (attempted; OAuth/permission blockers documented)
- Vercel deployment (attempted; auth blockers documented)
- Automated tests, reconciliation, and full documentation

## 3. Architecture

```text
Synthetic Sources (CSV)
         ↓
01_raw_data  (write-once evidence)
         ↓
02_staging   (typed, trimmed)
         ↓
03_cleaned_data (mapped, deduped, validated)
         ↓
04_master_data (dimensions + alias maps)
         ↓
06_data_warehouse (DuckDB star schema + marts)
         ↓
08_eda, 10_forecasting, 11_anomaly_detection
         ↓
09_dashboard/dashboard_data.json
         ↓
dashboard/ (Next.js static export)
         ↓
Vercel (when auth available)
```

## 4. Technology Stack

| Layer | Tool |
|-------|------|
| Language | Python 3.11 |
| Data | pandas, numpy, pyarrow |
| Warehouse | DuckDB (embedded) |
| Dashboard | Next.js 16, React 19, TypeScript, Tailwind 4, recharts |
| Sheets/Apps Script | Google Apps Script (clasp) — blocked by OAuth |
| Deployment | Vercel CLI — blocked by auth |
| Tests | pytest |

## 5. Business Entities

- 7 hotel properties + 2 F&B business units
- Group → Business Type → Property → Department → Category → Product
- Sources: PMS bookings, POS transactions, Finance/ERP GL, inventory, procurement, budget

## 6. KPI Definitions

- **Occupancy** = occupied room nights / available room nights × 100
- **ADR** = room revenue / rooms sold
- **RevPAR** = room revenue / available room nights
- **Average Check** = net F&B sales / transactions
- **Food Cost %** = food COGS / applicable F&B revenue × 100
- **Gross Profit** = net revenue − COGS
- **Gross Margin** = gross profit / net revenue × 100
- **EBITDA** = operating profit before D&A, interest, tax (documented account mapping)
- **Budget Achievement** = actual / budget × 100

## 7. Non-Functional Requirements

- Reproducible: deterministic seed
- Computed metrics only: no hardcoded KPIs
- Tests for ETL, quality gates, reconciliation
- Documentation for architecture, data model, KPIs, and deployment
- Security: no secrets in repo

## 8. Acceptance Criteria

- `python run_all.py --gen` completes without error
- Data quality gate passes (≥ 95% mapped, 0 orphan facts)
- DuckDB warehouse builds and marts queryable
- Dashboard JSON generated
- Next.js build succeeds as static export
- Reconciliation report shows differences within tolerance
- Tests pass
