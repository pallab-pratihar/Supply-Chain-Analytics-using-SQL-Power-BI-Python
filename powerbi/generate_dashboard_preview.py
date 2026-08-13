"""
generate_dashboard_preview.py
-------------------------------
Builds a static mock-up image of the Power BI "Executive Overview" page
using this project's real KPI numbers, so the repo has a visual preview
of the intended dashboard before it's built in Power BI Desktop.

Run from the repo root:
    python powerbi/generate_dashboard_preview.py
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pathlib import Path

DATA = Path("data/processed/supply_chain_cleaned.csv")
OUT = Path("powerbi/dashboard_preview.png")

BG = "#F3F2F1"
CARD_BG = "#FFFFFF"
ACCENT = "#118DFF"
TEXT_DARK = "#252423"
TEXT_GRAY = "#605E5C"


def card(ax, x, y, w, h, title, value, subtitle=None, color=ACCENT):
    box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.01,rounding_size=0.02",
                                  linewidth=0, facecolor=CARD_BG, transform=ax.transAxes)
    ax.add_patch(box)
    ax.text(x + 0.02, y + h - 0.03, title, transform=ax.transAxes,
             fontsize=10, color=TEXT_GRAY, va="top", ha="left")
    ax.text(x + 0.02, y + h * 0.42, value, transform=ax.transAxes,
             fontsize=20, color=color, va="center", ha="left", fontweight="bold")
    if subtitle:
        ax.text(x + 0.02, y + 0.03, subtitle, transform=ax.transAxes,
                 fontsize=8, color=TEXT_GRAY, va="bottom", ha="left")


def main():
    df = pd.read_csv(DATA)

    total_revenue = df["revenue_generated"].sum()
    total_profit = df["profit"].sum()
    ofr = df["order_fill_rate"].mean()
    turnover = df["inventory_turnover"].mean()
    otd = df["on_time_delivery_flag"].mean() * 100
    wh_util = df["warehouse_utilization_pct"].mean()

    fig = plt.figure(figsize=(14, 8), facecolor=BG)
    fig.suptitle("Supply Chain Analytics — Executive Overview  (Power BI mock-up preview)",
                 fontsize=14, color=TEXT_DARK, x=0.02, ha="left", fontweight="bold", y=0.98)
    fig.text(0.02, 0.945, "Preview generated from project data — build the live version in Power BI Desktop using powerbi/README.md",
              fontsize=8.5, color=TEXT_GRAY)

    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.set_facecolor(BG)

    # KPI cards row
    card(ax, 0.02, 0.78, 0.155, 0.13, "TOTAL REVENUE", f"${total_revenue:,.0f}")
    card(ax, 0.19, 0.78, 0.155, 0.13, "TOTAL PROFIT", f"${total_profit:,.0f}", color="#107C10")
    card(ax, 0.36, 0.78, 0.155, 0.13, "ORDER FILL RATE", f"{ofr:.1f}%")
    card(ax, 0.53, 0.78, 0.155, 0.13, "INVENTORY TURNOVER", f"{turnover:.1f}x")
    card(ax, 0.70, 0.78, 0.145, 0.13, "ON-TIME DELIVERY", f"{otd:.0f}%", color="#D83B01")
    card(ax, 0.855, 0.78, 0.13, 0.13, "WAREHOUSE UTIL.", f"{wh_util:.0f}%")

    # Revenue by product type (donut)
    ax_donut = fig.add_axes([0.03, 0.42, 0.28, 0.32])
    rev = df.groupby("product_type")["revenue_generated"].sum().sort_values(ascending=False)
    colors = ["#118DFF", "#12239E", "#E66C37"]
    wedges, _ = ax_donut.pie(rev.values, colors=colors, startangle=90,
                              wedgeprops=dict(width=0.4))
    ax_donut.legend(wedges, [f"{i} ({v/rev.sum()*100:.0f}%)" for i, v in rev.items()],
                     loc="center", fontsize=8, frameon=False)
    ax_donut.set_title("Revenue by Product Type", fontsize=10, color=TEXT_DARK, loc="left")

    # Revenue by location (bar)
    ax_bar = fig.add_axes([0.35, 0.42, 0.30, 0.32])
    rev_loc = df.groupby("location")["revenue_generated"].sum().sort_values(ascending=False)
    ax_bar.barh(rev_loc.index[::-1], rev_loc.values[::-1], color=ACCENT)
    ax_bar.set_title("Revenue by Location", fontsize=10, color=TEXT_DARK, loc="left")
    ax_bar.tick_params(labelsize=8)
    for spine in ["top", "right"]:
        ax_bar.spines[spine].set_visible(False)

    # On-time delivery by carrier
    ax_otd = fig.add_axes([0.69, 0.42, 0.29, 0.32])
    otd_carrier = df.groupby("shipping_carriers")["on_time_delivery_flag"].mean().sort_values(ascending=False) * 100
    ax_otd.bar(otd_carrier.index, otd_carrier.values, color="#D83B01")
    ax_otd.set_title("On-Time Delivery % by Carrier", fontsize=10, color=TEXT_DARK, loc="left")
    ax_otd.tick_params(labelsize=8)
    ax_otd.set_ylim(0, 100)
    for spine in ["top", "right"]:
        ax_otd.spines[spine].set_visible(False)

    # Supplier defect rate table-ish bar
    ax_supp = fig.add_axes([0.03, 0.06, 0.45, 0.30])
    supplier_perf = df.groupby("supplier_name")["defect_rates"].mean().sort_values()
    ax_supp.barh(supplier_perf.index, supplier_perf.values, color="#6B69D6")
    ax_supp.set_title("Avg Defect Rate (%) by Supplier", fontsize=10, color=TEXT_DARK, loc="left")
    ax_supp.tick_params(labelsize=8)
    for spine in ["top", "right"]:
        ax_supp.spines[spine].set_visible(False)

    # Route bottleneck
    ax_route = fig.add_axes([0.53, 0.06, 0.45, 0.30])
    route_perf = df.groupby("routes")["lead_times"].mean().sort_values(ascending=False)
    ax_route.bar(route_perf.index, route_perf.values, color="#E66C37")
    ax_route.set_title("Avg Lead Time (days) by Route", fontsize=10, color=TEXT_DARK, loc="left")
    ax_route.tick_params(labelsize=8)
    for spine in ["top", "right"]:
        ax_route.spines[spine].set_visible(False)

    fig.savefig(OUT, dpi=150, facecolor=BG, bbox_inches="tight")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
