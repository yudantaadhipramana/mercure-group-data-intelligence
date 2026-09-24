# BUSINESS REQUIREMENTS DOCUMENT (BRD)
# Hospitality & F&B Group Data Intelligence Demo — Powered by LensaData
**Fictional client:** Mercure Group · **Status:** Approved for build · **Version:** 1.0

> **Synthetic-data declaration.** This project is a synthetic demonstration created by LensaData. It does not represent actual operational data or systems of Mercure Group. All properties, transactions, and figures are fictional.

---

## 1. BUSINESS PROBLEM

Mercure Group operates **7 hotel properties** and **2 F&B business units (9 outlets)**. Operational data lives in **six disconnected systems** with different formats, naming conventions, and business definitions.

Management cannot answer basic questions reliably:

| # | Question management asks | Why it currently can't be answered |
|---|---|---|
| Q1 | How did the Group perform last month vs budget? | PMS, POS, Finance are separate; no group-level consolidation. Manual Excel takes days. |
| Q2 | Which property drives profit and which leaks it? | Different property naming in every system (5+ aliases per property); no cross-property comparison possible. |
| Q3 | Is food cost under control? | Inventory consumption and POS sales are in different systems with different product codes. Food cost % is not computable. |
| Q4 | Are we on budget by department and account? | Budget lives in a separate manual Excel; ERP uses different account codes. |
| Q5 | What should we expect next quarter? | No forecasting. Reporting is purely historical. |
| Q6 | Is the data itself trustworthy? | No data-quality monitoring. Duplicates, nulls, and mapping gaps are discovered only when a number "looks wrong". |
| Q7 | Where should we act first? | No single management view; insights buried in files. |

**Cost of the status quo (business framing of the "before" state):**
- Consolidation is manual, late, and error-prone → decisions made on stale data.
- Property aliases make cross-property benchmarking impossible.
- Food cost is invisible until the monthly close.
- No early warning on revenue/cost anomalies.
- No forecasting → staffing and purchasing based on guesswork.

---

## 2. PROJECT OBJECTIVES

1. **Integrate** all 6 source systems into one centralized data warehouse with a single business definition per metric.
2. **Standardize** properties, products, accounts, categories, and channels into stable master data with surrogate keys.
3. **Prove data quality** with an automated framework (completeness, uniqueness, validity, consistency, referential integrity) that is itself visible on a dashboard.
4. **Deliver management intelligence**: 6 dashboards covering Group, Property, Hotel, F&B, Finance, and Data Quality.
5. **Add advanced analytics**: 90-day forecasting and statistical anomaly detection, both derived from the data.
6. **Close the loop**: every insight points to an investigation area and a decision — See → Understand → Identify → Investigate → Act.

---

## 3. STAKEHOLDERS & PERSONAS

| Persona | Role | Primary question | Primary dashboard |
|---|---|---|---|
| **Owner / CEO** | Group owner | "Is the group healthy and growing?" | 01 Group Executive |
| **COO** | Operations | "Which property is underperforming, and why?" | 02 Property Performance |
| **GM (per property)** | Property head | "How is my property performing vs peer properties?" | 02 Property Performance |
| **Director of Rooms / Revenue Manager** | Hotel ops | "Occupancy, ADR, RevPAR, channel and segment mix?" | 03 Hotel Performance |
| **F&B Director** | F&B | "Food cost, waste, discount, void, margin by outlet?" | 04 F&B Performance |
| **CFO / Group Finance** | Finance | "Revenue, COGS, OPEX, EBITDA vs budget vs LY?" | 05 Finance |
| **Head of IT / Data** | Data platform | "Are all sources synced, complete, and clean?" | 06 Data Quality & Integration |
| **Business Analyst** | Analytics | "Where is the leakage? Show me the evidence." | All, with drill-down |

---

## 3a. PERSONA DETAIL — JOURNEY FRAMING

**CEO — "30 seconds" test:** open Dashboard 01 → see Group revenue, EBITDA margin, budget achievement, YoY. If a number is red, one click drills to the property and department responsible. **This is the acceptance bar for the executive view.**

**F&B Director — leakage test:** open Dashboard 04 → see Food Cost % by outlet. If one outlet's food cost is climbing, drill to that outlet's category and see whether it is purchase price (procurement), product mix, waste, or discount. **The dashboard must point at a cause, not just a symptom.**

**Head of Data — trust test:** open Dashboard 06 → every source shows last sync, record count, quality score, status. A failing source is visible before anyone asks. **Data quality is a first-class citizen, not a footnote.**

---

## 4. SCOPE

### In scope
- 6 synthetic source systems (PMS, POS, Finance/ERP, Inventory, Procurement, Budget), Jan 2025 – Dec 2026
- Deliberately messy raw data (aliases, mixed date formats, mixed decimal separators, whitespace, blanks, duplicates, nulls, invalid codes, orphan records)
- Full ETL pipeline: extract → profile → clean → standardize → map to master → transform → validate → load
- Master data management with surrogate keys
- Star-schema data warehouse (PostgreSQL DDL; executed on DuckDB)
- Semantic model + DAX measure library (Power BI specification)
- 6 interactive dashboards (self-contained HTML, engineered to the semantic model)
- 90-day forecasting (statsmodels), statistical + business-rule anomaly detection
- AI insight layer derived from the warehouse (no hardcoded conclusions)
- Full documentation set + executive demo narrative

### Out of scope
- Real Mercure Group data (fictional by design)
- Real-time / streaming ingestion (batch demo)
- Production deployment, security hardening, row-level security
- Customer-facing or guest-facing analytics
- HR / payroll systems
- Actual Power BI Desktop build (not available on this host)

---

## 5. KPI FRAMEWORK (requirements view)

### 5.1 Group
| KPI | Formula | Target / use |
|---|---|---|---|---|
| Total Revenue | Room Revenue + F&B Net Revenue + Other Income | Growth vs LY, vs budget |
| Revenue Growth YoY % | (Rev − Rev LY) / Rev LY | > 0 |
| EBITDA | Revenue − COGS − OPEX | Absolute + trend |
| EBITDA Margin % | EBITDA / Revenue | ≥ 28% healthy |
| Occupancy % | Occupied room nights / Available room nights | Property benchmark |
| ADR | Room Revenue / Rooms Sold | Pricing health |
| RevPAR | Room Revenue / Available room nights | Revenue efficiency |
| F&B Revenue | Net F&B sales | Mix |
| Food Cost % | F&B COGS / F&B Net Revenue | ≤ 32% healthy |
| Budget Achievement % | Actual / Budget | ≥ 100% |

### 5.2 Hotel
Room Revenue, Occupancy %, ADR, RevPAR, Cancellation %, No-show %, Avg LOS, Revenue by Channel, Revenue by Segment.

### 5.3 F&B
Gross Sales, Net Sales, Transactions, Average Check, COGS, Food Cost %, Gross Profit, Gross Margin %, Waste Value, Discount Value, Void, Refund.

### 5.4 Finance
Revenue, COGS, Gross Profit, OPEX, EBITDA, Net Profit; Actual vs Budget vs LY; Variance, Variance %.

### 5.5 Data Quality (the platform KPI)
Source Health: Connected Sources, Data Freshness, Completeness %, Duplicate Rate %, Mapping Completion %, Failed Records, Last Sync, Quality Score, Status.

---

## 6. FUNCTIONAL REQUIREMENTS

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | System shall ingest 6 heterogeneous sources without altering the raw files | Must |
| FR-02 | System shall profile each source and record missing/duplicate/invalid counts | Must |
| FR-03 | System shall standardize 5+ property aliases to 1 canonical property ID | Must |
| FR-04 | System shall standardize product aliases to 1 canonical product ID | Must |
| FR-05 | System shall parse all mixed date formats to ISO `YYYY-MM-DD` | Must |
| FR-05a | System shall parse mixed decimal/thousand separators (`1.234,56` / `1,234.56` / `1234.56`) | Must |
| FR-06 | System shall detect and remove duplicate transactions (same source+ID) | Must |
| FR-07 | System shall enforce referential integrity: every fact key exists in its dimension | Must |
| FR-08 | System shall compute and persist a data-quality score per source | Must |
| FR-09 | System shall expose KPIs through a semantic model with a DAX measure library | Must |
| FR-10 | System shall forecast 90 days for Revenue/Occupancy/ADR and F&B Sales/Transactions/Avg Check | Must |
| FR-11 | System shall flag anomalies via statistical + business rules, sourced from data | Must |
| FR-12 | System shall produce insights computed from warehouse marts, never hardcoded | Must |
| FR-13 | Dashboards shall filter by date, business type, property, department, category, product, channel | Must |
| FR-14 | Reconciliation report shall show Python ↔ SQL ↔ Dashboard variance for 9 anchor KPIs | Must |
| FR-15 | Pipeline shall be fully reproducible from a fixed seed | Must |

---

## 7. NON-FUNCTIONAL REQUIREMENTS

| ID | Requirement |
|---|---|
| NFR-01 | **Reproducibility** — fixed seed; re-running the pipeline reproduces every number |
| NFR-02 | **Traceability** — every dashboard number traceable to a mart view → fact → raw row |
| NFR-03 | **Modularity** — ETL as separate scripts per stage, shared parameter module |
| NFR-04 | **Performance** — dashboard loads from precomputed mart views |
| NFR-05 | **Usability** — executive-readable in ≤ 30 seconds (30-second test) |
| NFR-06 | **Aesthetic** — modern luxury hospitality: deep navy, champagne gold, warm white, charcoal, soft gray |
| NFR-07 | **Documentation** — full doc set; README states synthetic nature |
| NFR-08 | **Data volume** — production design point: PMS 100k–250k, POS 500k–1.5M, Inventory 300k+, Procurement 100k+, Finance 50k+. PoC runs at ~10% scale, same architecture |

---

## 8. SUCCESS CRITERIA (acceptance)

1. Raw files visibly messy; clean warehouse demonstrably trustworthy (DQ score per source visible).
2. Every KPI in every dashboard equals the warehouse number (reconciliation difference = 0).
3. Anomaly alerts originate from detection logic on real rows, not from hardcoded text.
4. Insights reference actual computed figures and name an investigation area.
5. An executive can answer "how is the group doing?" in ≤ 30 seconds from Dashboard 01.
6. Pipeline reproducible — second run byte-comparable (modulo timestamps) to the first.
7. Full documentation set exists and the README declares the synthetic nature.

---

## 9. THE BEFORE / AFTER STORY (demo spine)

**BEFORE** — PMS, POS, ERP, Inventory, Excel, CSV, Budget, manual files → fragmented → messy → manual consolidation → delayed reporting.

**AFTER** — Multiple sources → Data Ingestion → Raw Layer → Staging → ETL/Cleansing → Master Data → Data Warehouse → Semantic Model → BI → Management Insight → Decision.

The before/after transformation is a primary storytelling component and must be visible in the deliverables (architecture diagram, ETL flow diagram, Excel workbook, executive deck).

