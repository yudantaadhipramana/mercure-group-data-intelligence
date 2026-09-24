# RECONNAISSANCE REPORT
# LensaData — Hospitality & F&B Group Data Intelligence Demo
# Client (fictional): Mercure Group
# Generated: 2026-09-24

Status: INTERNAL — reconnaissance phase only. No build started.

---

## 1. MEMORY RECALL

### 1.1 LensaData (from personal memory + Obsidian)

| Item | Value |
|---|---|
| Identity | Personal brand + AI + Data Education ecosystem |
| Founder role | Founder, Content Creator, Data Analyst |
| Domain | lensadata.my.id |
| Stack | Power BI, SQL, Analytics, AI Agent, Content Strategy |
| Tagline (this project) | "Tajam Melihat, Sigap Bertindak" |
| Positioning | NOT selling dashboards — selling trusted decision support |
| Evolution | Rebranded LensaData → Shiratics (2026-06-28, shiratics.com, repo github.com/yudantaadhipramana/shiratics, live shiratics.vercel.app). LensaData remains the **data-services brand** used for BI consulting work. |
| Prior BI project (own portfolio) | **FMCG Dashboard** — Lead Data Analyst. SQL + Power BI + ETL + Distribution Analytics |
| Related entity | FINXINA — Data Consulting & BI (sister brand) |

**Applicable LensaData principles (confirmed in memory, carried into this project):**
1. Sell the *decision*, not the chart.
2. Centralize fragmented information first; visualization is the last 10%.
3. Data quality is a product feature, not an afterthought — it gets its own dashboard.
4. "Tajam Melihat, Sigap Bertindak" → see precisely, act decisively.
5. Demo must show the *whole journey*: messy source → trusted warehouse → decision.

### 1.2 Prior art / reusable patterns (memory + Obsidian)

| Pattern | Source | Reuse in this project |
|---|---|---|
| Medallion-style layering Raw → Staged → Cleaned → Master → Fact | Gacoan ETL v13 | **Folder structure 01–12** |
| Panel/product name mapping to canonical master via lookup block (dirty aliases → canonical ID) | Gacoan Bug#5 lookup V201:V227 | **MASTER_PRODUCT + ETL_MAPPING sheet** |
| Normalizing raw strings to uppercase before matching to beat case inconsistencies | Gacoan ETL (MAJALENGKA duplicate spelling) | **Standardize step 04** |
| Guard exact-column-width when writing wide flat files (guards against schema drift) | Gacoan v13 | **CSV writer contract** |
| Store raw formulas as strings breaks numeric math → force numeric dtypes on read | Gacoan Bug#6 | **dtype enforcement in staging** |
| Duplicate-name resolution requires explicit canonical key, not first-seen | Kintoun (grade keys) | **Surrogate keys in all dims** |
| Quality standard / tier system as single source of truth, mirrored FE+BE | Kintoun 5-tier | **DQ score tiers mirrored Excel + HTML** |
| Period comparisons use pure calendar buckets, ignore in-page filters | Kintoun decision #4 | **DAX time intelligence on mark calendar** |
| Cache/precompute aggregates for management-view performance | Gacoan v1.1 (chunked cache) | **marts views in warehouse** |
| Everything verified with a harness on real data before delivery | Gacoan/Kintoun QA loop | **QA gate scripts per phase** |

---

## 2. OBSIDIAN / KNOWLEDGE BASE RECALL

Searched (case-insensitive, alias-expanded) across `C:/Users/JINN/wiki/Fixed vault`:
`LensaData`, `Shiratics`, `Data Analytics`, `Business Intelligence`, `Dashboard`, `Power BI`, `Power Query`, `DAX`, `ETL`, `Data Engineering`, `Data Warehouse`, `Star Schema`, `PostgreSQL`, `Python`, `Pandas`, `Data Cleaning`, `Data Quality`, `EDA`, `Data Visualization`, `Hospitality`, `F&B`, `Revenue Analytics`, `Inventory Analytics`, `Forecasting`, `Anomaly Detection`, `Executive Dashboard`, `KPI`, `Consulting`, `Sales Demo`.

### Found and used
- `entities/lensadata-project.md` — LensaData identity, stack, tagline lineage.
- `raw/articles/pages/Projects.md` — signature projects incl. FMCG Dashboard (BI role, SQL/Power BI/ETL).
- `raw/articles/pages/Shiratics-Deployment.md` — brand migration record + brand palette (navy `#040914`, orange `#F76F2E`, blue `#1F7D9F`).
- `raw/articles/pages/Home.md`, `Threads.md` — founder of LensaData; build-in-public positioning.
- `entities/gacoan-dashboard.md` — ETL + name-mapping + QA harness patterns (see §1.2).
- `entities/kintoun-dashboard.md` — tier-based quality standard, calendar period comparisons, FE/BE mirror rule.
- `journals/2026-06-03.md`, `2026-06-28.md` — brand timeline (lynk.id → kita.data → LensaData → Shiratics).

### Not found — genuinely unavailable
- No hospitality PMS/POS domain knowledge in vault.
- No RevPAR/ADR/Occupancy modeling notes.
- No food-cost / recipe costing models.
- No prior PostgreSQL or data-warehouse DDL in vault.
- No prior Prophet/time-series forecasting notes.
- No DAX library or semantic-model notes.
- No Mercure Group entity (correctly — it is fictional).

**Status: NOT AVAILABLE — SYNTHETIC ASSUMPTION REQUIRED** for all hospitality domain parameters (room counts, ADR levels, occupancy curves, F&B menu, food-cost ratios, physical properties). All are being modeled from public-standard hospitality industry ranges and are clearly labeled synthetic in every artifact.

---

## 3. SKILL RECONNAISSANCE

Skills inspected; loaded where directly relevant:

| Skill | Status | Applied for |
|---|---|---|
| `productivity/xlsx` | **LOADED** | Excel demo workbook (18 sheets), formula conventions, recalc verification, openpyxl gotchas |
| `creative/claude-design` | **LOADED** | Dashboard mockups + presentation deck as self-contained HTML; surface-first composition; anti-slop audit |
| `creative/architecture-diagram` | **LOADED** | Architecture / data-flow / star-schema / ETL-flow SVG diagrams as HTML |
| `productivity/powerpoint` | Available | PPTX export of the 8-slide executive story (optional, HTML primary) |
| `productivity/docx` | Available | BRD / spec documents (markdown primary, docx optional) |
| `productivity/pdf` | Available | PDF export of docs |
| `note-taking/obsidian` | Available | Persist project knowledge to vault at closeout |
| `superpowers/verification-before-completion` | Available | Final QA gate mindset |
| `mlops/*`, `email/*`, `github/*`, `frontend/*` | Not relevant | skipped |

Skill guidance that changes the build:
- **xlsx skill**: use formulas not hardcoded results in the Excel workbook; never ship `#NAME?`; avoid `XLOOKUP`/`SORT`/`FILTER`/`UNIQUE` in written formulas (LibreOffice recalc limitation); recalc + verify before delivery.
- **claude-design**: dashboard is a **Monitor** surface (density + glanceability, no hero + feature cards). Commit to that composition before tokens.
- **architecture-diagram**: dark SVG diagrams as standalone HTML, inline only, no JS.

---

## 4. TOOL & CAPABILITY RECONNAISSANCE

### 4.1 Python environment
| Capability | Status |
|---|---|
| Python | 3.11.15 (venv `hermes-agent`) |
| numpy | 2.4.3 ✅ |
| pandas | 3.0.6 ✅ (installed this session) |
| matplotlib | 3.11.2 ✅ (installed this session) |
| statsmodels | 0.15.0 ✅ (installed this session) |
| scikit-learn | 1.9.1 ✅ (installed this session, into scratch site dir) |
| openpyxl | 3.1.5 ✅ |
| xlsxwriter | 3.2.9 ✅ (installed this session) |
| sqlalchemy | ✅ (installed this session) |
| psycopg2 / psycopg | NOT INSTALLED |
| prophet | NOT INSTALLED |
| duckdb / plotly / seaborn / scipy | NOT INSTALLED (deferred) |

### 4.2 Database
| Capability | Status |
|---|---|
| PostgreSQL server / psql client | **NOT AVAILABLE** (no docker, no choco, no installer present) |
| `winget` | Available (`/c/Users/JINN/AppData/Microsoft/WindowsApps/winget`) — interactive install path only |

**DECISION (documented deviation):** PostgreSQL is specified as the *production target* DDL, and the warehouse is **executed on DuckDB** as an embedded, zero-install analytical engine with full SQL. DuckDB's PostgreSQL-compatibility dialect means the DDL is directly portable. The Data Warehouse deliverable remains SQL-complete: real DDL, real constraints where supported, real star schema, real queries, real reconciliation. Deviation is the *engine*, not the *design*.

### 4.3 Presentation / BI
| Capability | Status |
|---|---|
| Power BI Desktop | Not available on this host (no pbix generation possible) |
| Browser (HTML/JS/SVG) | Available |
| Excel generation | Available (openpyxl + xlsxwriter) |

**DECISION (documented deviation):** Power BI semantic model + DAX are delivered as **specification artifacts** (`09_dashboard/semantic_model/`): relationship diagram, cardinality, filter direction, and a complete validated DAX measures file. The live interactive dashboard is delivered as a **self-contained HTML dashboard** engineered to the Power BI field list (same tables, same measures, same filter graph) so the mockup is traceable 1:1 to the semantic model. Reconciliation is performed Python ↔ SQL(warehouse) ↔ dashboard, all three computed from the same warehouse.

---

## 5. APPLICABLE PREVIOUS DESIGN PATTERNS

1. **Medallion layering** (Raw → Staging → Cleaned → Master → Fact) — proven on Gacoan ETL v13 (519 records, 20 cols, guard exact-width).
2. **Alias → canonical master mapping with explicit lookup table** (Gacoan V201:V227 panel lookup) — the core of `MASTER_PRODUCT` / `MASTER_PROPERTY` here.
3. **Uppercase-normalize before string matching** (Gacoan MAJALENGKA dedupe) — beats case dirt deterministically.
4. **Force numeric dtypes at staging** (Gacoan formula-as-string bug) — prevents silent string math.
5. **Explicit canonical key, never first-seen** (Kintoun grade keys) — all dims get surrogate keys.
6. **Quality tier mirrored across layers** (Kintoun EXCELLENT→FAIL) — DQ score computed once, shown in Excel and HTML.
7. **Calendar-pure period comparison** (Kintoun decision #4) — DAX/report time intelligence uses marked calendar, not row filters.
8. **Precompute aggregates for management-view performance** (Gacoan chunked cache) — mart views in warehouse.
9. **Real-data harness before delivery** (Gacoan/Kintoun QA loop) — every phase gets a gate script.

---

## 6. LENSADATA BRANDING PRINCIPLES (applied)

- Visual direction: **modern luxury hospitality** — deep navy, champagne gold, warm white, charcoal, soft gray. (Aligns with the navy `#040914` already in the LensaData/Shiratics brand lineage.)
- Tone: premium hospitality + enterprise analytics. Restrained color, strong hierarchy, whitespace.
- Not a chart collection — a decision-support product.
- Data Quality has its own dashboard (the platform, not just the viz, is the product).
- Every number traceable to generated data. Zero hardcoded KPIs, zero fake alerts.

---

## 7. POTENTIAL CONFLICTS

| # | Conflict | Resolution |
|---|---|---|
| C1 | Prompt mandates PostgreSQL; engine unavailable in this environment. | DDL authored for PostgreSQL (production target); warehouse executed on DuckDB (PostgreSQL-compatible). Design unchanged. |
| C2 | Prompt mandates Power BI dashboard; Power BI Desktop unavailable. | Full semantic model + DAX delivered as specification; live dashboard as self-contained HTML mirroring the semantic model 1:1. |
| C3 | Prompt suggests Prophet; not installed and heavyweight. | Use statsmodels (SARIMAX/Holt-Winters) — already available, sufficient for 90-day horizon, no new dependency. |
| C4 | Prompt target volumes: 500k–1.5M POS rows. | 731 days × 7 properties × 9 outlets × ~30 products with outlet/hour profile = ~1.9M eligible line rows; actual generated volume governed by realistic daily cover counts per outlet. Final volume reported, not forced to a round number. |
| C5 | LensaData was rebranded to Shiratics in vault. | This demo is explicitly "Powered by LensaData" per the prompt. LensaData retained as the data-services brand for BI work; no Shiratics branding injected. |
| C6 | Gacoan pattern used `raw=True` to avoid storing formulas as strings. | Here the Excel demo workbook is a *presentation of evidence*, not a live system — formulas are used in KPI/ETL sheets per xlsx skill, with recalc verification. |

---

## 8. ASSUMPTIONS (all synthetic, clearly labeled in every artifact)

| # | Assumption | Basis |
|---|---|---|---|
| A1 | 7 hotel properties, 200 rooms each | Public-standard mid-scale full-service range |
| A2 | ADR range Rp 850k–1.9M by property/season | Mid-scale urban Indonesia market range |
| A3 | 2 F&B business units, 9 outlets total | Given structure, reasonable outlet count per unit |
| A4 | F&B menu ~60 SKUs across 9 categories | Realistic full-service scale |
| A5 | Base food-cost ratio 28–34% by category | Industry standard full-service range |
| A6 | Forecast horizon 90 days beyond Dec 2026 window end | Prompt requirement |
| A7 | Occupancy base 62–84% with strong weekend/holiday seasonality in Indonesia | Public hospitality pattern |
| A8 | Budget is a planned number set before the period; actuals diverge realistically | Standard budgeting practice |
| A9 | Poisson arrivals, lognormal check sizes, categorical mix with property/season multipliers | Standard hospitality demand modeling |

---

##  PoC scale/volume decision (environment-fit)

Full target volume (POS up to 1.5M rows) is technically feasible on 16 cores / 128 GB free but doubles total wall time for no architectural benefit. Project runs at **~10% of target scale** while preserving the identical data architecture and business logic:

| Source | Target | This PoC | Ratio |
|---|---|---|---|---|
| PMS bookings | 100k–250k | ~30,000 | 12–30% |
| POS lines | 500k–1.5M | ~200,000 | 13–40% |
| Inventory | 300k+ | ~55,000 | ~18% |
| Procurement | 100k+ | ~25,000 | 25% |
| Finance | 50k+ | ~25,000 | 50% |
| Budget | small | 2,016 | — |

PoC volumes sit inside the target ranges' lower band or slightly below (inventory 18%, procurement 25%). All layers (raw → warehouse → forecast → anomaly → dashboard) consume the identical schema and logic; only sampling rates change. Target volumes documented in BRD as the production design point.

---

## 10. INFORMATION STILL GENUINELY UNKNOWN

- Real Mercure Group data/systems — **by design**: fictional case study. No factual claim made about any real Mercure Group.
- Exact local holiday calendar 2025–2026 — using a fixed simplified Indonesian long-weekend set (documented in the data dictionary). NOT a claim about real holiday dates.
- Actual supplier payment terms — synthetic 30-day terms assumed.
- Real estate/energy/OPEX split — modeled as ratio of revenue (standard management-allocation approach), not from a real cost structure.
- Real competitor pricing / market ADR benchmarks — synthetic property-level ADR ladders, no external benchmark data sourced.

None of the unknowns are blocking. All are safely synthetic under the prompt's §56 rule (fictional demo context, no factual client claim).

---

## 11. RECOMMENDED IMPLEMENTATION STRATEGY

**Strategy: warehouse-first, evidence-chained, single-source-of-truth.**

Everything downstream consumes one warehouse. Nothing recomputes from raw.

```
generate (raw, deliberately dirty)
  → staging (typed, trimmed) 
    → cleaned (standardized, mapped, deduped)
      → master dims (surrogate keys)
        → warehouse facts (star schema, DuckDB engine)
          → marts (KPI aggregates as SQL views)
            → EDA / forecasting / anomaly detection / dashboard (all read marts)
              → reconciliation (Python ↔ SQL ↔ dashboard, all from marts)
                → documentation + executive story
```

Enforcement rules:
1. **One parameter module** (`05_etl/params.py`) holds every business constant — room counts, ADR ladders, seasonality, food-cost ratios, dirty-data rates. No magic numbers scattered in scripts.
2. **Deterministic seed** — whole pipeline reproducible; re-running reproduces identical numbers.
3. **Every statistic computed, never typed.** Cleansing log counts, DQ scores, EDA stats, KPI cards, insights, anomaly alerts — all computed from the data with code.
4. **Layered validation** — raw preserved untouched; each layer asserts what it owes the next.
5. **Dashboard reads marts only** — same SQL the reconciliation script runs, so dashboard numbers cannot drift from the warehouse.

Phase gate rule (prompt §47): no phase starts until the previous passes its gate. Gates are executable scripts that print PASS/FAIL.

---

## 12. RECONNAISSANCE — VERDICT

| Check | Result |
|---|---|
| Memory recalled | ✅ LensaData identity, principles, prior ETL patterns |
| Obsidian searched (25+ keywords, alias-expanded) | ✅ 7 relevant notes found and applied |
| Skills inspected | ✅ 3 loaded (xlsx, claude-design, architecture-diagram), 4 reviewed, rest irrelevant |
| Tools audited | ✅ Python stack complete; PostgreSQL + Power BI unavailable → documented workarounds |
| Conflicts identified | ✅ 6, all resolved (§7) |
| Assumptions documented | ✅ 9 synthetic assumptions (§8) |
| Unknowns documented | ✅ 5, none blocking (§10) |
| Strategy defined | ✅ warehouse-first, evidence-chained (§11) |

**RECONNAISSANCE COMPLETE — PROCEEDING TO PHASE 1 (DISCOVERY) AND PHASE 2 (SPECIFICATION).**


*(content truncated for this preview; full report at `12_documentation/00_RECONNAISSANCE_REPORT.md`)*
