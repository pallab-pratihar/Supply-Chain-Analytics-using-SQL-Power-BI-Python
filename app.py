"""
app.py — Supply Chain Analytics Dashboard (Streamlit)

Live, interactive version of the KPI dashboard described in /powerbi.
Reads the same cleaned data produced by python/01_data_cleaning.py.

Run locally:
    streamlit run app.py

Deploy: see README.md > "Deploy the live dashboard (Streamlit)".
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# --------------------------------------------------------------------------
# Page config
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Supply Chain Analytics Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "processed" / "supply_chain_cleaned.csv"
RAW_PATH = Path(__file__).parent / "data" / "raw" / "supply_chain_data.csv"


# --------------------------------------------------------------------------
# Data loading + cleaning (cached so it only runs once per session)
# --------------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the pre-cleaned dataset if present, otherwise clean the raw file
    on the fly so the app works even on a fresh clone that hasn't run
    python/01_data_cleaning.py yet."""
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)

    df = pd.read_csv(RAW_PATH)
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    df.insert(0, "record_id", range(1, len(df) + 1))

    df["order_fill_rate"] = np.where(
        df["order_quantities"] > 0,
        (df["number_of_products_sold"] / df["order_quantities"]).clip(upper=1) * 100,
        np.nan,
    )
    df["inventory_turnover"] = np.where(
        df["stock_levels"] > 0, df["number_of_products_sold"] / df["stock_levels"], np.nan
    )
    median_by_mode = df.groupby("transportation_modes")["shipping_times"].transform("median")
    df["on_time_delivery_flag"] = (df["shipping_times"] <= median_by_mode).astype(int)
    denom = df["stock_levels"] + df["order_quantities"]
    df["warehouse_utilization_pct"] = np.where(denom > 0, (df["stock_levels"] / denom) * 100, np.nan)
    df["profit"] = df["revenue_generated"] - df["costs"]
    df["profit_margin_pct"] = np.where(
        df["revenue_generated"] > 0, (df["profit"] / df["revenue_generated"]) * 100, np.nan
    )
    df["total_shipping_cost"] = df["number_of_products_sold"] * df["shipping_costs"]
    df["quality_pass_flag"] = (df["inspection_results"].str.lower() == "pass").astype(int)
    return df


df_all = load_data()

# --------------------------------------------------------------------------
# Sidebar filters
# --------------------------------------------------------------------------
st.sidebar.title("📦 Supply Chain Analytics")
st.sidebar.caption("Filters apply to every chart on the page.")

product_types = sorted(df_all["product_type"].unique())
locations = sorted(df_all["location"].unique())
suppliers = sorted(df_all["supplier_name"].unique())
carriers = sorted(df_all["shipping_carriers"].unique())

sel_products = st.sidebar.multiselect("Product type", product_types, default=product_types)
sel_locations = st.sidebar.multiselect("Location", locations, default=locations)
sel_suppliers = st.sidebar.multiselect("Supplier", suppliers, default=suppliers)
sel_carriers = st.sidebar.multiselect("Shipping carrier", carriers, default=carriers)

df = df_all[
    df_all["product_type"].isin(sel_products)
    & df_all["location"].isin(sel_locations)
    & df_all["supplier_name"].isin(sel_suppliers)
    & df_all["shipping_carriers"].isin(sel_carriers)
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Showing **{len(df)}** of {len(df_all)} records")
st.sidebar.markdown(
    "[Source on GitHub](https://github.com/) · Built with Streamlit + Plotly"
)

if df.empty:
    st.warning("No records match the current filters. Adjust the filters in the sidebar.")
    st.stop()

# --------------------------------------------------------------------------
# Header + KPI cards
# --------------------------------------------------------------------------
st.title("Supply Chain Analytics Dashboard")
st.caption("Inventory, supplier performance, warehouse operations, and delivery efficiency")

ofr = df["order_fill_rate"].mean()
turnover = df["inventory_turnover"].mean()
otd = df["on_time_delivery_flag"].mean() * 100
wh_util = df["warehouse_utilization_pct"].mean()
total_revenue = df["revenue_generated"].sum()
total_profit = df["profit"].sum()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Revenue", f"${total_revenue:,.0f}")
k2.metric("Total Profit", f"${total_profit:,.0f}")
k3.metric("Order Fill Rate", f"{ofr:.1f}%")
k4.metric("Inventory Turnover", f"{turnover:.1f}x")
k5.metric("On-Time Delivery", f"{otd:.0f}%", delta=f"{otd-85:.0f} pts vs 85% target", delta_color="normal")
k6.metric("Warehouse Utilization", f"{wh_util:.0f}%")

st.markdown("---")

# --------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------
tab_overview, tab_inventory, tab_suppliers, tab_logistics, tab_root_cause, tab_data = st.tabs(
    [" Overview", " Inventory", " Suppliers & Quality", " Logistics", "Root Cause", "Raw Data"]
)

# ---------------- Overview ----------------
with tab_overview:
    c1, c2 = st.columns(2)
    with c1:
        rev = df.groupby("product_type")["revenue_generated"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(rev, x="product_type", y="revenue_generated", color="product_type",
                     title="Revenue by Product Type", labels={"revenue_generated": "Revenue ($)", "product_type": "Product Type"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        rev_loc = df.groupby("location")["revenue_generated"].sum().sort_values(ascending=False).reset_index()
        fig = px.pie(rev_loc, names="location", values="revenue_generated", hole=0.45,
                     title="Revenue Distribution by Location")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        profit = df.groupby("product_type")["profit"].sum().sort_values().reset_index()
        fig = px.bar(profit, x="profit", y="product_type", orientation="h", color="profit",
                     color_continuous_scale="RdYlGn", title="Profitability by Product Type",
                     labels={"profit": "Profit ($)", "product_type": ""})
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        price_cost = df.groupby("product_type").agg(
            Price=("price", "sum"), Manufacturing_Cost=("manufacturing_costs", "sum")
        ).reset_index().melt(id_vars="product_type", var_name="Metric", value_name="Value")
        fig = px.bar(price_cost, x="product_type", y="Value", color="Metric", barmode="group",
                     title="Price vs. Manufacturing Cost", labels={"product_type": "Product Type"})
        st.plotly_chart(fig, use_container_width=True)

# ---------------- Inventory ----------------
with tab_inventory:
    c1, c2 = st.columns(2)
    with c1:
        wh = df.groupby("location")["warehouse_utilization_pct"].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(wh, x="location", y="warehouse_utilization_pct", color="location",
                     title="Avg Warehouse Utilization by Location",
                     labels={"warehouse_utilization_pct": "Utilization (%)", "location": "Location"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        turn = df.groupby("product_type")["inventory_turnover"].mean().sort_values(ascending=False).reset_index()
        fig = px.bar(turn, x="product_type", y="inventory_turnover", color="product_type",
                     title="Avg Inventory Turnover by Product Type",
                     labels={"inventory_turnover": "Turnover (x)", "product_type": "Product Type"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Stockout risk: lowest Order Fill Rate SKUs")
    bottlenecks = df.nsmallest(10, "order_fill_rate")[
        ["sku", "product_type", "order_quantities", "number_of_products_sold", "order_fill_rate"]
    ].round(1)
    st.dataframe(bottlenecks, use_container_width=True, hide_index=True)

    fig = px.scatter(df, x="stock_levels", y="order_quantities", color="product_type", size="revenue_generated",
                      hover_name="sku", title="Stock Levels vs. Order Quantities",
                      labels={"stock_levels": "Stock Levels", "order_quantities": "Order Quantities"})
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Suppliers & Quality ----------------
with tab_suppliers:
    c1, c2 = st.columns(2)
    with c1:
        supplier_perf = df.groupby("supplier_name").agg(
            avg_defect_rate=("defect_rates", "mean"), avg_lead_time=("lead_times", "mean")
        ).reset_index()
        fig = px.scatter(supplier_perf, x="avg_lead_time", y="avg_defect_rate", color="supplier_name",
                          size=[20] * len(supplier_perf), title="Supplier Performance: Lead Time vs. Defect Rate",
                          labels={"avg_lead_time": "Avg Lead Time (days)", "avg_defect_rate": "Avg Defect Rate (%)"})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        pass_rate = df.groupby("supplier_name")["quality_pass_flag"].mean().mul(100).sort_values().reset_index()
        fig = px.bar(pass_rate, x="quality_pass_flag", y="supplier_name", orientation="h", color="supplier_name",
                     title="Inspection Pass Rate by Supplier",
                     labels={"quality_pass_flag": "Pass Rate (%)", "supplier_name": ""})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    fig = px.box(df, x="inspection_results", y="defect_rates", color="inspection_results",
                 title="Defect Rate Distribution by Inspection Result",
                 labels={"inspection_results": "Inspection Result", "defect_rates": "Defect Rate (%)"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Logistics ----------------
with tab_logistics:
    c1, c2 = st.columns(2)
    with c1:
        mode_counts = df["transportation_modes"].value_counts().reset_index()
        mode_counts.columns = ["transportation_modes", "count"]
        fig = px.bar(mode_counts, x="transportation_modes", y="count", color="transportation_modes",
                     title="Shipment Count by Transportation Mode",
                     labels={"transportation_modes": "Mode", "count": "Shipments"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        otd_carrier = df.groupby("shipping_carriers")["on_time_delivery_flag"].mean().mul(100).sort_values(ascending=False).reset_index()
        fig = px.bar(otd_carrier, x="shipping_carriers", y="on_time_delivery_flag", color="shipping_carriers",
                     title="On-Time Delivery % by Carrier",
                     labels={"shipping_carriers": "Carrier", "on_time_delivery_flag": "On-Time %"})
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    route_perf = df.groupby("routes").agg(
        avg_lead_time=("lead_times", "mean"), avg_cost=("costs", "mean"), avg_defect_rate=("defect_rates", "mean")
    ).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=route_perf["routes"], y=route_perf["avg_lead_time"], name="Avg Lead Time (days)"))
    fig.add_trace(go.Bar(x=route_perf["routes"], y=route_perf["avg_cost"], name="Avg Cost ($)"))
    fig.update_layout(barmode="group", title="Route-Level Lead Time & Cost")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- Root Cause ----------------
with tab_root_cause:
    st.subheader("Manufacturing lead time vs. defect rate")
    bins = [0, 10, 20, max(df["manufacturing_lead_time"].max() + 1, 21)]
    labels = ["0-10 days", "11-20 days", "21+ days"]
    df_rc = df.copy()
    df_rc["lead_time_bucket"] = pd.cut(df_rc["manufacturing_lead_time"], bins=bins, labels=labels)
    lt_defect = df_rc.groupby("lead_time_bucket", observed=True)["defect_rates"].mean().reset_index()
    fig = px.bar(lt_defect, x="lead_time_bucket", y="defect_rates", color="lead_time_bucket",
                 title="Avg Defect Rate by Manufacturing Lead-Time Bucket",
                 labels={"lead_time_bucket": "Manufacturing Lead Time", "defect_rates": "Avg Defect Rate (%)"})
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Route-level bottlenecks")
    route_tbl = df.groupby("routes").agg(
        avg_lead_time=("lead_times", "mean"), avg_cost=("costs", "mean"), avg_defect_rate=("defect_rates", "mean")
    ).round(2).sort_values("avg_lead_time", ascending=False)
    st.dataframe(route_tbl, use_container_width=True)

    st.info(
        "Full narrative findings and recommendations are in `reports/insights_and_recommendations.md` "
        "in the repository."
    )

# ---------------- Raw Data ----------------
with tab_data:
    st.subheader("Filtered dataset")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button(
        "Download filtered data as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="supply_chain_filtered.csv",
        mime="text/csv",
    )

st.markdown("---")
st.caption("Data: sample supply chain dataset · Dashboard built with Streamlit + Plotly")
