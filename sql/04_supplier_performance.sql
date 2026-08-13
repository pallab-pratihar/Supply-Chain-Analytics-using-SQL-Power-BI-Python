-- =====================================================================
-- 04_supplier_performance.sql
-- Supplier and shipping-carrier performance analysis.
-- =====================================================================

-- Manufacturing cost and quality by supplier
SELECT
    s.supplier_name,
    COUNT(*)                                             AS n_orders,
    ROUND(SUM(f.manufacturing_costs), 2)                  AS total_manufacturing_cost,
    ROUND(AVG(f.defect_rates), 2)                          AS avg_defect_rate,
    ROUND(SUM(f.quality_pass_flag) * 1.0 / COUNT(*) * 100, 2) AS pass_rate_pct,
    ROUND(AVG(f.lead_times), 2)                            AS avg_lead_time_days
FROM fact_supply_chain f
JOIN dim_supplier s ON f.supplier_key = s.supplier_key
GROUP BY s.supplier_name
ORDER BY avg_defect_rate DESC;

-- Rank suppliers by a simple composite score (lower defect + lower lead time = better)
SELECT
    supplier_name,
    avg_defect_rate,
    avg_lead_time_days,
    RANK() OVER (ORDER BY avg_defect_rate ASC, avg_lead_time_days ASC) AS performance_rank
FROM (
    SELECT
        s.supplier_name,
        ROUND(AVG(f.defect_rates), 2) AS avg_defect_rate,
        ROUND(AVG(f.lead_times), 2)   AS avg_lead_time_days
    FROM fact_supply_chain f
    JOIN dim_supplier s ON f.supplier_key = s.supplier_key
    GROUP BY s.supplier_name
) t
ORDER BY performance_rank;

-- Shipping carrier cost & speed comparison
SELECT
    sh.shipping_carriers,
    COUNT(*)                                AS n_shipments,
    ROUND(AVG(f.shipping_costs), 2)          AS avg_shipping_cost,
    ROUND(AVG(f.shipping_times), 2)          AS avg_shipping_time_days,
    ROUND(SUM(f.on_time_delivery_flag) * 1.0 / COUNT(*) * 100, 2) AS on_time_pct
FROM fact_supply_chain f
JOIN dim_shipping sh ON f.shipping_key = sh.shipping_key
GROUP BY sh.shipping_carriers
ORDER BY on_time_pct DESC;

-- Transportation mode efficiency (cost per shipment vs. speed)
SELECT
    sh.transportation_modes,
    ROUND(AVG(f.shipping_costs), 2) AS avg_shipping_cost,
    ROUND(AVG(f.shipping_times), 2) AS avg_shipping_time_days,
    ROUND(SUM(f.total_shipping_cost), 2) AS total_shipping_cost
FROM fact_supply_chain f
JOIN dim_shipping sh ON f.shipping_key = sh.shipping_key
GROUP BY sh.transportation_modes
ORDER BY total_shipping_cost DESC;
