import os
import pandas as pd
import numpy as np

def transform_data(raw_dir="data/raw", processed_dir="data/processed"):
    """
    Transforms raw CSV data into styled Star Schema Dimension and Fact tables.
    Also generates a complete date dimension.
    """
    print("Starting data transformation...")
    os.makedirs(processed_dir, exist_ok=True)
    
    # Load raw data
    df_cust = pd.read_csv(os.path.join(raw_dir, "customers.csv"))
    df_prod = pd.read_csv(os.path.join(raw_dir, "products.csv"))
    df_trans = pd.read_csv(os.path.join(raw_dir, "transactions.csv"))
    
    # Convert dates to datetime objects
    df_cust["signup_date"] = pd.to_datetime(df_cust["signup_date"])
    df_trans["transaction_date"] = pd.to_datetime(df_trans["transaction_date"])
    
    # ------------------
    # 1. Transform dim_customers
    # ------------------
    # Add cohort month (e.g., '2023-01')
    df_cust["cohort_month"] = df_cust["signup_date"].dt.strftime("%Y-%m")
    
    # ------------------
    # 2. Transform dim_products
    # ------------------
    # Products remain relatively static but let's ensure standard format
    
    # ------------------
    # 3. Create dim_dates
    # ------------------
    min_date = min(df_cust["signup_date"].min(), df_trans["transaction_date"].min())
    max_date = max(df_cust["signup_date"].max(), df_trans["transaction_date"].max())
    
    date_range = pd.date_range(start=min_date - pd.Timedelta(days=30), end=max_date + pd.Timedelta(days=30))
    df_dates = pd.DataFrame({"date_key": date_range})
    
    df_dates["date_actual"] = df_dates["date_key"].dt.strftime("%Y-%m-%d")
    df_dates["year"] = df_dates["date_key"].dt.year
    df_dates["quarter"] = df_dates["date_key"].dt.quarter
    df_dates["month"] = df_dates["date_key"].dt.month
    df_dates["month_name"] = df_dates["date_key"].dt.strftime("%B")
    df_dates["day"] = df_dates["date_key"].dt.day
    df_dates["day_of_week"] = df_dates["date_key"].dt.dayofweek + 1 # 1 = Monday, 7 = Sunday
    df_dates["is_weekend"] = df_dates["date_key"].dt.dayofweek.isin([5, 6]).astype(int)
    
    # Convert date_key to string for joining
    df_dates["date_key"] = df_dates["date_key"].dt.strftime("%Y-%m-%d")
    
    # ------------------
    # 4. Transform fact_sales
    # ------------------
    df_fact = df_trans.copy()
    df_fact["date_key"] = df_fact["transaction_date"].dt.strftime("%Y-%m-%d")
    df_fact.drop(columns=["transaction_date"], inplace=True)
    
    # Format and clean types
    df_cust["signup_date"] = df_cust["signup_date"].dt.strftime("%Y-%m-%d")
    
    # Save processed dimensions and facts
    df_cust.to_csv(os.path.join(processed_dir, "dim_customers.csv"), index=False)
    df_prod.to_csv(os.path.join(processed_dir, "dim_products.csv"), index=False)
    df_dates.to_csv(os.path.join(processed_dir, "dim_dates.csv"), index=False)
    df_fact.to_csv(os.path.join(processed_dir, "fact_sales.csv"), index=False)
    
    print("Data transformation completed successfully.")
    print(f"dim_customers shape: {df_cust.shape}")
    print(f"dim_products shape: {df_prod.shape}")
    print(f"dim_dates shape: {df_dates.shape}")
    print(f"fact_sales shape: {df_fact.shape}")

if __name__ == "__main__":
    transform_data()
