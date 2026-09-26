# IMPLEMENTATION_PLAN.md

Rebuild phases for the Mercure Group Data Intelligence Demo.

---

## Phase 0 — Reconnaissance ✅
- Memory, skills, and existing repo inspected.
- Existing ETL scripts, params, and dashboard structure understood.

## Phase 1 — Backup & Clean Slate ✅
- Backup branch: `backup-before-rebuild-2026-09-26`
- Rebuild branch: `rebuild-2026-09-26`
- Removed generated artifacts; kept source code and docs.

## Phase 2 — Documentation
- Write SPEC.md, IMPLEMENTATION_PLAN.md, ARCHITECTURE.md.
- Update README.md.

## Phase 3 — Foundation Pipeline
- Run synthetic data generation.
- Run extract → profile → master → clean → validate → load.
- Verify warehouse builds and marts query.

## Phase 4 — Quality, EDA, Forecasting, Anomaly, Insights
- Build data quality report.
- Generate EDA outputs.
- Build 90-day forecast.
- Run anomaly detection.
- Generate business insights.

## Phase 5 — Reconciliation
- Reconcile raw ↔ cleaned ↔ warehouse ↔ dashboard JSON.

## Phase 6 — Tests
- Unit tests for transformations.
- Integration tests for pipeline stages.
- Data quality tests.
- Reconciliation tests.

## Phase 7 — Dashboard
- Rebuild Next.js app with multi-page navigation.
- Implement 9 pages per prompt.
- Generate dashboard JSON from warehouse marts.
- Build static export.

## Phase 8 — Google Sheets + Apps Script
- Attempt OAuth setup (expected blocker).
- Document fallback architecture.

## Phase 9 — Vercel Deployment
- Attempt login/deployment (expected blocker).
- Verify local build and static export.

## Phase 10 — Final Report
- FINAL_DELIVERY_REPORT.md with actual results and blockers.
