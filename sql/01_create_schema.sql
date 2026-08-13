-- =====================================================================
-- 01_create_schema.sql
-- Creates the star-schema tables used for the supply chain analysis.
-- Compatible with SQLite / MySQL / PostgreSQL / SQL Server (minor type
-- tweaks may be needed depending on engine).
-- Load order: dim tables first, then the fact table.
-- =====================================================================

DROP TABLE IF EXISTS fact_supply_chain;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_supplier;
DROP TABLE IF EXISTS dim_shipping;
DROP TABLE IF EXISTS dim_location;

CREATE TABLE dim_product (
    product_key     INTEGER PRIMARY KEY,
    sku             TEXT NOT NULL,
    product_type    TEXT,
    price           NUMERIC
);

CREATE TABLE dim_supplier (
    supplier_key    INTEGER PRIMARY KEY,
    supplier_name   TEXT,
    location        TEXT
);

CREATE TABLE dim_shipping (
    shipping_key        INTEGER PRIMARY KEY,
    shipping_carriers   TEXT,
    transportation_modes TEXT,
    routes               TEXT
);

CREATE TABLE dim_location (
    location_key    INTEGER PRIMARY KEY,
    location        TEXT
);

CREATE TABLE fact_supply_chain (
    record_id                  INTEGER PRIMARY KEY,
    product_key                INTEGER REFERENCES dim_product(product_key),
    supplier_key                INTEGER REFERENCES dim_supplier(supplier_key),
    shipping_key                INTEGER REFERENCES dim_shipping(shipping_key),
    location_key                INTEGER REFERENCES dim_location(location_key),
    availability                 INTEGER,
    number_of_products_sold      INTEGER,
    revenue_generated            NUMERIC,
    customer_demographics        TEXT,
    stock_levels                 INTEGER,
    lead_times                   INTEGER,
    order_quantities             INTEGER,
    shipping_times                INTEGER,
    shipping_costs                 NUMERIC,
    production_volumes             INTEGER,
    manufacturing_lead_time         INTEGER,
    manufacturing_costs             NUMERIC,
    inspection_results               TEXT,
    defect_rates                     NUMERIC,
    costs                            NUMERIC,
    order_fill_rate                   NUMERIC,
    inventory_turnover                NUMERIC,
    on_time_delivery_flag              INTEGER,
    warehouse_utilization_pct          NUMERIC,
    profit                             NUMERIC,
    profit_margin_pct                  NUMERIC,
    total_shipping_cost                NUMERIC,
    is_defective_batch                 INTEGER,
    quality_pass_flag                  INTEGER
);

-- Helpful indexes for the KPI/analysis queries
CREATE INDEX idx_fact_product   ON fact_supply_chain(product_key);
CREATE INDEX idx_fact_supplier  ON fact_supply_chain(supplier_key);
CREATE INDEX idx_fact_shipping  ON fact_supply_chain(shipping_key);
CREATE INDEX idx_fact_location  ON fact_supply_chain(location_key);
