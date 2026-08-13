-- =====================================================================
-- 05_inventory_analysis.sql
-- Inventory, stock, and warehouse-utilization analysis.
-- =====================================================================

-- Stock health by product type: low stock relative to demand = risk of stockout
SELECT
    p.product_type,
    ROUND(AVG(f.stock_levels), 2)        AS avg_stock_level,
    ROUND(AVG(f.order_quantities), 2)    AS avg_order_quantity,
    ROUND(AVG(f.inventory_turnover), 2)  AS avg_inventory_turnover,
    CASE
        WHEN AVG(f.stock_levels) < AVG(f.order_quantities) THEN 'At Risk of Stockout'
        ELSE 'Healthy'
    END AS stock_risk_flag
FROM fact_supply_chain f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_type
ORDER BY avg_inventory_turnover DESC;

-- Warehouse utilization by location
SELECT
    l.location,
    ROUND(AVG(f.warehouse_utilization_pct), 2) AS avg_warehouse_utilization_pct,
    ROUND(SUM(f.stock_levels), 0)               AS total_stock_units,
    ROUND(SUM(f.order_quantities), 0)           AS total_order_units
FROM fact_supply_chain f
JOIN dim_location l ON f.location_key = l.location_key
GROUP BY l.location
ORDER BY avg_warehouse_utilization_pct DESC;

-- SKUs with the lowest fill rate (operational bottleneck candidates)
SELECT
    pr.sku,
    pr.product_type,
    f.order_quantities,
    f.number_of_products_sold,
    f.order_fill_rate
FROM fact_supply_chain f
JOIN dim_product pr ON f.product_key = pr.product_key
ORDER BY f.order_fill_rate ASC
LIMIT 10;

-- Slow-moving inventory: high stock, low turnover
SELECT
    pr.sku,
    pr.product_type,
    f.stock_levels,
    f.inventory_turnover
FROM fact_supply_chain f
JOIN dim_product pr ON f.product_key = pr.product_key
WHERE f.inventory_turnover < (SELECT AVG(inventory_turnover) FROM fact_supply_chain)
ORDER BY f.stock_levels DESC
LIMIT 10;
