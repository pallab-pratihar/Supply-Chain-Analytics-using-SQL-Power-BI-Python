# Power BI Dashboard — Build Guide

This folder contains everything needed to build the Power BI dashboard from this project:
a ready-to-import star-schema data model, the exact DAX measures for each KPI, and a
step-by-step guide to lay out the report pages.



## 1. Import the data model

1. Open **Power BI Desktop** → **Get Data → Text/CSV**.
2. Import these five files from `data/processed/` (already cleaned and de-duplicated):
   - `fact_supply_chain.csv` (fact table)
   - `dim_product.csv`
   - `dim_supplier.csv`
   - `dim_shipping.csv`
   - `dim_location.csv`
3. In **Model view**, create relationships (all one-to-many, single direction, from dim → fact):
   - `dim_product[product_key]` → `fact_supply_chain[product_key]`
   - `dim_supplier[supplier_key]` → `fact_supply_chain[supplier_key]`
   - `dim_shipping[shipping_key]` → `fact_supply_chain[shipping_key]`
   - `dim_location[location_key]` → `fact_supply_chain[location_key]`

This gives you a clean star schema — the same one the SQL scripts in `/sql` query against.

## 2. Add the DAX measures

Copy the measures from `DAX_measures.txt` into a new measures table (**Modeling → New Table**,
name it `_Measures`, then add each one via **New Measure**). They cover the four headline KPIs
plus supporting measures for profitability, quality, and shipping.

## 3. Build the report pages

### Page 1 — Executive Overview
| Visual | Fields |
|---|---|
| KPI cards (x4) | `Order Fill Rate %`, `Inventory Turnover`, `On-Time Delivery %`, `Warehouse Utilization %` |
| Card | `Total Revenue`, `Total Profit`, `Avg Profit Margin %` |
| Donut chart | Revenue by `dim_product[product_type]` |
| Map or bar chart | Revenue by `dim_location[location]` |
| Slicers | `product_type`, `location`, `supplier_name` |

### Page 2 — Inventory & Warehouse
| Visual | Fields |
|---|---|
| Bar chart | Avg Warehouse Utilization % by `location` |
| Bar chart | Avg Inventory Turnover by `product_type` |
| Table | SKUs with lowest Order Fill Rate (bottleneck candidates) |
| Scatter | Stock Levels vs. Order Quantities, colored by `product_type` |

### Page 3 — Supplier & Quality Performance
| Visual | Fields |
|---|---|
| Scatter chart | Avg Lead Time (x) vs. Avg Defect Rate (y), one point per `supplier_name` |
| Bar chart | Pass rate % by `supplier_name` |
| Box/column chart | Defect rate distribution by `inspection_results` |
| Table | Supplier performance ranking (defect rate + lead time) |

### Page 4 — Logistics & Delivery
| Visual | Fields |
|---|---|
| Bar chart | Shipment count by `transportation_modes` |
| Scatter | Avg shipping time vs. avg shipping cost, by `transportation_modes` |
| Bar chart | On-Time Delivery % by `shipping_carriers` |
| Bar chart | Avg lead time & cost by `routes` (root-cause / bottleneck view) |

### Page 5 — Root Cause & Recommendations
| Visual | Fields |
|---|---|
| Column chart | Avg defect rate by manufacturing lead-time bucket |
| Table | Route-level bottlenecks (lead time, cost, defect rate) |
| Text box | Key findings, pulled from `reports/insights_and_recommendations.md` |

## 4. Formatting tips
- Use a consistent theme: **View → Themes** → import a dark or brand theme for consistency
  with the chart styling used in `/visuals`.
- Add a top-level slicer panel (product type, location, supplier) so every page filters together.
- Turn on **Sync Slicers** (View → Sync Slicers) so filters persist across report pages.
- Publish to the Power BI Service and enable a scheduled refresh if you connect this to a
  live source instead of the static CSVs.

## 5. Files in this folder
- `DAX_measures.txt` — copy-paste-ready DAX for all KPIs
- `data_model_schema.md` — table/column reference and relationship diagram (text form)
- `dashboard_preview.png` — a static mock-up of the Executive Overview page layout, generated
  from this project's own data, so you can see the intended look before building it in Power BI
