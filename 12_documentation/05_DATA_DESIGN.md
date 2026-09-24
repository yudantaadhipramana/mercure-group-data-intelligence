# DATA DESIGN
# Hospitality & F&B Group Data Intelligence Demo — Powered by LensaData

Synthetic demonstration. Mercure Group is fictional. All values synthetic.

---

## 1. SOURCE SCHEMAS (as delivered from the fictional source systems)

### S01 — HOTEL PMS (`01_raw_data/pms/pms_bookings_raw.csv`)
| Column | Type (as found) | Notes |
|---|---|---|---|---|
| booking_id | string | PK in source; duplicates injected |
| property | string | 5+ alias variants per property |
| booking_date | string | mixed date formats |
| check_in | string | mixed date formats; some after check_out |
| check_out | string | mixed date formats |
| room_type | string | case inconsistent |
| guest_segment | string | nulls injected |
| booking_channel | string | case inconsistent; nulls injected |
| room_rate | string | mixed decimal separators (text!) |
| room_revenue | string | mixed decimal separators (text!) |
| cancellation_status | string | Confirmed/Cancelled/No-Show |
| payment_status | string | Paid/Unpaid/Partial |
| *(stray blank column `prop_code`)* | empty | injected blank column |

### S02 — F&B POS (`01_raw_data/pos/pos_transactions_raw.csv`)
| Column | Notes |
|---|---|---|
| transaction_id | duplicates injected |
| transaction_date | mixed formats |
| outlet | case inconsistent |
| product_code | aliases + unknown codes (orphans) |
| product_name | 4–5 alias variants per product |
| category | case inconsistent + invalid values |
| quantity | negatives injected |
| gross_sales | mixed decimal separators |
| discount | mixed decimals, nulls |
| net_sales | mixed decimals |
| payment_method | case inconsistent |
| void_flag | Y/N, case inconsistent |
| refund_flag | Y/N, case inconsistent |

### S03 — FINANCE / ERP (`01_raw_data/finance/erp_transactions_raw.csv`)
transaction_id (dups), transaction_date (mixed), property (aliases + 1 unknown), account_code (malformed `4100X`), account_name (case), department (case), amount (mixed decimals), transaction_type (Debit/Credit).

### S04 — INVENTORY (`01_raw_data/inventory/inventory_daily_raw.csv`)
inventory_date (mixed), property (aliases), product_code (aliases), product_name (aliases), opening_stock, purchase_qty, transfer_qty (nulls), consumption_qty (negatives), waste_qty, closing_stock, stock_value (mixed decimals). Exact duplicate rows injected.

### S05 — PROCUREMENT (`01_raw_data/procurement/procurement_raw.csv`)
purchase_id, purchase_date (mixed), supplier (case), property (aliases), product_code, product_name, quantity, unit_price, total_amount (mixed decimals).

### S06 — BUDGET (`01_raw_data/budget/budget_raw.csv`)
period (e.g. `2025-01`, `Jan-2025` mixed), property (aliases), department, account, budget_amount (mixed decimals).

---

## 2. MASTER DATA (canonical, surrogate-keyed)

### dim_property
| property_id | property_name | business_type | city | region | rooms | class |
|---|---|---|---|---|---|---|---|---|
| H001 | Mercure Grand Jakarta | Hotel | Jakarta | Java | 200 | Upper Midscale |
| H002 | Mercure Grand Bandung | Hotel | Bandung | Java | 200 | Upper Midscale |
| H003 | Mercure Grand Surabaya | Hotel | Surabaya | Java | 200 | Upper Midscale |
| H004 | Mercure Grand Yogyakarta | Hotel | Yogyakarta | Java | 200 | Midscale |
| H005 | Mercure Grand Bali | Hotel | Denpasar | Bali | 200 | Upper Midscale |
| H00 map | Mercure Grand Semarang | Hotel | Semarang | Java | 200 | Midscale |
| H007 | Mercure Grand Malang | Hotel | Malang | Java | 200 | Midscale |
| F001 | Mercure Food Hall | F&B | Jakarta | Java | — | F&B |
| F002 | Mercure Dining Group | F&B | Bandung | Java | — | F&B |

### Property alias → canonical mapping (excerpt)
| raw_alias | → property_id |
|---|---|---|---|---|
| `Mercure Grand Jakarta`, `MERCURE GRAND JAKARTA`, `Mercure Grand JKT`, `MG Jakarta`, `Mercure-Jakarta`, `MG JKT` | H001 |
| `Mercure Grand Bandung`, `MERCURE GRAND BANDUNG`, `Mercure Grand BDG`, `MG Bandung`, `MG BDG` | H002 |
| ... (5–6 aliases per property) | ... |

### dim_business_unit
| business_unit_id | business_unit_name | business_type |
|---|---|---|---|---|
| BU-HOTEL | Hotel Operations | Hotel |
| BU-FNB-1 | Mercure Food Hall | F&B |
| BU-FNB-2 | Mercure Dining Group | F&B |

### dim_department
D001 Rooms, D002 Food & Beverage, D003 Kitchen, D004 Engineering, D005 Sales & Marketing, D006 Administration, D007 Housekeeping.

### dim_product (~60 SKUs)
`product_id` (P001…), `product_name` canonical, `category_id` FK, `base_price`, `unit_cost_ratio` (recipe cost ratio), `active_flag`. **Product alias table** maps 4–5 raw variants → 1 product_id.

### dim_product_category
C001 Coffee, C002 Tea, C003 Breakfast, C004 Appetizer, C005 Main Course, C006 Rice & Noodles, C007 Dessert, C008 Beverage, C009 Snack.

### dim_account (~38 accounts)
`account_id`, `account_code`, `account_name`, `account_type` (Revenue / COGS / OPEX / Other), `department_id`. Revenue accounts 4000-series, COGS 5000-series, OPEX 6000-series.

### dim_customer_segment
Leisure, Corporate, OTA, Wholesale, Group, Wedding & Event.

### dim_channel
Direct Website, OTA, Corporate, GDS, Walk-in, WhatsApp.

### dim_room_type
Standard, Deluxe, Executive, Suite, Family (with rack-rate ladder and price multiplier).

### dim_supplier (~14)
S001… supplier_name, city, lead_time_days, payment_terms (synthetic 30 days).

### dim_date
Full daily calendar over 2025-01-01 → 2026-12-31 + 90 forecast days (2027-01-01 → 2027-03-31): date_key, full_date, year, quarter, month, month_name, day_of_week, day_name, is_weekend, is_holiday_flag, holiday_name (simplified set), day_of_year, week_of_year.

---

## 3. PRODUCT ALIAS MAPPING (excerpt)

| raw_variant | → product_id | canonical name |
|---|---|---|---|---|
| `COFFEE LATTE`, `Coffee Latte`, `coffee latte`, `Latte Coffee`, `LATTE - COFFEE` | P001 | Coffee Latte |
| `NASI GORENG SPESIAL`, `Nasi Goreng Spesial`, `nasi goreng spesial`, `Nasi Goreng Spcl`, `NASI GORENG SPSL` | P021 | Nasi Goreng Spesial |
| ... 60 products × ~4.5 aliases ≈ 270 alias rows |

---

## 4. ALIAS GENERATION RULE
Aliases constructed from canonical name by deterministic case transforms, abbreviations, word reorderings, and separator variants — seeded so the mapping table is reproducible and covers 100% of aliases actually used in raw data.

---

## 5. FACT TABLE GRAIN (explicit)

| Fact | Grain (1 row =) | PK | FKs |
|---|---|---|---|---|
| `fact_room_sales` | 1 room booking | booking_id | date_id (check_in), property_id, room_type_id, segment_id, channel_id |
| `fact_fnb_sales` | 1 POS product line | (transaction_id, line_no) | date_id, property_id, outlet (dim_property or business-unit outlet), product_id, category_id |
| `fact_inventory` | product × property × date | (product_id, property_id, date_id) | date_id, property_id, product_id |
| `fact_purchase` | 1 purchase line | purchase_line_id | date_id, property_id, product_id, supplier_id |
| `fact_expense` | 1 expense transaction | expense_id | date_id, property_id, department_id, account_id |
| `fact_budget` | property × department × account × month | (property_id, department_id, account_id, month_date_id) | month_date_id (dim_date month start), property_id, department_id, account_id |

**Grain guards (enforced in `07_validate.py`):**
- `fact_room_sales`: no duplicate booking_id; check_in < check_out after cleaning.
- `fact_fnb_sales`: no duplicate (transaction_id, line_no); net_sales ≤ gross_sales.
- `fact_inventory`: exactly one row per (product, property, date); opening = prior closing.
- `fact_purchase`: total_amount = quantity × unit_price (±0.01).
- `fact_budget`: exactly one row per (property, department, account, month).

---

## 6. FACT MEASURES

### fact_room_sales
`rooms_sold` (0 if cancelled/no-show), `room_nights` (LOS × sold), `room_revenue`, `adr_amount`, `is_cancelled`, `is_no_show`, `los`.

### fact_fnb_sales
`quantity`, `gross_sales`, `discount`, `net_sales`, `unit_price`, `is_void`, `is_refund`, `cogs_amount` (quantity × unit cost), `gross_profit` (net_sales − cogs).

### fact_inventory
`opening_stock`, `purchase_qty`, `transfer_qty`, `consumption_qty`, `waste_qty`, `closing_stock`, `stock_value`, `unit_cost`, `inventory_variance` (book closing − theoretical closing, where theoretical = opening + purchase − transfer − consumption − waste).

### fact_purchase
`quantity`, `unit_price`, `total_amount`.

### fact_expense
`amount`, `transaction_type` (Debit/Credit), `is_cogs` flag (account_type = COGS).

### fact_budget
`budget_amount`, `budget_year`, `budget_month`.

---

## 7. KPI FORMULAS (canonical business definitions)

All computed in marts and reused verbatim in DAX and the dashboard.

| KPI | Formula |
|---|---|---|---|---|
| Room Revenue | Σ room_revenue (fact_room_sales, rooms_sold = 1) |
| Available Room Nights | rooms × days in period (dim_property.rooms × dim_date) |
| Occupied Room Nights | Σ room_nights |
| Occupancy % | Occupied / Available × 100 |
| ADR | Room Revenue / Rooms Sold |
| RevPAR | Room Revenue / Available Room Nights |
| F&B Gross Sales | Σ gross_sales (is_void = 0) |
| F&B Net Revenue | Σ net_sales (is_void = 0, is_refund = 0) |
| F&B COGS | Σ cogs_amount |
| Food Cost % | F&B COGS / F&B Net Revenue × 100 |
| Gross Profit | Net Revenue − COGS |
| Gross Margin % | Gross Profit / Net Revenue × 100 |
| Total Revenue | Room Revenue + F&B Net Revenue + Other Income |
| OPEX | Σ fact_expense where account_type = OPEX |
| EBITDA | Total Revenue − COGS − OPEX |
| EBITDA Margin % | EBITDA / Total Revenue × 100 |
| Net Profit | EBITDA − D&A − Interest + Tax (synthetic simplified: EBITDA × 0.72) |
| Budget Achievement % | Actual / Budget × 100 |
| Variance | Actual − Budget |
| Variance % | (Actual − Budget) / Budget × 100 |
| Revenue YoY % | (Rev − Rev LY) / Rev LY × 100 |
| Revenue MoM % | (Rev − Rev LM) / Rev LM × 100 |
| Average Check | F&B Net Revenue / Transactions |
| Cancellation % | cancelled bookings / total bookings × 100 |
| No-show % | no-show bookings / total bookings × 100 |
| Avg LOS | Σ LOS / bookings (confirmed) |
| Waste Value | Σ waste_qty × unit_cost |
| Discount % | Σ discount / Σ gross_sales × 100 |
| Void % | void lines / total lines × 100 |

**Denominator guard:** every ratio measure is computed with NULLIF-style protection (division by zero → NULL, displayed as `—`).

---

## 8. RELATIONSHIPS (star schema)

```
dim_date ──< fact_room_sales >── dim_property
dim_room_type ──^                  dim_customer_segment ──^
dim_channel ──^

dim_date ──< fact_fnb_sales >── dim_property, dim_product >── dim_product_category

dim_date ──< fact_inventory >── dim_property, dim_product

dim_date ──< fact_purchase >── dim_property, dim_product, dim_supplier

dim_date ──< fact_expense >── dim_property, dim_department, dim_account

dim_date ──< fact_budget >── dim_property, dim_department, dim_account
```

All relationships **single direction** (dimension → fact). `dim_date` is the filter backbone for every fact. No bi-directional filtering (avoids ambiguity and performance traps).

---

## 9. DATA QUALITY FRAMEWORK (7 dimensions)

| Dimension | Check | Metric |
|---|---|---|---|---|
| Completeness | non-null on mandatory fields / total rows | % |
| Uniqueness | distinct PK / total rows | % |
| Validity | valid dates, codes, amounts, categories | % |
| Consistency | cross-source agreements (e.g. POS net sales vs finance revenue account) | % |
| Integrity | fact FKs existing in dims (referential integrity) | % |
| Timeliness | latest record date vs today | freshness days |
| Accuracy | business-rule checks (net ≤ gross, occupancy ≤ 100%, closing ≥ 0) | % |

**Quality score per source** = weighted mean of the six percentage dimensions. Tiered (Kintoun-style mirror, applied to data sources):
A ≥ 98 · B 95–98 · C 90–95 · D < 90.
Persisted in `mart_dq_source_health` and shown on Dashboard 06.

---

## 10. MART VIEWS (read path)

| View | Grain | Used by |
|---|---|---|---|---|
| `mart_kpi_daily` | date | Dashboard 01/02, forecast, anomaly, insights |
| `mart_hotel_monthly` | property × month | Dashboard 03 |
| `mart_fnb_monthly` | property × outlet × month | Dashboard 04 |
| `mart_finance_monthly` | property × month × account_type | Dashboard 05 |
| `mart_budget_vs_actual` | property × department × account × month | Dashboard 02/05 |
| `mart_dq_source_health` | source | Dashboard 06 |

---

## 11. LINEAGE & MAPPING TABLES

| Table | Purpose |
|---|---|---|---|---|
| `map_property_alias` | raw property string → property_id |
| `map_product_alias` | raw product string → product_id |
| `map_account_code` | raw account code → account_id |
| `map_category_alias` | raw category string → category_id |
| `etl_cleansing_log` | rule × records_affected × before/after evidence |
| `etl_batch_run` | pipeline run metadata (start, end, rows in/out, status) |

Every cleaned row carries `source_file` + `raw_row_number` for full traceability back to the raw file.

