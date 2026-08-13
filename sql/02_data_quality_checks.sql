-- =====================================================================
-- 02_data_quality_checks.sql
-- Sanity checks to run right after loading the data.
-- =====================================================================

-- Row counts per table
SELECT 'dim_product' AS table_name, COUNT(*) AS row_count FROM dim_product
UNION ALL
SELECT 'dim_supplier', COUNT(*) FROM dim_supplier
UNION ALL
SELECT 'dim_shipping', COUNT(*) FROM dim_shipping
UNION ALL
SELECT 'dim_location', COUNT(*) FROM dim_location
UNION ALL
SELECT 'fact_supply_chain', COUNT(*) FROM fact_supply_chain;

-- Null checks on key fact columns
SELECT
    SUM(CASE WHEN product_key  IS NULL THEN 1 ELSE 0 END) AS null_product_key,
    SUM(CASE WHEN supplier_key IS NULL THEN 1 ELSE 0 END) AS null_supplier_key,
    SUM(CASE WHEN shipping_key IS NULL THEN 1 ELSE 0 END) AS null_shipping_key,
    SUM(CASE WHEN revenue_generated IS NULL THEN 1 ELSE 0 END) AS null_revenue
FROM fact_supply_chain;

-- Duplicate SKUs (should be zero if dim_product is properly deduplicated)
SELECT sku, COUNT(*) AS occurrences
FROM dim_product
GROUP BY sku
HAVING COUNT(*) > 1;

-- Orphan fact rows (foreign keys that don't resolve to a dimension row)
SELECT COUNT(*) AS orphan_product_rows
FROM fact_supply_chain f
LEFT JOIN dim_product p ON f.product_key = p.product_key
WHERE p.product_key IS NULL;

-- Negative or implausible values worth flagging
SELECT record_id, revenue_generated, costs, shipping_costs, defect_rates
FROM fact_supply_chain
WHERE revenue_generated < 0
   OR costs < 0
   OR shipping_costs < 0
   OR defect_rates < 0;
