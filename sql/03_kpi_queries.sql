-- =====================================================================
-- 03_kpi_queries.sql
-- The four headline KPIs called out in the project: Order Fill Rate,
-- Inventory Turnover, On-Time Delivery, Warehouse Utilization.
-- These are the same metrics wired up as DAX measures in Power BI
-- (see powerbi/DAX_measures.txt).
-- =====================================================================

-- 1) Overall Order Fill Rate (%)
SELECT
    ROUND(SUM(number_of_products_sold) * 1.0 / NULLIF(SUM(order_quantities), 0) * 100, 2) AS order_fill_rate_pct
FROM fact_supply_chain;

-- 2) Overall Inventory Turnover (products sold per unit of stock held)
SELECT
    ROUND(SUM(number_of_products_sold) * 1.0 / NULLIF(SUM(stock_levels), 0), 2) AS inventory_turnover
FROM fact_supply_chain;

-- 3) On-Time Delivery Rate (%)
SELECT
    ROUND(SUM(on_time_delivery_flag) * 1.0 / COUNT(*) * 100, 2) AS on_time_delivery_pct
FROM fact_supply_chain;

-- 4) Warehouse Utilization (%)
SELECT
    ROUND(AVG(warehouse_utilization_pct), 2) AS avg_warehouse_utilization_pct
FROM fact_supply_chain;

-- 5) All four KPIs broken out by product type (for the dashboard's category view)
SELECT
    p.product_type,
    ROUND(SUM(f.number_of_products_sold) * 1.0 / NULLIF(SUM(f.order_quantities), 0) * 100, 2) AS order_fill_rate_pct,
    ROUND(SUM(f.number_of_products_sold) * 1.0 / NULLIF(SUM(f.stock_levels), 0), 2) AS inventory_turnover,
    ROUND(SUM(f.on_time_delivery_flag) * 1.0 / COUNT(*) * 100, 2) AS on_time_delivery_pct,
    ROUND(AVG(f.warehouse_utilization_pct), 2) AS avg_warehouse_utilization_pct,
    ROUND(SUM(f.revenue_generated), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit
FROM fact_supply_chain f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_type
ORDER BY total_revenue DESC;

-- 6) KPI trend by location (proxy for a time-series view since the dataset has no date field)
SELECT
    l.location,
    ROUND(SUM(f.revenue_generated), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2)            AS total_profit,
    ROUND(AVG(f.lead_times), 2)        AS avg_lead_time_days,
    ROUND(SUM(f.on_time_delivery_flag) * 1.0 / COUNT(*) * 100, 2) AS on_time_delivery_pct
FROM fact_supply_chain f
JOIN dim_location l ON f.location_key = l.location_key
GROUP BY l.location
ORDER BY total_revenue DESC;
