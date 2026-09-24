# TECHNICAL SPECIFICATION
# Hospitality & F&B Group Data Intelligence Demo — Powered by LensaData
**Version 1.0** · Fictional client: Mercure Group · Synthetic data

---

## 1. OBJECTIVE

Prove, end-to-end, that LensaData converts six fragmented, dirty operational sources into a trusted warehouse and management decision support — with forecasting, anomaly detection, and a data-quality product surface.

---

## 2. SYSTEM CONTEXT & DEVIATIONS

| Prompt requirement | This build | Rationale |
|---|---|---|
| PostgreSQL data warehouse | **DDL authored for PostgreSQL** (production target); warehouse **executed on DuckDB** (embedded, zero-install, PostgreSQL-compatible dialect) | No PostgreSQL server, docker, or package admin on host. Design unchanged; DDL portable. |
| Power BI dashboard | **Semantic model + full DAX library as specification** (relationships, cardinality, filter direction, measures). **Live dashboard delivered as self-contained HTML** engineered to the semantic model 1:1. | No Power BI Desktop on host. |
| Prophet forecasting | **statsmodels** (Holt-Winters + SARIMAX) | Available, sufficient for 90-day horizon, no heavyweight dependency. |
| Data volume (POS up to 1.5M rows) | **PoC at ~10% scale** — identical architecture and business logic, reduced sampling rates | 16 cores / 128 GB free; full volume doubles wall time for no architectural benefit. Production design point documented. |

All deviations documented in `00_RECONNAISSANCE_REPORT.md` §7.

---

## 3. TECHNOLOGY STACK

| Layer | Technology |
|---|---|---|---|---|
| Synthetic generation | Python 3.11, numpy 2.4.3, pandas 3.0.6 |
| Raw storage | CSV + Excel (deliberately dirty, raw preserved untouched) |
| ETL | Python + pandas, modular per-stage scripts |
| Profiling / EDA | pandas, numpy, matplotlib |
| Warehouse (execution) | **DuckDB** (embedded OLAP SQL, PostgreSQL-compatible) |
| Warehouse (target DDL) | **PostgreSQL** scripts in `07_sql/` |
| Marts | SQL views (aggregated KPI layer) |
| Forecasting | statsmodels — Holt-Winters / SARIMAX |
| Anomaly detection | z-score + IQR + rolling baseline + business rules |
| Dashboard | Self-contained HTML + JS + SVG charts (no external deps) |
| Excel demo workbook | openpyxl + xlsxwriter (18 sheets) |
| Documentation | Markdown |

---

## 4. DATA ARCHITECTURE (layers)

```
01_raw_data       raw CSV per source, intentionally dirty. READ-ONLY. Never edited.
02_staging        typed + trimmed copy; dtype-enforced (fixes formula-as-string / text-numbers)
03_cleaned_data   standardized, mapped to master IDs, deduped, validated
04_master_data    dim_* tables with surrogate keys + alias→canonical mapping tables
05_etl            modular pipeline scripts + shared params module
06_data_warehouse fact_* tables + dim_* tables + mart views (executed on DuckDB)
07_sql            PostgreSQL DDL (production target) + warehouse DDL + mart views + reconciliation SQL
08_eda            profiling + EDA scripts and outputs
09_dashboard      semantic model spec, DAX library, HTML dashboards
10_forecasting    forecast scripts + outputs + methodology
11_anomaly_detection detection scripts + alerts + methodology
12_documentation  full doc set
```

**Lineage rule:** every cleaned row traces to a staging row traces to a raw row. Raw is never overwritten in place — it is the audit baseline.

**Mart rule:** `mart_kpi_daily`, `mart_fnb_monthly`, `mart_hotel_monthly`, `mart_finance_monthly`, `mart_budget_vs_actual`, `mart_dq_source_health` are the **only** read path for dashboards, forecast, anomaly, insights, and reconciliation.

---

## 5. SYNTHETIC DATA MODEL (business logic)

Deterministic (`SEED = 20260924`). All constants in `05_etl/params.py`.

### 5.1 Calendar & seasonality
- Window: **2025-01-01 → 2026-12-31** (731 days).
- Day-of-week effect: Fri/Sat premium (+), Sun dip, Mon–Thu baseline.
- Month effect: peak Jun–Aug + Dec–Jan (Indonesian holiday pattern), low Feb–Mar.
- Long-weekend boost: fixed simplified Indonesian holiday set (Idul Fitri, Christmas, New Year, Easter, Independence Day, Vesak) — documented as simplified, not a claim about real dates.
- 2026 carries a mild demand uplift vs 2025 (growth).

### 5.2 Hotels (7 properties, 200 rooms each)
- Base occupancy per property 62–84%; multiplied by DOW × month × holiday factors.
- ADR ladder per property Rp 850k–1.9M base, adjusted by season.
- Booking segments: Leisure, Corporate, OTA, Wholesale, Group, Wedding/Event.
- Channels: Direct Website, OTA, Corporate, GDS, Walk-in, WhatsApp.
- Room types: Standard, Deluxe, Executive, Suite, Family.
- Poisson booking arrivals → room nights; check-in 2025-01-01 onward, LOS 1–6 nights.
- Cancellation ~6–9%, no-show ~1.5%, both higher for OTA/Wholesale.
 cancellation_status ∈ {Confirmed, Cancelled, No-Show}; payment_status ∈ {Paid, Unpaid, Partial}.
- Rooms sold = bookings confirmed & not cancelled/no-show. **Room revenue = rooms sold × ADR.**

### 5.3 F&B (2 business units, 9 outlets, ~60 SKUs, 9 categories)
- Outlets: All-Day Dining (×7, one per hotel), Specialty Restaurant (×2 at flagship), Lobby Lounge (×2), Rooftop Bar (×1), and Mercure Food Hall + Mercure Dining Group units.
- Covers per outlet per day follow Poisson around an outlet profile, boosted by occupancy (hotel F&B is demand-linked to occupancy) and weekend/holiday.
- Menu ~60 SKUs across 9 categories (Coffee, Tea, Breakfast, Appetizer, Main Course, Rice/Noodles, Dessert, Beverage, Snack).
- Price ladder by category; lognormal check size; category mix weights per outlet type.
- Discounts ~3–5% (promo, staff, happy hour); void ~1.2%; refund ~0.8%.
- Net sales = gross − discount − void − refund value.
- **F&B COGS linkage:** each product has a recipe cost ratio; inventory consumption for F&B products is tied to quantities sold; waste 2–4% of consumption.

### 5.4 Inventory
- One row per **product × property × date** for the F&B product set (per prompt's stated grain).
- opening = prior closing; closing = opening + purchase − consumption − waste (+ transfers).
- consumption derived from POS quantities (business linkage: F&B sales → consumption).
- stock_value = closing × moving-average unit cost.
- Procurement replenishes when stock falls below a reorder point → purchase orders.

### 5.5 F&B products vs hotel supplies
`fact_inventory` covers the **F&B product set only**. Hotel room supplies (amenities, linen, toiletries) are out of scope for the inventory fact — documented in `05_DATA_DESIGN.md` to keep the grain (product × property × date) clean and avoid a second, structurally different inventory domain.

### 5.6 Procurement
- Purchase lines generated from inventory reorder events + supplier base (~14 suppliers).
- Unit price = product base cost × supplier variance × mild inflation drift over 24 months (a realistic cost-inflation story that shows up in food cost trend and anomaly detection).
- `total_amount = quantity × unit_price`.

### 5.7 Finance / ERP
- Expense transactions by property × department × account (~38 accounts, 7 departments).
- COGS accounts fed from F&B COGS (business linkage); other expenses modeled as ratios of revenue with property efficiency variance.
- `transaction_type ∈ {Debit, Credit}`.

### 5.8 Budget
- Monthly budget per property × department × account, set as a planned number with realistic optimism/pessimism per property (some properties beat budget, some miss — this is what makes Budget vs Actual meaningful).
- 7 properties × 7 departments × 38 accounts = ~1,850 accounts-monthly lines; × 24 months ≈ 2,016 active budget lines (a property-department-account cell is only budgeted where it applies).

---

## 6. DIRTY-DATA DESIGN (deliberately injected)

| # | Category | Concrete injection |
|---|---|---|---|---|
| D1 | Property aliases | 5+ variants per property: `Mercure Grand Jakarta`, `MERCURE GRAND JAKARTA`, `Mercure Grand JKT`, `MG Jakarta`, `Mercure-Jakarta`, `MG JKT` → canonical `H001 · Mercure Grand Jakarta` |
| D2 | Product aliases | `COFFEE LATTE` / `Coffee Latte` / `coffee latte` / `Latte Coffee` / `LATTE - COFFEE` → canonical `P001 · Coffee Latte` |
| D3 | Mixed date formats | `YYYY-MM-DD`, `DD/MM/YYYY`, `MM-DD-YYYY`, `DD-MMM-YYYY`, `YYYYMMDD` across and within files |
| D4 | Mixed decimals | `1.234,56` (ID locale), `1,234.56` (EN locale), `1234.56` bare |
| D5 | Whitespace | leading/trailing spaces on names and codes |
| D6 | Case inconsistency | upper/lower/title mixing on category, channel, segment, account |
| D7 | Blank rows / columns | stray blank rows mid-file; one stray blank column in PMS |
| D8 | Inconsistent headers | aliased headers (`prop` vs `property`, `qty` vs `quantity`, `amt` vs `amount`), sometimes title-case |
| D9 | NULLs | ~1–3% nulls on optional fields (segment, channel, discount, transfer_qty) |
| D10 | Duplicates | duplicate transaction_ids in POS/Finance (~1%), exact row dups in inventory |
| D11 | Invalid codes | malformed account codes (`4100X`), unknown property (`MG Solo`), unknown product codes |
| D12 | Negative quantities | small % negative `quantity` / `consumption_qty` (real-world correction artifacts) |
| D13 | Impossible dates | check-in after check-out; a few dates outside the window |
| D14 | Orphan records | POS rows referencing products not in the product master; finance rows referencing unknown properties |
| D15 | Invalid categories | a few `category` values outside the category master |

Every injection is a plausible real-world issue, not random noise. Each is detected, counted, and logged in the **DATA_CLEANSING_LOG** with actual computed counts — never typed by hand.

---

## 7. ETL PIPELINE DESIGN

```
01_extract.py     raw → staging      read raw, enforce dtypes, trim, preserve raw untouched
02_profile.py     staging            profile: nulls, dups, invalid, distributions → profile report
03_clean.py       staging → cleaned  fix whitespace, case, dates → ISO, decimals → float, drop blanks
04_standardize.py cleaned            canonical case + units + category whitelist
05_map_master.py  cleaned            alias → canonical ID via master mapping tables
06_transform.py   cleaned → warehouse grain  business calcs (rooms sold, net sales, COGS, closing stock)
07_validate.py    warehouse          DQ framework: completeness/uniqueness/validity/consistency/RI
08_load.py        warehouse          load facts+dims into DuckDB, create indexes, build marts
09_quality_report.py  warehouse     source health + DQ score per source → mart_dq_source_health
```

Each script is runnable standalone and idempotent. Shared constants live in `params.py`.

**Gate rule:** each script asserts its output contract before writing. A failure aborts the pipeline rather than propagating dirty state downstream.

---

## 8. WAREHOUSE DESIGN

Star schema, 11 dimensions + 6 facts (full DDL in `07_sql/`):

**Dimensions:** `dim_date`, `dim_property`, `dim_business_unit`, `dim_department`, `dim_product`, `dim_product_category`, `dim_customer_segment`, `dim_channel`, `dim_account`, `dim_supplier`, `dim_room_type`

**Facts and grain:**
| Fact | Grain |
|---|---|---|---|---|
| `fact_room_sales` | 1 row = 1 room booking |
| `fact_fnb_sales` | 1 row = 1 POS product line |
| `fact_inventory` | 1 row = product × property × date |
| `fact_purchase` | 1 row = 1 purchase line |
| `fact_expense` | 1 row = 1 expense transaction |
| `fact_budget` | 1 row = property × department × account × period |

**Marts (read path for all consumers):** `mart_kpi_daily`, `mart_fnb_monthly`, `mart_hotel_monthly`, `mart_finance_monthly`, `mart_budget_vs_actual`, `mart_dq_source_health`.

PostgreSQL DDL is the production target; DuckDB executes the identical design (PostgreSQL-compatible dialect). Differences are limited to index/constraint syntax and are isolated in the DDL files.

---

## 9. SEMANTIC MODEL & DAX (Power BI specification)

- Star schema imported as-is; **no flat table**.
- `dim_date` marked as date table with `Date` key; relationships single-direction (dimension → fact).
- Relationship inventory, cardinality, and filter direction in `09_dashboard/semantic_model/01_relationships.md`.
- DAX measure library in `09_dashboard/semantic_model/02_dax_measures.dax` — validated measure-by-measure against SQL marts.
- Browser dashboard implements the same measure names and logic so the mockup is traceable to the semantic model.

---

## 10. DASHBOARD DESIGN

Monitor surface (per claude-design skill): density + glanceability, no hero + feature cards.

| # | Dashboard | Primary question |
|---|---|---|---|---|
| 01 | Group Executive | How is the Group performing? |
| 02 | Property Performance | Which property drives/leaks profit? |
| 03 | Hotel Performance | Occupancy, ADR, RevPAR, channel, segment, cancellation |
| 04 | F&B Performance | Food cost, waste, discount, void, margin by outlet |
| 05 | Finance | Actual vs Budget vs LY, EBITDA |
| 06 | Data Quality & Integration | Source health, freshness, quality score |

**Design system:** deep navy `#0B1F3A`, champagne gold `#C9A227`, warm white `#F7F4EE`, charcoal `#2A2A2A`, soft gray `#8A8F98`. Inter/system sans for body; strong numeric hierarchy. Whitespace, restrained color, conditional formatting only where it carries meaning.

**Information hierarchy per dashboard:** QUESTION → KPI cards → TREND → COMPARISON → DIAGNOSIS → DETAIL table → ACTION / insight panel.

Filters: date range, year, month, business type, property, department, category, product, channel.

---

## 11. ADVANCED ANALYTICS

### 11.1 Forecasting (90-day horizon)
- Series: Group revenue, Occupancy, ADR, F&B net sales, F&B transactions, Average check.
- Training: full 24-month window. Forecast: 90 days beyond Dec 2026.
- Models: Holt-Winters (additive/multiplicative seasonality) selected per series by validation MAPE; SARIMAX as fallback/contrast.
- Validation: last 90 days of actuals held out; MAPE/MAE/RMSE reported per series.
- Output: `10_forecasting/forecast_90d.csv` + methodology doc + chart HTML.

### 11.2 Anomaly detection
- z-score (|z| > 3) and IQR (1.5×IQR) on daily revenue, food cost %, occupancy, transaction count, inventory variance.
- Rolling 28-day median baseline for trend-shifted series.
- Business rules: negative net sales, occupancy > 100% or < 20%, food cost % > 40%, discount ratio > 20%, void rate > 5%.
- **Every alert is computed from data.** Zero manually inserted alerts. Output: `11_anomaly_detection/anomalies.csv` + methodology.

### 11.3 AI insight layer
Computed from marts at generation time, each insight: **evidence** (computed figures) → **interpretation** → **investigation areas** → **suggested action**. No hardcoded conclusions. Output: `09_dashboard/insights.json`, rendered into the dashboards and the executive deck.

---

## 12. RECONCILIATION DESIGN

9 anchor KPIs reconciled **Python ↔ SQL warehouse ↔ Dashboard**, all three computed from the same marts:

Total Revenue, Room Revenue, F&B Revenue, COGS, Gross Profit, EBITDA, Occupancy %, ADR, RevPAR.

Report: `07_sql/05_reconciliation.sql` + `12_documentation/14_QA_REPORT.md` — table of KPI | Python | SQL | Dashboard | Difference | Status. Target difference = 0.

---

## 13. QUALITY GATES (executable)

| Phase | Gate script | Pass criteria |
|---|---|---|---|---|
| Data gen | `05_etl/gate_generate.py` | row counts in range, raw files exist, dirty patterns present |
| ETL | `05_etl/gate_etl.py` | 0 nulls on PKs, 0 dup PKs, 100% mapped IDs, 0 orphan facts |
| Warehouse | `07_sql/gate_warehouse.sql` | RI checks all pass, mart row counts > 0, KPI non-null |
| Analytics | gate in forecast/anomaly scripts | MAPE bounded, anomaly count > 0 and < 1% of rows |
| BI | `09_dashboard/gate_dashboard.py` | every dashboard KPI equals mart value (diff = 0) |
| Docs | manual review | doc set complete, synthetic declaration present |

A gate that fails aborts the build. No phase starts until the previous gate passes.

---

## 14. REPRODUCIBILITY

`python 05_etl/run_all.py` → regenerates the entire project from `SEED = 20260924`: raw → staging → cleaned → master → warehouse → marts → EDA → forecast → anomaly → insights → dashboards → Excel workbook → reconciliation. Identical numbers on re-run.

