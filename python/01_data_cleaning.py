"""
01_data_cleaning.py
--------------------
Loads the raw supply chain dataset, standardizes column names, engineers
KPI-ready fields, validates data quality, and writes:
  1. A cleaned flat file  -> data/processed/supply_chain_cleaned.csv
  2. A star-schema model  -> data/processed/dim_*.csv and fact_supply_chain.csv
     (this is the layout Power BI / SQL both read from)

Run from the repo root:
    python python/01_data_cleaning.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

RAW_PATH = Path("data/raw/supply_chain_data.csv")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def load_raw(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # normalize column names: strip, lower, snake_case
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    return df


def engineer_fields(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Unique surrogate key
    df.insert(0, "record_id", range(1, len(df) + 1))

    # --- KPI building blocks -------------------------------------------------
    # Order Fill Rate proxy = products sold / order quantities (capped at 100%)
    df["order_fill_rate"] = np.where(
        df["order_quantities"] > 0,
        (df["number_of_products_sold"] / df["order_quantities"]).clip(upper=1) * 100,
        np.nan,
    )

    # Inventory Turnover proxy = products sold / stock levels
    df["inventory_turnover"] = np.where(
        df["stock_levels"] > 0,
        df["number_of_products_sold"] / df["stock_levels"],
        np.nan,
    )

    # On-time delivery flag: shipping time <= median shipping time for its mode
    median_by_mode = df.groupby("transportation_modes")["shipping_times"].transform("median")
    df["on_time_delivery_flag"] = (df["shipping_times"] <= median_by_mode).astype(int)

    # Warehouse Utilization proxy = stock levels / (stock levels + order quantities)
    denom = df["stock_levels"] + df["order_quantities"]
    df["warehouse_utilization_pct"] = np.where(
        denom > 0, (df["stock_levels"] / denom) * 100, np.nan
    )

    # Profitability
    df["profit"] = df["revenue_generated"] - df["costs"]
    df["profit_margin_pct"] = np.where(
        df["revenue_generated"] > 0, (df["profit"] / df["revenue_generated"]) * 100, np.nan
    )

    # Total shipping cost line
    df["total_shipping_cost"] = df["number_of_products_sold"] * df["shipping_costs"]

    # Defect flag
    df["is_defective_batch"] = (df["defect_rates"] > df["defect_rates"].median()).astype(int)

    # Quality pass flag
    df["quality_pass_flag"] = (df["inspection_results"].str.lower() == "pass").astype(int)

    return df


def data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    report = pd.DataFrame(
        {
            "column": df.columns,
            "dtype": df.dtypes.astype(str).values,
            "null_count": df.isnull().sum().values,
            "null_pct": (df.isnull().mean() * 100).round(2).values,
            "n_unique": df.nunique().values,
        }
    )
    return report


def build_star_schema(df: pd.DataFrame):
    # dim_product
    dim_product = (
        df[["sku", "product_type", "price"]]
        .drop_duplicates(subset="sku")
        .reset_index(drop=True)
    )
    dim_product.insert(0, "product_key", range(1, len(dim_product) + 1))

    # dim_supplier
    dim_supplier = (
        df[["supplier_name", "location"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_supplier.insert(0, "supplier_key", range(1, len(dim_supplier) + 1))

    # dim_shipping
    dim_shipping = (
        df[["shipping_carriers", "transportation_modes", "routes"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    dim_shipping.insert(0, "shipping_key", range(1, len(dim_shipping) + 1))

    # dim_location
    dim_location = (
        df[["location"]].drop_duplicates().reset_index(drop=True)
    )
    dim_location.insert(0, "location_key", range(1, len(dim_location) + 1))

    # fact table: join back the surrogate keys
    fact = df.merge(dim_product[["product_key", "sku"]], on="sku", how="left")
    fact = fact.merge(
        dim_supplier[["supplier_key", "supplier_name", "location"]],
        on=["supplier_name", "location"],
        how="left",
    )
    fact = fact.merge(
        dim_shipping[["shipping_key", "shipping_carriers", "transportation_modes", "routes"]],
        on=["shipping_carriers", "transportation_modes", "routes"],
        how="left",
    )
    fact = fact.merge(dim_location, on="location", how="left")

    fact_cols = [
        "record_id",
        "product_key",
        "supplier_key",
        "shipping_key",
        "location_key",
        "availability",
        "number_of_products_sold",
        "revenue_generated",
        "customer_demographics",
        "stock_levels",
        "lead_times",
        "order_quantities",
        "shipping_times",
        "shipping_costs",
        "production_volumes",
        "manufacturing_lead_time",
        "manufacturing_costs",
        "inspection_results",
        "defect_rates",
        "costs",
        "order_fill_rate",
        "inventory_turnover",
        "on_time_delivery_flag",
        "warehouse_utilization_pct",
        "profit",
        "profit_margin_pct",
        "total_shipping_cost",
        "is_defective_batch",
        "quality_pass_flag",
    ]
    fact_supply_chain = fact[fact_cols]

    return dim_product, dim_supplier, dim_shipping, dim_location, fact_supply_chain


def main():
    print(f"Loading raw data from {RAW_PATH} ...")
    df = load_raw(RAW_PATH)
    print(f"Raw shape: {df.shape}")

    dq = data_quality_report(df)
    dq.to_csv(OUT_DIR / "data_quality_report.csv", index=False)
    print("Saved data quality report -> data/processed/data_quality_report.csv")

    dup_count = df.duplicated().sum()
    print(f"Duplicate rows: {dup_count}")

    df = engineer_fields(df)
    df.to_csv(OUT_DIR / "supply_chain_cleaned.csv", index=False)
    print(f"Saved cleaned flat file -> {OUT_DIR / 'supply_chain_cleaned.csv'} ({df.shape})")

    dim_product, dim_supplier, dim_shipping, dim_location, fact = build_star_schema(df)
    dim_product.to_csv(OUT_DIR / "dim_product.csv", index=False)
    dim_supplier.to_csv(OUT_DIR / "dim_supplier.csv", index=False)
    dim_shipping.to_csv(OUT_DIR / "dim_shipping.csv", index=False)
    dim_location.to_csv(OUT_DIR / "dim_location.csv", index=False)
    fact.to_csv(OUT_DIR / "fact_supply_chain.csv", index=False)

    print("Saved star schema:")
    print(f"  dim_product.csv      ({dim_product.shape})")
    print(f"  dim_supplier.csv     ({dim_supplier.shape})")
    print(f"  dim_shipping.csv     ({dim_shipping.shape})")
    print(f"  dim_location.csv     ({dim_location.shape})")
    print(f"  fact_supply_chain.csv ({fact.shape})")
    print("\nDone. This star schema is what the SQL scripts and the Power BI model use.")


if __name__ == "__main__":
    main()
