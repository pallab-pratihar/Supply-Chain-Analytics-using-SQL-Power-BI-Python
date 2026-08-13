-- =====================================================================
-- 06_root_cause_analysis.sql
-- Root-cause style queries linking defects, lead time, and cost to
-- find where the operational bottlenecks are coming from.
-- =====================================================================

-- Does a longer manufacturing lead time correlate with higher defect rates?
SELECT
    CASE
        WHEN manufacturing_lead_time <= 10 THEN '0-10 days'
        WHEN manufacturing_lead_time <= 20 THEN '11-20 days'
        ELSE '21+ days'
    END AS lead_time_bucket,
    COUNT(*) AS n_batches,
    ROUND(AVG(defect_rates), 2) AS avg_defect_rate
FROM fact_supply_chain
GROUP BY lead_time_bucket
ORDER BY lead_time_bucket;

-- Inspection failure concentration by supplier + transportation mode
SELECT
    s.supplier_name,
    sh.transportation_modes,
    COUNT(*) AS n_batches,
    SUM(CASE WHEN f.inspection_results = 'Fail' THEN 1 ELSE 0 END) AS n_failed,
    ROUND(SUM(CASE WHEN f.inspection_results = 'Fail' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) * 100, 2) AS fail_rate_pct
FROM fact_supply_chain f
JOIN dim_supplier s ON f.supplier_key = s.supplier_key
JOIN dim_shipping sh ON f.shipping_key = sh.shipping_key
GROUP BY s.supplier_name, sh.transportation_modes
HAVING COUNT(*) >= 1
ORDER BY fail_rate_pct DESC
LIMIT 15;

-- Cost overrun candidates: manufacturing cost higher than price (margin erosion)
SELECT
    pr.sku,
    pr.product_type,
    pr.price,
    f.manufacturing_costs,
    ROUND(f.manufacturing_costs - pr.price, 2) AS cost_over_price
FROM fact_supply_chain f
JOIN dim_product pr ON f.product_key = pr.product_key
WHERE f.manufacturing_costs > pr.price
ORDER BY cost_over_price DESC
LIMIT 15;

-- Route-level bottlenecks: routes with high lead time AND high cost
SELECT
    sh.routes,
    ROUND(AVG(f.lead_times), 2)     AS avg_lead_time,
    ROUND(AVG(f.costs), 2)          AS avg_cost,
    ROUND(AVG(f.defect_rates), 2)   AS avg_defect_rate,
    COUNT(*) AS n_shipments
FROM fact_supply_chain f
JOIN dim_shipping sh ON f.shipping_key = sh.shipping_key
GROUP BY sh.routes
ORDER BY avg_lead_time DESC, avg_cost DESC;
