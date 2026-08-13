# Methodology

## 1. Data Cleaning
- Standardized column names to snake_case.
- Checked for nulls and duplicate rows (none found in the source data).
- Added a surrogate `record_id` primary key.

## 2. KPI Definitions

Since the raw dataset has no native "fill rate," "turnover," or "on-time" fields, each KPI
was derived from the closest available columns. These definitions are used consistently
across the SQL queries, the Python analysis, and the Power BI DAX measures.

| KPI | Formula | Rationale |
|---|---|---|
| Order Fill Rate | `number_of_products_sold / order_quantities` (capped at 100%) | Standard fill-rate definition: how much of demand was actually fulfilled. |
| Inventory Turnover | `number_of_products_sold / stock_levels` | Classic turnover ratio: how many times stock "turned over" relative to sales. |
| On-Time Delivery | 1 if `shipping_times <= median shipping time for that transportation mode`, else 0 | The dataset has no promised/actual delivery date, so on-time is defined relative to each mode's typical (median) shipping time — a reasonable proxy for "faster/slower than expected." |
| Warehouse Utilization | `stock_levels / (stock_levels + order_quantities)` | Approximates how much of total warehouse "demand" (stock + open orders) is currently held as stock. |

These are proxies built to be directionally useful and reproducible from the available
columns — they are documented here so anyone reviewing the project can see exactly how each
number was derived and adjust the formulas if a stricter definition (e.g. based on service-level
targets or promised delivery dates) becomes available.

## 3. Star Schema Design

The flat CSV was normalized into a star schema (`fact_supply_chain` + four dimension tables)
to:
- Match how the KPIs would be modeled in a real BI/warehouse environment.
- Make the SQL queries and Power BI relationships easy to follow.
- Avoid repeating supplier/shipping/product attributes across every row.

See `powerbi/data_model_schema.md` for the full table and relationship reference.

## 4. Tools & Why

- **SQL** — used for the KPI, supplier-performance, inventory, and root-cause queries,
  written to be portable across SQLite/PostgreSQL/MySQL/SQL Server.
- **Python (pandas, matplotlib, seaborn)** — used for data cleaning, exploratory analysis,
  and static chart generation for the README/reports.
- **Power BI** — used for the interactive KPI dashboard. The DAX measures mirror the SQL/Python
  KPI definitions exactly, so all three layers agree on the numbers.
