import os
import pandas as pd
import numpy as np

def analyze_churn(processed_dir="data/processed"):
    """
    Analyzes customer churn, calculating overall churn rates and factors
    such as segment, billing cycle, country, and subscription tier.
    """
    print("Performing Churn Analysis...")
    
    # Load processed data
    df_cust = pd.read_csv(os.path.join(processed_dir, "dim_customers.csv"))
    df_fact = pd.read_csv(os.path.join(processed_dir, "fact_sales.csv"))
    
    # Get last transaction details per customer
    df_paid = df_fact[df_fact["payment_status"] == "Paid"].copy()
    df_paid["date_key"] = pd.to_datetime(df_paid["date_key"])
    
    last_trans = df_paid.groupby("customer_id").agg(
        last_date=("date_key", "max"),
        billing_cycle=("billing_cycle", "last"),
        product_id=("product_id", "last")
    ).reset_index()
    
    max_date = df_paid["date_key"].max()
    
    # Classify Churn:
    # If customer is on Monthly cycle and last payment is older than 45 days -> Churned
    # If customer is on Annual cycle and last payment is older than 395 days -> Churned
    # (Otherwise they are active)
    
    def evaluate_churn(row):
        days_since_last = (max_date - row["last_date"]).days
        if row["billing_cycle"] == "Monthly":
            return 1 if days_since_last > 45 else 0
        else: # Annual
            return 1 if days_since_last > 395 else 0
            
    last_trans["is_churned"] = last_trans.apply(evaluate_churn, axis=1)
    
    # Merge back to customers list
    df_churn = pd.merge(df_cust, last_trans[["customer_id", "is_churned", "last_date", "billing_cycle", "product_id"]], on="customer_id", how="left")
    
    # Customers with no paid transactions at all are churned (or never active)
    df_churn["is_churned"] = df_churn["is_churned"].fillna(1).astype(int)
    
    # Save churn dataframe
    df_churn.to_csv(os.path.join(processed_dir, "customer_churn.csv"), index=False)
    
    # Calculate churn rates by dimensions
    overall_churn = df_churn["is_churned"].mean()
    
    churn_by_segment = df_churn.groupby("segment")["is_churned"].mean().reset_index()
    churn_by_billing = df_churn.groupby("billing_cycle")["is_churned"].mean().reset_index()
    churn_by_country = df_churn.groupby("country")["is_churned"].mean().reset_index()
    
    print(f"Overall Churn Rate: {overall_churn * 100:.2f}%")
    print("\nChurn Rate by Segment:")
    print(churn_by_segment)
    print("\nChurn Rate by Billing Cycle:")
    print(churn_by_billing)
    
    # Save a summary dictionary/json or return dataframes
    return {
        "overall_churn": overall_churn,
        "churn_by_segment": churn_by_segment,
        "churn_by_billing": churn_by_billing,
        "churn_by_country": churn_by_country,
        "detailed_churn": df_churn
    }

if __name__ == "__main__":
    analyze_churn()
