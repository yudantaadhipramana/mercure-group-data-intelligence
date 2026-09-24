# IMPLEMENTATION PLAN
# Hospitality & F&B Group Data Intelligence Demo — Powered by LensaData

17 phases, each with an **executable gate**. No phase starts before the previous gate passes.

---

## PHASE 0 — RECONNAISSANCE ✅
Memory → Obsidian → skills → tools → conflicts → assumptions → strategy.
Gate: `12_documentation/00_RECONNAISSANCE_REPORT.md` written. **PASSED.**

## PHASE 1 — DISCOVERY & SPECIFICATION ✅
Business context, personas, problems, KPI framework, functional + non-functional requirements.
Gate: `01_BRD.md` complete. **PASSED.**

## PHASE 2 — SPECIFICATION ✅
Technical spec: stack, layers, dirty-data design, ETL design, warehouse design, analytics design, gates.
Gate: `02_TECHNICAL_SPECIFICATION.md` complete. **PASSED.**

## PHASE 3 — SOLUTION ARCHITECTURE ✅
Before/after architecture, component view, data flow, star schema, diagram list.
Gate: `03_SOLUTION_ARCHITECTURE.md` complete. **PASSED.**

## PHASE 4 — DATA DESIGN
Source schemas, master data, dimensions, facts, grain, mapping tables, KPI formulas.
Deliverable: `12_documentation/05_DATA_DESIGN.md`
Gate: every table + column + grain + relationship named. **IN PROGRESS.**

## PHASE 5 — SYNTHETIC DATA GENERATION
`05_etl/params.py` + `05_etl/generate_raw.py` → 6 dirty sources in `01_raw_data/`.
Gate: `gate_generate.py` — row counts, files exist, dirty patterns present.

## PHASE 6 — ETL
9 modular scripts. Cleansing log counts computed from actual data.
Gate: `gate_etl.py` — 0 null PKs, 0 dup PKs, 100% mapped, 0 orphans.

## PHASE 7 — EDA
`08_eda/` — structure, quality, statistics, distributions, time series, segmentation, outliers.
Gate: EDA report complete + business interpretation for every chart.

## PHASE 8 — DATA WAREHOUSE
DuckDB database, DDL, facts, dims, indexes, marts. PostgreSQL DDL alongside.
Gate: `gate_warehouse.sql` — RI 100%, mart counts, KPIs non-null.

## PHASE 9 — SEMANTIC MODEL + DAX
Relationships, cardinality, filter direction, measure library, hierarchies.
Gate: every DAX measure reconciled to its SQL mart counterpart.

## PHASE 10 — DASHBOARDS
6 HTML dashboards + architecture/data-flow/star-schema/ETL-flow/nav diagrams.
Gate: `gate_dashboard.py` — every dashboard KPI equals mart value.

## PHASE 11 — FORECASTING
6 series × 90-day horizon. Holt-Winters + SARIMAX, validated by holdout MAPE.
Gate: forecasts produced, error metrics bounded, methodology documented.

## PHASE 12 — ANOMALY DETECTION
z-score + IQR + rolling baseline + business rules on marts.
Gate: alerts all sourced from data, count bounded, methodology documented.

## PHASE 13 — AI INSIGHT LAYER
Evidence → interpretation → investigation areas → action, computed from marts.
Gate: every insight references computed figures, zero hardcoded conclusions.

## PHASE 14 — REVIEW
Data Architect / BI Consultant / Executive User reviews (3 hats).
Gate: every major issue logged with a fix or an accepted rationale.

## PHASE 15 — QA
Data / ETL / SQL / DAX / Dashboard / UX / Business QA + reconciliation.
Gate: reconciliation difference = 0 on all 9 anchor KPIs; QA report clean.

## PHASE 16 — REFINEMENT
Fix everything found in 14/15. Polish, optimize, tighten copy.
Gate: re-run gates 5→15 all PASS.

## PHASE 17 — FINAL DELIVERY
README, demo guide, executive narrative, 8-slide story, final delivery report.
Gate: checklist RAW→CLEAN→ETL→EDA→MASTER→DW→SEMANTIC→DAX→DASH→FORECAST→ANOMALY→INSIGHT→RECON→QA→DOCS→STORY all ✓.
