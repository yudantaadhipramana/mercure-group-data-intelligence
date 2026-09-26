# SPEC.md — Mercure Group Data Intelligence Demo v3
**Powered by LensaData** — *Tajam Melihat, Sigap Bertindak*

## 1. Executive Command
Rebuild the entire demo from first principles. The previous v2 output was superficial. This v3 must be:
- **Data-realistic**: multi-source hospitality & F&B raw data with genuine schema/format variation and controlled dirtiness.
- **ETL-demonstrative**: a full Python → DuckDB pipeline plus a real Google Apps Script ETL inside Sheets.
- **Analytics-rich**: star-schema warehouse, KPIs, forecast, anomaly detection, evidence-based insights.
- **Dashboard-premium**: a Next.js web app with role-based navigation and a design inspired by the Gacoan product-audit dashboard and the National Zakat offline dashboard.
- **Deploy-ready**: Vercel + Apps Script + documented Google Sheets structure.

## 2. Business Context
**Mercure Group** (fictional): 7 hotels + 2 standalone F&B business units across Indonesia.
Properties: Jakarta, Bandung, Surabaya, Yogyakarta, Bali, Semarang, Malang.

**Pain points**:
- Data fragmented across branch-level POS and ERP systems.
- Different branches use different naming, column names, date formats, decimal styles.
- Manual consolidation for group reporting.
- No visibility into cross-property performance.
- Food cost, occupancy, and revenue leakages not detected automatically.
- Budget vs actual only available weeks after month-end.

**User personas**:
- **BOD / Executive**: high-level group KPIs, trends, alerts, strategic decisions.
- **Regional / Property Manager**: property-level P&L, occupancy, RevPAR, benchmarks.
- **F&B Manager**: category mix, food cost %, waste, outlet performance.
- **Finance Controller**: P&L, budget variance, cash flow signals.
- **Data / IT**: data quality, ETL monitoring, source health.

## 3. Source Systems (explicit, realistic)
Each branch has its own POS/ERP. We define 6 fictional source systems with **different schemas**.

### 3.1 PMS-HOTEL-01 (Jakarta, Surabaya, Bali)
File: `RAW_PMS_BOOKINGS_H01.csv`
Columns: `booking_id, hotel_name, booking_date, check_in, check_out, room_type, guest_segment, channel, room_rate_idr, room_revenue_idr, status, payment_status`
Date format: `DD/MM/YYYY`
Numeric: `1.234.567,89` (ID)
Dirtiness: alias names, mixed case, blank optional fields, duplicate booking_id, impossible dates.

### 3.2 PMS-HOTEL-02 (Bandung, Yogyakarta)
File: `RAW_PMS_BOOKINGS_H02.csv`
Columns: `reservation_number, property_code, arrival_date, departure_date, room_category, market_segment, distribution_channel, adr, revenue, reservation_status, paid`
Date format: `YYYY-MM-DD`
Numeric: `1,234,567.89` (EN)
Dirtiness: property_code instead of name, different room categories, missing segment.

### 3.3 PMS-HOTEL-03 (Semarang, Malang)
File: `RAW_PMS_BOOKINGS_H03.xlsx` (we export as .csv for pipeline: `RAW_PMS_BOOKINGS_H03.csv`)
Columns: `ID, Hotel, Date In, Date Out, Type, Segment, Channel, Rate, Rev, Cancelled, Paid`
Date format: `DD-MMM-YYYY`
Numeric: plain integer
Dirtiness: all-caps names, missing headers, blank rows.

### 3.4 POS-FNB-01 (The Grand Table hotel outlets)
File: `RAW_POS_FNB_01.csv`
Columns: `tx_id, date, outlet_name, item_code, item_name, category, qty, gross, disc, net, pay_method, void, refund`
Date format: `DD/MM/YYYY`
Numeric: ID

### 3.5 POS-FNB-02 (specialty / food hall / casual dining)
File: `RAW_POS_FNB_02.csv`
Columns: `transaction_id, transaction_date, outlet, sku, product, product_group, quantity, gross_sales, discount, net_sales, payment_type, is_void, is_refund`
Date format: `YYYY-MM-DD`
Numeric: EN

### 3.6 ERP-FIN-01
File: `RAW_FINANCE_GL.csv`
Columns: `txn_id, date, branch, gl_account, account_name, dept, amount, dc`
Date format: `YYYY-MM-DD`
Numeric: mixed
Dirtiness: invalid gl_account codes, malformed account names, missing dept.

### 3.7 INV-SYSTEM-01
File: `RAW_INVENTORY.csv`
Columns: `date, branch, sku, item_name, opening, purchase, transfer, consumption, waste, closing, stock_value`
Date format: `DD/MM/YYYY`
Numeric: EN

### 3.8 PROCUREMENT-01
File: `RAW_PROCUREMENT.csv`
Columns: `po_id, po_date, vendor, branch, sku, item, qty, unit_price, total`
Date format: `YYYY-MM-DD`
Numeric: plain

### 3.9 BUDGET-01
File: `RAW_BUDGET.csv`
Columns: `period, branch, account_code, account_name, department, budget_amount`
Date format: `YYYY-MM-DD` (first of month)
Numeric: plain

## 4. Data Volume
Period: Jan 2025 – Dec 2026 (731 days).
- PMS booking lines: ~150k
- POS lines: ~1.4M
- Finance lines: ~7.5k
- Inventory daily: ~150k
- Procurement: ~16k
- Budget: ~7.5k

## 5. Master Data & Mapping
- `MASTER_PROPERTY`: property_id, property_name, city, region, business_type, rooms, opening_date, status
- `MASTER_PRODUCT`: product_id, standard_name, category_id, unit_cost_ratio
- `MASTER_ACCOUNT`: account_id, account_code, account_name, account_type, department_id
- `MASTER_MAPPING`: source_system, source_entity, source_code, source_name, canonical_id, status
- `MASTER_DEPARTMENT`, `MASTER_CATEGORY`, `MASTER_SUPPLIER`, `MASTER_CHANNEL`, `MASTER_SEGMENT`, `MASTER_ROOM_TYPE`

## 6. ETL Pipeline (Python + DuckDB)
Stage 01: Generate raw per-source-system files.
Stage 02: Extract to staging parquet (preserve _source_system, _source_file).
Stage 03: Profile raw data.
Stage 04: Clean per source system.
  - Header normalization per source system
  - Date standardization
  - Numeric standardization (ID/EN/plain)
  - Property/product/account mapping
  - Deduplication
  - Business-rule validation
Stage 05: Build master data + mapping tables.
Stage 06: Load star schema into DuckDB.
Stage 07: SQL marts (KPI daily, hotel monthly, F&B monthly, finance monthly, budget vs actual).
Stage 08: Data quality report.
Stage 09: EDA outputs.
Stage 10: Forecast (90-day).
Stage 11: Anomaly detection.
Stage 12: Insights.
Stage 13: Dashboard payload.
Stage 14: Reconciliation.
Stage 15: Push to Google Sheets (when auth available).

## 7. Data Quality Framework
Dimensions: completeness, validity, uniqueness, consistency, integrity.
Per source: quality_score, dq_tier, status.
Logs: `DATA_CLEANSING_LOG`, `DATA_QUALITY_RESULTS`, `DATA_QUALITY_ISSUES`, `ETL_RECONCILIATION`.

## 8. Google Sheets Structure
### Control & Docs
- 00_README
- 01_CONTROL_PANEL
- 02_DATA_DICTIONARY
- 03_ETL_RUN_LOG

### Raw
- RAW_PMS_BOOKINGS_H01
- RAW_PMS_BOOKINGS_H02
- RAW_PMS_BOOKINGS_H03
- RAW_POS_FNB_01
- RAW_POS_FNB_02
- RAW_FINANCE_GL
- RAW_INVENTORY
- RAW_PROCUREMENT
- RAW_BUDGET

### Staging & Clean
- STG_* (one per raw)
- CLEAN_*

### Master
- MASTER_PROPERTY, MASTER_DEPARTMENT, MASTER_PRODUCT, MASTER_PRODUCT_CATEGORY, MASTER_ACCOUNT, MASTER_CHANNEL, CUSTOMER_SEGMENT, ROOM_TYPE, SUPPLIER, MAPPING

### Analytics
- DIM_DATE, DIM_PROPERTY, DIM_ACCOUNT, DIM_PRODUCT, DIM_DEPARTMENT
- FACT_ROOM_SALES, FACT_FNB_SALES, FACT_INVENTORY, FACT_PURCHASE, FACT_EXPENSE, FACT_BUDGET
- MART_KPI_DAILY, MART_HOTEL_MONTHLY, MART_FNB_MONTHLY, MART_FINANCE_MONTHLY, MART_BUDGET_VS_ACTUAL

### EDA / Quality
- EDA_DATA_PROFILE, EDA_STATISTICS, EDA_TRENDS, EDA_SEGMENTATION, EDA_OUTLIERS
- DATA_QUALITY_RESULTS, DATA_QUALITY_ISSUES, DATA_CLEANSING_LOG, ETL_RECONCILIATION

### Dashboard
- KPI, REVENUE_TREND, PROPERTY_PERFORMANCE, FNB_PERFORMANCE, FORECAST, ANOMALY, INSIGHTS, DATA_QUALITY

## 9. Apps Script Backend (real ETL in Sheets)
Modules:
- Config.gs
- Menu.gs
- Utils.gs
- SyntheticDataGenerator.gs (schema only; actual data via API push or manual paste)
- RawDataService.gs (read raw sheets)
- StagingService.gs (normalize per source system)
- MasterDataService.gs (load master sheets)
- MappingService.gs (alias → canonical)
- CleansingService.gs (clean raw into clean sheets)
- ETLService.gs (run raw→clean)
- DataQualityService.gs
- ReconciliationService.gs
- AnalyticsService.gs (build analytical sheets from clean sheets)
- DashboardApi.gs (doGet API for web dashboard)
- AutomationService.gs (triggers)
- LoggingService.gs
- TestService.gs

## 10. Frontend (Next.js)
Stack: Next.js 16, TypeScript, Tailwind CSS v4, Recharts.
Design system: Deep navy (#0B1F3A), champagne gold (#C9A227), warm white, charcoal, soft gray.

Pages (role-aware):
1. Executive — group KPIs, revenue trend, property ranking, anomaly alerts, top insights.
2. BOD — strategic view: YoY growth, budget achievement, EBITDA bridge, risk matrix.
3. Property Manager — per-property P&L, occupancy/ADR/RevPAR, benchmark.
4. F&B Manager — category mix, food cost %, outlet ranking, waste & discount.
5. Finance — P&L, budget vs actual, variance, cash flow signals.
6. Inventory — stock movement, purchase price, waste, reorder signals.
7. Data Quality — ETL monitoring, source health, issue drill-down.
8. Forecast & Anomaly — 90-day forecast, detected anomalies.

Shared:
- Sidebar navigation with role labels.
- Filter bar: period, property, business type, outlet.
- Premium cards with status colors.
- Tables with sortable columns.
- Tooltips and loading states.

## 11. KPI Dictionary
- Total Revenue = Room Revenue + Net F&B Revenue + Other Income
- EBITDA = Total Revenue − COGS − OPEX
- Occupancy = Occupied Room Nights / Available Room Nights
- ADR = Room Revenue / Rooms Sold
- RevPAR = Room Revenue / Available Room Nights
- Food Cost % = F&B COGS / Net F&B Revenue
- Average Check = Net F&B Sales / Transactions
- Budget Achievement = Actual / Budget

## 12. Acceptance Criteria
- All pipeline stages run end-to-end without error.
- Raw data clearly shows different schemas per source system.
- DuckDB warehouse has star schema with RI checks passing.
- Dashboard builds and deploys to Vercel.
- Apps Script pushes and menu works.
- Google Sheets structure created with all required sheets.
- Data quality scores calculated from actual data.
- Forecast non-zero and anomalies detected algorithmically.
- Insights include metric, period, evidence, interpretation, investigation.

## 13. Deliverables
- SPEC.md, IMPLEMENTATION_PLAN.md, ARCHITECTURE.md, README.md
- Python ETL pipeline
- DuckDB warehouse
- Next.js dashboard source
- Apps Script source
- FINAL_DELIVERY_REPORT.md
- Live Vercel URL
- Apps Script deployment URL (after manual deploy step)
