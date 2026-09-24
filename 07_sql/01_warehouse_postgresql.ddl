===============================================================================
 MERCURE GROUP DATA WAREHOUSE — DDL (PostgreSQL — PRODUCTION TARGET)
 Hospitality & F&B Group Data Intelligence Demo — Powered by LensaData
===============================================================================
Synthetic demonstration. Mercure Group is a fictional business context.
This DDL is the production target. The local build executes the identical design
on DuckDB (PostgreSQL-compatible); see 02_warehouse_duckdb.sql for the few
engine-specific differences (indexes/serial vs identity).
===============================================================================

DROP SCHEMA IF EXISTS mercure CASCADE;
CREATE SCHEMA mercure;
SET search_path = mercure, public;

----------------------------------------------------------- DIMENSIONS ----------
CREATE TABLE dim_date (
    date_key        INTEGER      PRIMARY KEY,
    full_date       DATE         NOT NULL UNIQUE,
    year            SMALLINT     NOT NULL,
    quarter         SMALLINT     NOT NULL,
    month           SMALLINT     NOT NULL,
    month_name      TEXT         NOT NULL,
    day_of_week     SMALLINT     NOT NULL,
    day_name        TEXT         NOT NULL,
    is_weekend      SMALLINT     NOT NULL DEFAULT 0,
    is_holiday_flag SMALLINT     NOT NULL DEFAULT 0,
    holiday_name    TEXT,
    day_of_year     SMALLINT     NOT NULL,
    week_of_year    SMALLINT     NOT NULL
);

CREATE TABLE dim_property (
    property_id     TEXT         PRIMARY KEY,
    property_name   TEXT         NOT NULL,
    business_type   TEXT         NOT NULL CHECK (business_type IN ('Hotel','F&B')),
    city            TEXT         NOT NULL,
    region          TEXT         NOT NULL,
    rooms           INTEGER,
    property_class  TEXT
);

CREATE TABLE dim_business_unit (
    business_unit_id   TEXT      PRIMARY KEY,
    business_unit_name TEXT      NOT NULL,
    business_type      TEXT      NOT NULL
);

CREATE TABLE dim_department (
    department_id   TEXT         PRIMARY KEY,
    department_name TEXT         NOT NULL
);

CREATE TABLE dim_product_category (
    category_id     TEXT         PRIMARY KEY,
    category_name   TEXT         NOT NULL
);

CREATE TABLE dim_product (
    product_id      TEXT         PRIMARY KEY,
    product_name    TEXT         NOT NULL,
    category_id     TEXT         NOT NULL REFERENCES dim_product_category(category_id),
    base_price      NUMERIC(14,2) NOT NULL,
    unit_cost_ratio NUMERIC(6,4) NOT NULL,
    active_flag     SMALLINT     NOT NULL DEFAULT 1
);

CREATE TABLE dim_customer_segment (
    segment_id      TEXT         PRIMARY KEY,
    segment_name    TEXT         NOT NULL
);

CREATE TABLE dim_channel (
    channel_id      TEXT         PRIMARY KEY,
    channel_name    TEXT         NOT NULL
);

CREATE TABLE dim_room_type (
    room_type_id    TEXT         PRIMARY KEY,
    room_type_name  TEXT         NOT NULL,
    price_multiplier NUMERIC(6,3) NOT NULL
);

CREATE TABLE dim_account (
    account_id      TEXT         PRIMARY KEY,
    account_code    TEXT         NOT NULL,
    account_name    TEXT         NOT NULL,
    account_type    TEXT         NOT NULL CHECK (account_type IN ('Revenue','COGS','OPEX')),
    department_id   TEXT         REFERENCES dim_department(department_id)
);

CREATE TABLE dim_supplier (
    supplier_id        TEXT      PRIMARY KEY,
    supplier_name      TEXT      NOT NULL,
    city               TEXT,
    lead_time_days     INTEGER,
    payment_terms_days INTEGER
);

--------------------------------------------------------------- FACTS ----------
-- Grain documented in 12_documentation/05_DATA_DESIGN.md

CREATE TABLE fact_room_sales (
    booking_id        TEXT       PRIMARY KEY,
    date_id           INTEGER    NOT NULL REFERENCES dim_date(date_key),
    property_id       TEXT       NOT NULL REFERENCES dim_property(property_id),
    room_type_id      TEXT       REFERENCES dim_room_type(room_type_id),
    segment_id        TEXT       REFERENCES dim_customer_segment(segment_id),
    channel_id        TEXT       REFERENCES dim_channel(channel_id),
    los               INTEGER    NOT NULL,
    rooms_sold        INTEGER    NOT NULL DEFAULT 0,
    room_nights       INTEGER    NOT NULL DEFAULT 0,
    room_revenue      NUMERIC(16,2) NOT NULL DEFAULT 0,
    adr_amount        NUMERIC(16,2) NOT NULL DEFAULT 0,
    is_cancelled      SMALLINT   NOT NULL DEFAULT 0,
    is_no_show        SMALLINT   NOT NULL DEFAULT 0,
    source_file       TEXT,
    raw_row           INTEGER
);
CREATE INDEX idx_room_sales_date   ON fact_room_sales(date_id);
CREATE INDEX idx_room_sales_prop   ON fact_room_sales(property_id);
CREATE INDEX idx_room_sales_seg    ON fact_room_sales(segment_id);
CREATE INDEX idx_room_sales_chan   ON fact_room_sales(channel_id);

CREATE TABLE fact_fnb_sales (
    transaction_id    TEXT       NOT NULL,
    line_no           INTEGER    NOT NULL,
    date_id           INTEGER    NOT NULL REFERENCES dim_date(date_key),
    property_id       TEXT       NOT NULL REFERENCES dim_property(property_id),
    outlet_name       TEXT       NOT NULL,
    product_id        TEXT       NOT NULL REFERENCES dim_product(product_id),
    category_id       TEXT       NOT NULL REFERENCES dim_product_category(category_id),
    quantity          NUMERIC(12,3) NOT NULL DEFAULT 0,
    gross_sales       NUMERIC(16,2) NOT NULL DEFAULT 0,
    discount          NUMERIC(16,2) NOT NULL DEFAULT 0,
    net_sales         NUMERIC(16,2) NOT NULL DEFAULT 0,
    unit_price        NUMERIC(16,2) NOT NULL DEFAULT 0,
    cogs_amount       NUMERIC(16,2) NOT NULL DEFAULT 0,
    gross_profit      NUMERIC(16,2) NOT NULL DEFAULT 0,
    is_void           SMALLINT   NOT NULL DEFAULT 0,
    is_refund         SMALLINT   NOT NULL DEFAULT 0,
    source_file       TEXT,
    raw_row           INTEGER,
    PRIMARY KEY (transaction_id, line_no)
);
CREATE INDEX idx_fnb_sales_date   ON fact_fnb_sales(date_id);
CREATE INDEX idx_fnb_sales_prop   ON fact_fnb_sales(property_id);
CREATE INDEX idx_fnb_sales_prod   ON fact_fnb_sales(product_id);
CREATE INDEX idx_fnb_sales_outlet ON fact_fnb_sales(outlet_name);

CREATE TABLE fact_inventory (
    date_id           INTEGER    NOT NULL REFERENCES dim_date(date_key),
    property_id       TEXT       NOT NULL REFERENCES dim_property(property_id),
    product_id        TEXT       NOT NULL REFERENCES dim_product(product_id),
    opening_stock     NUMERIC(14,3) NOT NULL DEFAULT 0,
    purchase_qty      NUMERIC(14,3) NOT NULL DEFAULT 0,
    transfer_qty      NUMERIC(14,3) NOT NULL DEFAULT 0,
    consumption_qty   NUMERIC(14,3) NOT NULL DEFAULT 02,
    waste_qty         NUMERIC(14,3) NOT NULL DEFAULT 0,
    closing_stock     NUMERIC(14,3) NOT NULL DEFAULT 0,
    unit_cost         NUMERIC(16,2) NOT NULL DEFAULT 0,
    stock_value       NUMERIC(16,2) NOT NULL DEFAULT 0,
    inventory_variance NUMERIC(16,3) NOT NULL DEFAULT 0,
    PRIMARY KEY (date_id, property_id, product_id)
);
CREATE INDEX idx_inventory_prop   ON fact_inventory(property_id);
CREATE INDEX idx_inventory_prod   ON fact_inventory(product_id);

CREATE TABLE fact_purchase (
    purchase_line_id  TEXT       PRIMARY KEY,
    date_id           INTEGER    NOT NULL REFERENCES dim_date(date_key),
    property_id       TEXT       NOT NULL REFERENCES dim_property(property_id),
    product_id        TEXT       NOT NULL REFERENCES dim_product(product_id),
    supplier_id       TEXT       NOT NULL REFERENCES dim_supplier(supplier_id),
    quantity          NUMERIC(14,3) NOT NULL DEFAULT 0,
    unit_price        NUMERIC(16,2) NOT NULL DEFAULT 0,
    total_amount      NUMERIC(16,2) NOT NULL DEFAULT 0
);
CREATE INDEX idx_purchase_date ON fact_purchase(date_id);
CREATE INDEX idx_purchase_prop ON fact_purchase(property_id);

CREATE TABLE fact_expense (
    expense_id        TEXT       PRIMARY KEY,
    date_id           INTEGER    NOT NULL REFERENCES dim_date(date_key),
    property_id       TEXT       NOT NULL REFERENCES dim_property(property_id),
    department_id     TEXT       NOT NULL REFERENCES dim_department(department_id),
    account_id        TEXT       NOT NULL REFERENCES dim_account(account_id),
    amount            NUMERIC(16,2) NOT NULL DEFAULT 0,
    transaction_type  TEXT       NOT NULL CHECK (transaction_type IN ('Debit','Credit')),
    is_cogs           SMALLINT   NOT NULL DEFAULT 0,
    source_file       TEXT,
    raw_row           INTEGER
);
CREATE INDEX idx_expense_date ON fact_expense(date_id);
CREATE INDEX idx_expense_prop ON fact_expense(property_id);
CREATE INDEX idx_expense_acc  ON fact_expense(account_id);

CREATE TABLE fact_budget (
    date_id           INTEGER    NOT NULL REFERENCES dim_date(date_key),
    property_id       TEXT       NOT NULL REFERENCES dim_property(property_id),
    department_id     TEXT       NOT NULL REFERENCES dim_department(department_id),
    account_id        TEXT       NOT NULL REFERENCES dim_account(account_id),
    budget_amount     NUMERIC(16,2) NOT NULL DEFAULT 0,
    budget_year       INTEGER    NOT NULL,
    budget_month      INTEGER    NOT NULL,
    PRIMARY KEY (date_id, property_id, department_id, account_id)
);
CREATE INDEX idx_budget_prop ON fact_budget(property_id);
CREATE INDEX idx_budget_acc  ON fact_budget(account_id);

------------------------------------------------- MAPPING / LINEAGE ----------
CREATE TABLE map_property_alias (
    raw_alias    TEXT PRIMARY KEY,
    property_id  TEXT NOT NULL REFERENCES dim_property(property_id)
);
CREATE TABLE map_product_alias (
    raw_alias    TEXT PRIMARY KEY,
    product_id   TEXT NOT NULL REFERENCES dim_product(product_id)
);
CREATE TABLE map_account_alias (
    raw_alias    TEXT PRIMARY KEY,
    account_id   TEXT NOT NULL REFERENCES dim_account(account_id)
);
CREATE TABLE map_category_alias (
    raw_alias    TEXT PRIMARY KEY,
    category_id  TEXT NOT NULL REFERENCES dim_product_category(category_id)
);

CREATE TABLE etl_cleansing_log (
    log_id           BIGSERIAL PRIMARY KEY,
    rule             TEXT NOT NULL,
    source           TEXT NOT NULL,
    records_affected INTEGER NOT NULL,
    before_example   TEXT,
    after_example    TEXT
);

CREATE TABLE etl_batch_run (
    run_id     BIGSERIAL PRIMARY KEY,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    ended_at   TIMESTAMP,
    stage      TEXT NOT NULL,
    rows_in    BIGINT,
    rows_out   BIGINT,
    status     TEXT NOT NULL
);
===============================================================================
