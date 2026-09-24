# KPI DICTIONARY
# Hospitality & F&B Group Data Intelligence Demo — Powered by LensaData

Synthetic demonstration. All KPIs computed from warehouse marts — never hardcoded.

---

## 1. KPI FORMULAS

| KPI | Formula | Unit | Healthy band |
|---|---|---|---|---|
| **Total Revenue** | Room Revenue + F&B Net Revenue + Other Income | Rp | grows YoY |
| **Room Revenue** | Σ fact_room_sales.room_revenue (rooms_sold = 1) | Rp | |
| **F&B Net Revenue** | Σ fact_fnb_sales.net_sales (is_void=0, is_refund=0) | Rp | |
| **Occupancy %** | Occupied Room Nights ÷ Available Room Nights × 100 | % | 65–85% |
| **ADR** | Room Revenue ÷ Rooms Sold | Rp | property-dependent |
| **RevPAR** | Room Revenue ÷ Available Room Nights | Rp | |
| **F&B COGS** | Σ fact_fnb_sales.cogs_amount | Rp | |
| **Food Cost %** | F&B COGS ÷ F&B Net Revenue × 100 | % | ≤ 32% |
| **Gross Profit** | Net Revenue − COGS | Rp | |
| **Gross Margin %** | Gross Profit ÷ Net Revenue × 100 | % | ≥ 65% |
| **OPEX** | Σ fact_expense.amount where account_type = 'OPEX' | Rp | |
| **EBITDA** | Total Revenue − COGS − OPEX | Rp | |
| **EBITDA Margin %** | EBITDA ÷ Total Revenue × 100 | % | ≥ 28% |
| **Net Profit** | EBITDA × 0.72 (synthetic simplified D&A/interest/tax) | Rp | |
| **Average Check** | F&B Net Revenue ÷ Transactions | Rp | |
| **Transactions** | distinct transaction_id in fact_fnb_sales | count | |
| **Cancellation %** | cancelled bookings ÷ total bookings × 100 | % | ≤ 8% |
| **No-show %** | no-show bookings ÷ total bookings × 100 | % | ≤ 2% |
| **Avg LOS** | Σ los ÷ confirmed bookings | nights | 2–4 |
| **Waste Value** | Σ waste_qty × unit_cost | Rp | ≤ 3% of consumption |
| **Discount %** | Σ discount ÷ Σ gross_sales × 100 | % | ≤ 6% |
| **Void %** | void lines ÷ total lines × 100 | % | ≤ 2% |
| **Budget Achievement %** | Actual ÷ Budget × 100 | % | ≥ 100% |
| **Variance** | Actual − Budget | Rp | ≥ 0 |
| **Variance %** | (Actual − Budget) ÷ Budget × 100 | % | ≥ 0 |
| **Revenue YoY %** | (Rev − Rev LY) ÷ Rev LY × 100 | % | > 0 |
| **Revenue MoM %** | (Rev − Rev LM) ÷ Rev LM × 100 | % | context |

---

## 2. DATA QUALITY KPIs (the platform metrics)

| KPI | Formula |
|---|---|---|---|---|
| Completeness % | non-null mandatory fields ÷ total records × 100 |
| Uniqueness % | distinct PK ÷ total rows × 100 |
| Validity % | records passing format/domain checks ÷ total × 100 |
| Consistency % | records passing cross-source checks ÷ total × 100 |
| Integrity % | fact rows with valid FK ÷ total fact rows × 100 |
| Duplicate Rate % | duplicate rows ÷ total rows × 100 |
| Mapping Completion % | mapped records ÷ total records × 100 |
| Data Freshness | days since latest record |
| **Quality Score** | weighted mean of the six % dimensions |
| **DQ Tier** | A ≥ 98 · B 95–98 · C 90–95 · D < 90 |

---

## 3. KPI → DASHBOARD MAP

| KPI | D1 Group | D2 Property | D3 Hotel | D4 F&B | D5 Finance | D6 DQ |
|---|---|---|---|---|---|---|
| Total Revenue | ● | ● | | | ● | |
| EBITDA / Margin | ● | ● | | | ● | |
| Occupancy % | ● | ● | ● | | | |
| ADR | ● | ● | ● | | | |
| RevPAR | ● | ● | ● | | | |
| Room Revenue | ● | ● | ● | | ● | |
| F&B Net Revenue | ● | ● | | ● | ● | |
| Food Cost % | ● | ● | | ● | ● | |
| Average Check | | | | ● | | |
| Transactions | | | | ● | | |
| Waste / Discount / Void | | | | ● | | |
| Budget vs Actual | ● | ● | | | ● | |
| Cancellation / No-show / LOS | | | ● | | | |
| Channel / Segment mix | | | ● | | | |
| Quality Score / Freshness | | | | | | ● |
