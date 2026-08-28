import os
import pandas as pd
import numpy as np

def calculate_rfm_segments(processed_dir="data/processed"):
    """
    Computes RFM (Recency, Frequency, Monetary) segments for customers.
    """
    print("Calculating RFM Customer Segments...")
    
    # Load processed data
    df_cust = pd.read_csv(os.path.join(processed_dir, "dim_customers.csv"))
    df_fact = pd.read_csv(os.path.join(processed_dir, "fact_sales.csv"))
    
    # Filter paid transactions
    df_paid = df_fact[df_fact["payment_status"] == "Paid"].copy()
    df_paid["date_key"] = pd.to_datetime(df_paid["date_key"])
    
    # Reference date for Recency calculation (day after last transaction in dataset)
    ref_date = df_paid["date_key"].max() + pd.Timedelta(days=1)
    
    # Aggregate transaction metrics per customer
    rfm = df_paid.groupby("customer_id").agg({
        "date_key": lambda x: (ref_date - x.max()).days, # Recency
        "transaction_id": "count",                      # Frequency
        "amount": "sum"                                 # Monetary
    }).reset_index()
    
    rfm.rename(columns={
        "date_key": "recency",
        "transaction_id": "frequency",
        "amount": "monetary"
    }, inplace=True)
    
    # Handle users with no paid transactions (if any)
    missing_custs = df_cust[~df_cust["customer_id"].isin(rfm["customer_id"])].copy()
    if not missing_custs.empty:
        missing_rfm = pd.DataFrame({
            "customer_id": missing_custs["customer_id"],
            "recency": (ref_date - pd.to_datetime(missing_custs["signup_date"])).dt.days,
            "frequency": 0,
            "monetary": 0.0
        })
        rfm = pd.concat([rfm, missing_rfm], ignore_index=True)
        
    # Quantiles for scoring (1-5, where 5 is best/most desirable)
    # Recency: lower is better (more recent) -> label 5 for lowest recency
    # Frequency, Monetary: higher is better -> label 5 for highest
    
    # Use qcut, handling potential duplicate bin edges by using rank or drop duplicates
    try:
        rfm["R_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])
    except ValueError:
        # Fallback to rank if qcut fails due to low variance
        rfm["R_score"] = pd.qcut(rfm["recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1])
        
    try:
        rfm["F_score"] = pd.qcut(rfm["frequency"], 5, labels=[1, 2, 3, 4, 5])
    except ValueError:
        rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
        
    try:
        rfm["M_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])
    except ValueError:
        rfm["M_score"] = pd.qcut(rfm["monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
        
    # Combine scores
    rfm["R_score"] = rfm["R_score"].astype(int)
    rfm["F_score"] = rfm["F_score"].astype(int)
    rfm["M_score"] = rfm["M_score"].astype(int)
    
    # Segment definition logic
    # Segment maps based on R and F score combinations
    def rfm_segment_label(row):
        r, f, m = row["R_score"], row["F_score"], row["M_score"]
        
        if r >= 4 and f >= 4:
            return "Champions"
        elif r >= 3 and f >= 3:
            return "Loyal Customers"
        elif r >= 4 and f < 2:
            return "New Customers"
        elif r == 3 and f < 3:
            return "Potential Loyalists"
        elif r == 2 and f >= 4:
            return "At Risk"
        elif r == 2 and f < 4:
            return "About to Sleep"
        elif r == 1 and f >= 4:
            return "Can't Lose Them"
        elif r == 1 and f < 2:
            return "Lost"
        else:
            return "Hibernating"
            
    rfm["rfm_segment"] = rfm.apply(rfm_segment_label, axis=1)
    
    # Save segmentation back to processed data folder
    rfm.to_csv(os.path.join(processed_dir, "customer_rfm.csv"), index=False)
    print("RFM Customer Segmentation complete. Saved customer_rfm.csv.")
    
    # Return summary
    summary = rfm["rfm_segment"].value_counts().reset_index()
    summary.columns = ["Segment", "Count"]
    print(summary)
    return rfm

if __name__ == "__main__":
    calculate_rfm_segments()
