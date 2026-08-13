# Supply Chain Analytics — Insights & Recommendations

**Data:** 100 SKU-level supply chain records (product, supplier, shipping, and quality attributes)
**Tools used:** SQL (star schema + KPI/root-cause queries), Python (pandas EDA), Power BI (KPI dashboard)

---

## 1. Headline KPIs

| KPI | Value |
|---|---|
| Total Revenue | $577,604.82 |
| Total Profit | $524,680.24 |
| Average Profit Margin | 87.44% |
| Order Fill Rate | 97.93% |
| Inventory Turnover | 28.88x |
| On-Time Delivery Rate | **61.00%** |
| Avg Warehouse Utilization | 47.38% |

**Takeaway:** Order fulfillment and margins are strong, but **on-time delivery is the weakest
KPI at 61%** — more than a third of shipments arrive later than the median for their
transportation mode. This is the single biggest lever for operational improvement.

## 2. Product-Line Performance

| Product Type | Order Fill Rate | Inventory Turnover | On-Time Delivery | Revenue | Profit |
|---|---|---|---|---|---|
| Skincare | 100.0% | 45.4x | 65% | $241,628 | $219,399 |
| Haircare | 95.7% | 18.5x | 62% | $174,455 | $157,127 |
| Cosmetics | 97.6% | 16.6x | 54% | $161,521 | $148,155 |

**Takeaway:** Skincare is the strongest line across every metric — highest fill rate, by far
the highest inventory turnover, and the best delivery performance. **Cosmetics is the laggard**,
with the lowest on-time delivery rate and the lowest revenue/profit contribution. Cosmetics
warrants a closer look at its specific suppliers and shipping lanes.

## 3. Supplier Performance

| Supplier | Avg Defect Rate | Avg Lead Time | Pass Rate |
|---|---|---|---|
| Supplier 1 | 1.80% | 16.8 days | 48% |
| Supplier 4 | 2.34% | 17.0 days | 0% |
| Supplier 2 | 2.36% | 16.2 days | 23% |
| Supplier 3 | 2.47% | 14.3 days | 13% |
| Supplier 5 | 2.67% | 14.7 days | 17% |

**Takeaway:** Supplier 1 is the clear top performer — lowest defect rate and highest pass
rate. **Supplier 4 has a 0% pass rate** despite an average defect rate, which is a red flag
worth investigating (possibly a data/inspection-process issue as much as a supplier
performance issue) and a strong candidate for a supplier audit.

## 4. Root Cause: Manufacturing Lead Time vs. Defect Rate

| Manufacturing Lead Time | Avg Defect Rate |
|---|---|
| 0–10 days | 2.11% |
| 11–20 days | 2.07% |
| 21+ days | **2.66%** |

**Takeaway:** Defect rates climb noticeably once manufacturing lead time exceeds 20 days.
This points to a quality-control gap on longer production runs — batches held or produced
over longer windows may need an added inspection checkpoint partway through, not just at
the end.

## 5. Logistics & Routing

| Route | Avg Lead Time | Avg Cost | Avg Defect Rate |
|---|---|---|---|
| Route B | 17.22 days | $595.66 | 2.32% |
| Route C | 16.35 days | $500.47 | 2.05% |
| Route A | 14.70 days | $485.48 | 2.34% |

**Takeaway:** **Route B is both the slowest and the most expensive**, with an above-average
defect rate too — it's the single clearest bottleneck in the logistics network and the best
candidate for renegotiating carrier terms or shifting volume to Route A/C.

## 6. Bottleneck SKUs (Lowest Order Fill Rate)

The lowest-performing SKUs by fill rate (`SKU2`, `SKU85`, `SKU45`) sit far below the 97.9%
average, each filling under half of ordered quantity. These are the first candidates for a
stock-level or demand-forecasting review — see `sql/05_inventory_analysis.sql` for the full
"at risk of stockout" query.

---

## Recommendations

1. **Prioritize on-time delivery.** At 61%, this is the weakest KPI and the one most likely
   to affect customer satisfaction. Start with Carrier A (lowest on-time % of the three
   carriers) and Route B (slowest, most expensive route).
2. **Audit Supplier 4.** A 0% inspection pass rate alongside a mid-range defect rate suggests
   either a genuine quality problem or an inspection/data-recording issue — both are worth
   resolving.
3. **Add a mid-production quality checkpoint** for manufacturing runs over 20 days, since
   defect rates rise meaningfully past that threshold.
4. **Investigate cosmetics-line delivery performance** specifically — it lags the other two
   product lines on on-time delivery and would benefit from a supplier/route breakdown
   filtered to that category (this is a one-click filter in the Power BI dashboard).
5. **Review stock policy for the lowest-fill-rate SKUs** to prevent recurring stockouts.

---

*Full query logic: `/sql`. Full exploratory analysis: `/python/supply_chain_analysis.ipynb`.
Interactive dashboard build: `/powerbi`.*
