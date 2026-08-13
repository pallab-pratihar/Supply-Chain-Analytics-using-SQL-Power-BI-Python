"""
03_kpi_analysis.py
--------------------
Computes the headline KPIs and root-cause findings and writes a plain-text
summary to reports/kpi_summary.txt. This mirrors sql/03_kpi_queries.sql and
sql/06_root_cause_analysis.sql but in pandas, useful for quick checks or for
environments without a SQL engine set up.

Run from the repo root (after 01_data_cleaning.py):
    python python/03_kpi_analysis.py
"""

import pandas as pd
from pathlib import Path

DATA = Path("data/processed/supply_chain_cleaned.csv")
OUT = Path("reports")
OUT.mkdir(exist_ok=True)


def main():
    df = pd.read_csv(DATA)
    lines = []

    def log(msg=""):
        print(msg)
        lines.append(msg)

    log("=" * 70)
    log("SUPPLY CHAIN KPI SUMMARY")
    log("=" * 70)

    ofr = df["order_fill_rate"].mean()
    turnover = df["inventory_turnover"].mean()
    otd = df["on_time_delivery_flag"].mean() * 100
    wh_util = df["warehouse_utilization_pct"].mean()
    total_revenue = df["revenue_generated"].sum()
    total_profit = df["profit"].sum()
    avg_margin = df["profit_margin_pct"].mean()

    log(f"Total Revenue:              ${total_revenue:,.2f}")
    log(f"Total Profit:                ${total_profit:,.2f}")
    log(f"Average Profit Margin:        {avg_margin:.2f}%")
    log(f"Order Fill Rate:              {ofr:.2f}%")
    log(f"Inventory Turnover:           {turnover:.2f}x")
    log(f"On-Time Delivery Rate:        {otd:.2f}%")
    log(f"Avg Warehouse Utilization:    {wh_util:.2f}%")

    log("\n" + "-" * 70)
    log("KPIs BY PRODUCT TYPE")
    log("-" * 70)
    by_product = df.groupby("product_type").agg(
        order_fill_rate=("order_fill_rate", "mean"),
        inventory_turnover=("inventory_turnover", "mean"),
        on_time_delivery_pct=("on_time_delivery_flag", "mean"),
        revenue=("revenue_generated", "sum"),
        profit=("profit", "sum"),
    ).round(2)
    by_product["on_time_delivery_pct"] *= 100
    log(by_product.to_string())

    log("\n" + "-" * 70)
    log("SUPPLIER PERFORMANCE (sorted by defect rate)")
    log("-" * 70)
    supplier_perf = df.groupby("supplier_name").agg(
        avg_defect_rate=("defect_rates", "mean"),
        avg_lead_time=("lead_times", "mean"),
        pass_rate_pct=("quality_pass_flag", "mean"),
    ).round(2)
    supplier_perf["pass_rate_pct"] *= 100
    supplier_perf = supplier_perf.sort_values("avg_defect_rate", ascending=False)
    log(supplier_perf.to_string())

    log("\n" + "-" * 70)
    log("ROOT CAUSE: MANUFACTURING LEAD TIME vs. DEFECT RATE")
    log("-" * 70)
    bins = [0, 10, 20, df["manufacturing_lead_time"].max() + 1]
    labels = ["0-10 days", "11-20 days", "21+ days"]
    df["lead_time_bucket"] = pd.cut(df["manufacturing_lead_time"], bins=bins, labels=labels)
    lt_defect = df.groupby("lead_time_bucket", observed=True)["defect_rates"].mean().round(2)
    log(lt_defect.to_string())

    log("\n" + "-" * 70)
    log("BOTTLENECK CANDIDATES: LOWEST ORDER FILL RATE SKUs")
    log("-" * 70)
    bottlenecks = df.nsmallest(10, "order_fill_rate")[
        ["sku", "product_type", "order_quantities", "number_of_products_sold", "order_fill_rate"]
    ]
    log(bottlenecks.to_string(index=False))

    log("\n" + "-" * 70)
    log("ROUTE-LEVEL BOTTLENECKS (lead time & cost)")
    log("-" * 70)
    route_perf = df.groupby("routes").agg(
        avg_lead_time=("lead_times", "mean"),
        avg_cost=("costs", "mean"),
        avg_defect_rate=("defect_rates", "mean"),
    ).round(2).sort_values("avg_lead_time", ascending=False)
    log(route_perf.to_string())

    (OUT / "kpi_summary.txt").write_text("\n".join(lines))
    print("\nSaved -> reports/kpi_summary.txt")


if __name__ == "__main__":
    main()
