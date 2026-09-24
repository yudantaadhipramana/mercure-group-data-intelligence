# SOLUTION ARCHITECTURE
# Hospitality & F&B Group Data Intelligence Demo — Powered by LensaData

> Synthetic demonstration. Mercure Group is a fictional business context. No factual claim about any real Mercure Group.

---

## 1. THE PROBLEM — BEFORE

```
  PMS          POS          ERP/Finance    Inventory     Procurement    Budget
 (bookings)   (F&B sales)   (ledger)       (stock)       (purchases)   (Excel)
     │            │              │              │              │            │
     ▼            ▼              ▼              ▼              ▼            ▼
  ┌────────────────────────────────────────────────────────────────────────┐
  │                     FRAGMENTED DATA                                    │
  │  5+ property aliases · different product codes · different accounts    │
  │  mixed date formats · mixed decimal separators · duplicates · nulls    │
  └────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                     MANUAL EXCEL CONSOLIDATION
                                  │
                                  ▼
                       LATE, UNTRUSTED REPORTING
```

## 2. THE SOLUTION — AFTER

```
  PMS          POS          ERP/Finance    Inventory     Procurement    Budget
     │            │              │              │              │            │
     └────────────┴──────────────┴──────────────┴──────────────┴────────────┘
                                      │  Data Ingestion (preserve raw)
                                      ▼
                          ┌───────────────────────┐
                          │   01 RAW LAYER        │  dirty, untouched
                          └───────────────────────┘
                                      │  profile → typed → trimmed
                                      ▼
                          ┌───────────────────────┐
                          │   02 STAGING          │
                          └───────────────────────┘
                                      │  clean · standardize · map · dedupe
                                      ▼
                          ┌───────────────────────┐
                          │ 03 CLEANED + 04 MASTER│  canonical IDs, surrogate keys
                          └───────────────────────┘
                                      │  conform to star schema
                                      ▼
                          ┌───────────────────────┐
                          │  06 DATA WAREHOUSE    │  star schema
                          └───────────────────────┘
                                      │  aggregate KPI layer
                                      ▼
                          ┌───────────────────────┐
                          │      MART VIEWS       │  single source of truth
                          └───────────────────────┘
                                      │
                 ┌────────────────────┼────────────────────────┐
                 ▼                    ▼                        ▼
        ┌─────────────────┐  ┌─────────────────┐    ┌─────────────────────┐
        │  SEMANTIC MODEL │  │  ADVANCED       │    │  DATA QUALITY       │
        │  + DAX (spec)   │  │  ANALYTICS      │    │  MONITORING         │
        │  + HTML DASH    │  │  forecast 90d   │    │  completeness,      │
        │                 │  │  anomaly detect │    │  duplicates, RI     │
        └─────────────────┘  └─────────────────┘    └─────────────────────┘
                                      │
                                      ▼
                          ┌───────────────────────┐
                          │  MANAGEMENT INSIGHT   │
                          │  AI insight layer     │
                          └───────────────────────┘
                                      │
                                      ▼
                                 DECISION
                    "Tajam Melihat, Sigap Bertindak"
```

---

## 3. COMPONENT VIEW

| Component | Technology | Location |
|---|---|---|---|---|
| Synthetic sources (6) | Python + numpy generative model | `05_etl/generate_*.py` → `01_raw_data/` |
| Raw layer | CSV (preserved) | `01_raw_data/` |
| Staging | parquet (typed) | `02_staging/` |
| Cleaned + mapping | parquet | `03_cleaned_data/` |
| Master data | parquet + Excel sheets | `04_master_data/` |
| ETL pipeline | 9 modular Python scripts | `05_etl/` |
| Warehouse | DuckDB (execution), PostgreSQL (target DDL) | `06_data_warehouse/mercure.duckdb` |
| Marts | SQL views | `07_sql/03_marts.sql` |
| EDA | pandas + matplotlib | `08_eda/` |
| Semantic model + DAX | specification + measure library | `09_dashboard/semantic_model/` |
| Dashboards | self-contained HTML/JS/SVG | `09_dashboard/*.html` |
| Forecasting | statsmodels | `10_forecasting/` |
| Anomaly detection | statistical + business rules | `11_anomaly_detection/` |
| Documentation | markdown | `12_documentation/` |

---

## 4. DATA FLOW

```
RAW (dirty) ──extract──▶ STAGING (typed) ──clean/standardize/map──▶ CLEANED
CLEANED ──conform──▶ FACTS + DIMS (warehouse) ──aggregate──▶ MARTS
MARTS ──read──▶ { DASHBOARDS, FORECAST, ANOMALY, INSIGHTS, RECONCILIATION }
```

**Single-source-of-truth rule:** dashboards, forecasts, anomaly detection, insights, and the reconciliation report **all read marts**. Nothing recomputes from raw. This is what guarantees the dashboard can never drift from the warehouse.

---

## 5. STAR SCHEMA

```
                              dim_date
                                  │
        dim_property ─────────────┼─────────────── dim_product
            │                     │                    │
      dim_business_unit     dim_room_type        dim_product_category
            │                     │                    │
        dim_department      dim_channel       dim_supplier
            │                     │                    │
      dim_account          dim_customer_segment │
            │                     │              │
            └────────┬────────────┴──────────────┘
                     │
                     ▼
   ┌─────────────────────────────────────────────┐
   │  fact_room_sales   fact_fnb_sales           │
   │  fact_inventory    fact_purchase            │
   │  fact_expense      fact_budget              │
   └─────────────────────────────────────────────┘
```

Grain documented in `05_DATA_DESIGN.md` §6.

---

## 6. SECURITY & GOVERNANCE NOTES (demo scope)

- No credentials in source. The warehouse is a local embedded file with no network exposure.
- Synthetic data only — no PII, no real guest records, no real financial data.
- All figures fictional; README and every dashboard carry the synthetic declaration.
- In a production build: secrets in a vault, RLS by property in the semantic model, audit trail on the warehouse, retention policy per source.

---

## 7. DIAGRAM DELIVERABLES

| Diagram | File | Skill used |
|---|---|---|
| Solution architecture (before/after) | `09_dashboard/architecture.html` | architecture-diagram |
| Data flow (raw → mart → BI) | `09_dashboard/data_flow.html` | architecture-diagram |
| Star schema | `09_dashboard/star_schema.html` | architecture-diagram |
| ETL flow | `09_dashboard/etl_flow.html` | architecture-diagram |
| Dashboard navigation | `09_dashboard/nav.html` | claude-design |

All diagrams self-contained HTML + inline SVG, no external dependencies.
