# Mercure Group Data Intelligence Demo — Powered by LensaData

> **Tajam Melihat, Sigap Bertindak**

This repository is a synthetic end-to-end data intelligence demonstration for a fictional hospitality & F&B group, **Mercure Group**. It shows how LensaData transforms fragmented operational data into clean, integrated data, a star-schema data warehouse, and an interactive management dashboard.

## Synthetic Nature Disclaimer

**This project is a synthetic demonstration.** All property names, financial figures, transactions, and operational data are generated for illustration only. They do not represent actual data or systems of any real Mercure Group.

## What This Demo Covers

- Raw synthetic data from 6 sources (PMS, POS, Finance/ERP, Inventory, Procurement, Budget)
- Realistic data quality issues (duplicates, inconsistent names, missing values, bad formats)
- Python + Pandas ETL pipeline
- Star-schema data warehouse in DuckDB
- Data quality gate and validation
- Master data management
- KPI calculation and reconciliation
- Google Sheets integration as a live data backend
- Next.js dashboard deployed to Vercel
- Executive story and documentation

## Live Dashboard

- **Vercel Dashboard:** `https://dashboard-mhrynganu-lensadata.vercel.app`
- **GitHub Repository:** `https://github.com/yudantaadhipramana/mercure-group-data-intelligence`
- **Google Sheets backend:** `1x7RyquXcQ3eFcsGh4R3B7wmCg2XWneHddhtY_nql4mw`

## Folder Structure

```
mercure-group-data-intelligence/
├── 01_raw_data/          # Synthetic raw sources
├── 02_staging/           # Staged parquet files
├── 03_cleaned_data/      # Cleaned data outputs
├── 04_master_data/       # Master / dimension / mapping tables
├── 05_etl/               # Python ETL scripts
├── 06_data_warehouse/    # DuckDB warehouse
├── 07_sql/               # SQL DDL and mart scripts
├── 08_eda/               # EDA outputs
├── 09_dashboard/         # Dashboard assets
├── 10_forecasting/       # Forecast scripts
├── 11_anomaly_detection/ # Anomaly detection scripts
├── 12_documentation/     # BRD, specs, data dictionary
├── apps-script/          # Google Apps Script for Sheets API
├── dashboard/            # Next.js dashboard
└── README.md
```

## Technology Stack

- **Python 3.11**, Pandas, NumPy, DuckDB
- **Next.js 16**, React, TypeScript, Tailwind CSS, Recharts
- **Google Sheets API** (backend data store)
- **GitHub** + **Vercel** (CI/CD and hosting)
- **Google Apps Script** (Sheets read/write)

## How to Reproduce

```bash
cd 05_etl
python generate_raw_pms_pos.py
python generate_raw_others.py
python 01_extract.py
python 02_profile.py
python 00_build_master.py
python 03_clean_map.py
python 07_validate.py
python 08_load.py
python 13_push_sheets.py
```

Then build and deploy the dashboard:

```bash
cd ../dashboard
npm install
npm run build
vercel --prod --scope=lensadata
```

## Key KPIs

| KPI | Source |
|---|---|
| Total Revenue | Room Revenue + F&B Net Sales |
| Occupancy % | Rooms Sold / Available Room Nights |
| ADR | Room Revenue / Rooms Sold |
| RevPAR | Room Revenue / Available Room Nights |
| Food Cost % | F&B COGS / F&B Net Sales |
| Gross Margin % | Gross Profit / Net Revenue |

## Contact

Built by **LensaData**.
