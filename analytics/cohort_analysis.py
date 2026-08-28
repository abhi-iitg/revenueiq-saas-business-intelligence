import os
import pandas as pd
import numpy as np

def calculate_cohort_retention(processed_dir="data/processed"):
    """
    Computes a monthly cohort retention matrix.
    Rows represent the cohort (signup month) and columns represent
    the months active since signup (Month 0, Month 1, etc.).
    """
    print("Calculating Cohort Retention Matrix...")
    
    # Load data
    df_cust = pd.read_csv(os.path.join(processed_dir, "dim_customers.csv"))
    df_fact = pd.read_csv(os.path.join(processed_dir, "fact_sales.csv"))
    
    df_cust["signup_date"] = pd.to_datetime(df_cust["signup_date"])
    df_fact["date_key"] = pd.to_datetime(df_fact["date_key"])
    
    # Only count Paid transactions as active engagement
    df_paid = df_fact[df_fact["payment_status"] == "Paid"].copy()
    
    # Map customer signup date to transaction dates
    df_merged = pd.merge(df_paid, df_cust[["customer_id", "signup_date", "cohort_month"]], on="customer_id", how="inner")
    
    # Define active month of transaction
    df_merged["transaction_month"] = df_merged["date_key"].dt.to_period("M")
    df_merged["cohort_period"] = pd.to_datetime(df_merged["cohort_month"]).dt.to_period("M")
    
    # Calculate difference in months
    df_merged["cohort_index"] = (df_merged["transaction_month"] - df_merged["cohort_period"]).apply(lambda x: x.n)
    
    # Filter out index < 0 (should not exist but just in case)
    df_merged = df_merged[df_merged["cohort_index"] >= 0]
    
    # Group by CohortMonth and CohortIndex, count unique active customers
    cohort_group = df_merged.groupby(["cohort_month", "cohort_index"])["customer_id"].nunique().reset_index()
    
    # Pivot the table to create a retention matrix
    cohort_matrix = cohort_group.pivot(index="cohort_month", columns="cohort_index", values="customer_id")
    
    # Get cohort size (number of customers who signed up in that month)
    # Using cohort size as the base (Month 0)
    cohort_sizes = df_cust.groupby("cohort_month")["customer_id"].nunique()
    
    # Fill Month 0 in matrix with cohort size since some users might sign up but not have transaction immediately,
    # though in our generation signup date = first transaction date.
    # To keep it exact, we align the cohort size:
    cohort_matrix[0] = cohort_matrix[0].fillna(cohort_sizes)
    
    # Divide each column by cohort size to get percentage retention
    retention_matrix = cohort_matrix.divide(cohort_sizes, axis=0)
    
    # Save both absolute cohort matrix and retention percentage matrix
    cohort_matrix.to_csv(os.path.join(processed_dir, "cohort_counts.csv"))
    retention_matrix.to_csv(os.path.join(processed_dir, "cohort_retention.csv"))
    
    print("Cohort analysis completed. Saved cohort_retention.csv.")
    return retention_matrix

if __name__ == "__main__":
    calculate_cohort_retention()
