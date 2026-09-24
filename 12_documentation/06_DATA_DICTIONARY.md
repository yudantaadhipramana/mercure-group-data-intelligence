# DATA DICTIONARY
# Hospitality & F&B Group Data Intelligence Demo — Powered by LensaData

Synthetic demonstration. All values fictional.

---

## WAREHOUSE TABLES

### dim_date
| Column | Type | Description |
|---|---|---|---|---|
| date_key | int | YYYYMMDD key |
| full_date | date | the date |
| year | int | 2025, 2026 (+ 2027 forecast days) |
| quarter | int | 1–4 |
| month | int | 1–12 |
| month_name | text | January… |
| day_of_week | int | Mon=0 |
| day_name | text | Monday… |
| is_weekend | int | 1 if Sat/Sun |
| is_holiday_flag | int | 1 if in simplified holiday set |
| holiday_name | text | holiday label (synthetic simplified) |
| day_of_year | int | 1–366 |
| week_of_year | int | ISO week |

### dim_property
| Column | Type | Description |
|---|---|---|---|---|
| property_id | text PK | H001–H007 (hotels), F001–F002 (F&B units) |
| property_name | text | canonical name |
| business_type | text | Hotel / F&B |
| city, region | text | location |
| rooms | int | room count (hotels) |
| class | text | Midscale / Upper Midscale |

### dim_business_unit, dim_department, dim_product_category, dim_customer_segment, dim_channel, dim_room_type, dim_supplier
Standard surrogate-keyed dims; columns documented in `05_DATA_DESIGN.md` §2.

### dim_product
| Column | Type | Description |
|---|---|---|---|---|
| product_id | text PK | P001… |
| product_name | text | canonical name |
| category_id | text FK | → dim_product_category |
| base_price | numeric | menu price (Rp) |
| unit_cost_ratio | numeric | recipe cost ratio (drives COGS) |
| active_flag | int | 1 |

### dim_account
| Column | Type | Description |
|---|---|---|---|---|
| account_id | text PK | A4000… |
| account_code | text | source code (4000-series revenue, 5000 COGS, 6000 OPEX) |
| account_name | text | canonical name |
| account_type | text | Revenue / COGS / OPEX |
| department_id | text FK | → dim_department |

### fact_room_sales
| Column | Type | Description |
|---|---|---|---|---|
| booking_id | text PK | source booking id |
| date_id | int FK | check-in date key |
| property_id, room_type_id, segment_id, channel_id | text FK | |
| los | int | length of stay |
| rooms_sold | int | 1 if Confirmed else 0 |
| room_nights | int | los × rooms_sold |
| room_revenue | numeric | rooms_sold × rate |
| adr_amount | numeric | rate |
| is_cancelled, is_no_show | int | flags |
| source_file, raw_row_number | text/int | lineage |

### fact_fnb_sales
| Column | Type | Description |
|---|---|---|---|---|
| transaction_id | text | POS transaction |
| line_no | int | line within transaction |
| date_id, property_id, outlet_id, product_id, category_id | FK | |
| quantity | numeric | units sold |
| gross_sales | numeric | price × qty |
| discount | numeric | discount value |
| net_sales | numeric | gross − discount − void/refund effect |
| unit_price | numeric | |
| cogs_amount | numeric | qty × unit cost |
| gross_profit | numeric | net_sales − cogs_amount |
| is_void, is_refund | int | flags |
| source_file, raw_row_number | | lineage |

### fact_inventory
| Column | Type | Description |
|---|---|---|---|---|
| date_id, property_id, product_id | PK/FK | grain: product × property × date |
| opening_stock, purchase_qty, transfer_qty, consumption_qty, waste_qty, closing_stock | numeric | units |
| unit_cost | numeric | moving-average cost |
| stock_value | numeric | closing × unit_cost |
| inventory_variance | numeric | book closing − theoretical closing |

### fact_purchase
purchase_line_id PK; date_id, property_id, product_id, supplier_id FK; quantity, unit_price, total_amount.

### fact_expense
expense_id PK; date_id, property_id, department_id, account_id FK; amount, transaction_type, is_cogs.

### fact_budget
(property_id, department_id, account_id, month_date_id) PK; budget_amount, budget_year, budget_month.

---

## MAPPING / LINEAGE TABLES

| Table | Columns | Purpose |
|---|---|---|---|---|
| map_property_alias | raw_alias (PK), property_id | dirty property string → canonical |
| map_product_alias | raw_alias (PK), product_id | dirty product string → canonical |
| map_account_code | raw_code (PK), account_id | account code → canonical |
| map_category_alias | raw_alias (PK), category_id | category string → canonical |
| etl_cleansing_log | rule_id, rule, source, records_affected, before_example, after_example | audit trail of every transformation |
| etl_batch_run | run_id, started_at, ended_at, stage, rows_in, rows_out, status | pipeline metadata |

---

## RAW SOURCE SCHEMAS (as extracted)
See `05_DATA_DESIGN.md` §1 for the six source schemas with their injected imperfections.
