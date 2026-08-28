import os
import pandas as pd
import numpy as np

def calculate_clv(processed_dir="data/processed"):
    """
    Calculates Customer Lifetime Value (CLV) based on historical transaction value,
    and implements a SaaS CLV forecasting model based on segment-level ARPU and churn.
    """
    print("Calculating Customer Lifetime Value (CLV)...")
    
    # Load processed datasets
    df_cust = pd.read_csv(os.path.join(processed_dir, "dim_customers.csv"))
    df_fact = pd.read_csv(os.path.join(processed_dir, "fact_sales.csv"))
    df_churn = pd.read_csv(os.path.join(processed_dir, "customer_churn.csv"))
    
    # 1. Historical CLV (sum of paid transactions per customer)
    df_paid = df_fact[df_fact["payment_status"] == "Paid"].copy()
    hist_clv = df_paid.groupby("customer_id")["amount"].sum().reset_index()
    hist_clv.rename(columns={"amount": "historical_clv"}, inplace=True)
    
    # Merge with customers and churn status
    df_clv = pd.merge(df_churn, hist_clv, on="customer_id", how="left")
    df_clv["historical_clv"] = df_clv["historical_clv"].fillna(0.0)
    
    # 2. Predictive/SaaS CLV Model
    # CLV = (ARPU * Gross Margin) / Monthly Churn Rate
    # Let's assume a standard SaaS Gross Margin of 85% (0.85)
    gross_margin = 0.85
    
    # Calculate ARPU and Churn Rate per Segment to compute Segment-Level Predicted CLV
    # We'll calculate monthly equivalent revenue first
    df_paid["date_key"] = pd.to_datetime(df_paid["date_key"])
    df_paid["month_key"] = df_paid["date_key"].dt.strftime("%Y-%m")
    
    # Monthly revenue per customer
    # If transaction is Annual, monthly value is amount / 12
    df_paid["monthly_equiv_revenue"] = df_paid.apply(
        lambda r: r["amount"] / 12 if r["billing_cycle"] == "Annual" else r["amount"], axis=1
    )
    
    # Segment metrics
    segment_metrics = []
    for segment in ["SMB", "Mid-Market", "Enterprise"]:
        segment_custs = df_clv[df_clv["segment"] == segment]
        total_custs = len(segment_custs)
        
        # Segment Churn
        churned_custs = segment_custs["is_churned"].sum()
        churn_rate = churned_custs / total_custs if total_custs > 0 else 0.05
        
        # Standardize churn rate to monthly (approx: annual churn / 12)
        # In our simulation, churn happens per payment cycle.
        # Let's calculate the customer tenure in months
        df_paid_seg = df_paid[df_paid["customer_id"].isin(segment_custs["customer_id"])]
        
        # Monthly ARPU = Total Monthly Equiv Revenue / Total Unique Active Months of Customers
        active_months = df_paid_seg.groupby(["customer_id", "month_key"]).size().reset_index()
        total_customer_months = len(active_months)
        
        total_mrr = df_paid_seg["monthly_equiv_revenue"].sum()
        arpu = total_mrr / total_customer_months if total_customer_months > 0 else 50.0
        
        # Handle division by zero for Churn Rate
        # Convert annual churn to approximate monthly churn if it was annual bias
        monthly_churn_rate = max(churn_rate / 12, 0.01) # min 1% monthly churn for calculation stability
        
        predicted_clv = (arpu * gross_margin) / monthly_churn_rate
        
        segment_metrics.append({
            "segment": segment,
            "arpu": round(arpu, 2),
            "churn_rate": round(churn_rate, 4),
            "monthly_churn_rate": round(monthly_churn_rate, 4),
            "predicted_clv": round(predicted_clv, 2)
        })
        
    df_seg_metrics = pd.DataFrame(segment_metrics)
    print("\nSegment CLV Metrics:")
    print(df_seg_metrics)
    
    # Map segment-level predicted CLV back to individual customers
    df_clv = pd.merge(df_clv, df_seg_metrics[["segment", "predicted_clv"]], on="segment", how="left")
    
    # Save results
    df_clv.to_csv(os.path.join(processed_dir, "customer_clv.csv"), index=False)
    df_seg_metrics.to_csv(os.path.join(processed_dir, "segment_clv_metrics.csv"), index=False)
    
    print("CLV calculation finished. Saved customer_clv.csv.")
    return df_clv, df_seg_metrics

if __name__ == "__main__":
    calculate_clv()
