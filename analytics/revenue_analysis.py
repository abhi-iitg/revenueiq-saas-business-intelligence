import os
import pandas as pd
import numpy as np

def calculate_revenue_kpis(processed_dir="data/processed"):
    """
    Calculates monthly SaaS KPIs: Monthly Recurring Revenue (MRR), 
    Annual Recurring Revenue (ARR), Average Revenue Per User (ARPU),
    and Month-over-Month Revenue Growth Rate.
    Uses amortization to spread Annual contract value over 12 months.
    """
    print("Analyzing revenue metrics (MRR, ARR, ARPU, Growth)...")
    
    # Load data
    df_fact = pd.read_csv(os.path.join(processed_dir, "fact_sales.csv"))
    
    # Ensure paid status
    df_paid = df_fact[df_fact["payment_status"] == "Paid"].copy()
    df_paid["date_key"] = pd.to_datetime(df_paid["date_key"])
    
    # Generate list of all months in dataset range
    min_date = df_paid["date_key"].min()
    max_date = df_paid["date_key"].max()
    all_months = pd.date_range(start=min_date, end=max_date, freq="MS").strftime("%Y-%m").tolist()
    
    # We will build a dictionary to store MRR contributions and customer counts per month
    # Structure: { '2023-01': { 'mrr': 0.0, 'active_users': set() } }
    monthly_data = {m: {"mrr": 0.0, "active_users": set()} for m in all_months}
    
    # Iterate through each transaction and distribute its value
    for idx, row in df_paid.iterrows():
        tx_date = row["date_key"]
        cycle = row["billing_cycle"]
        amount = row["amount"]
        cust_id = row["customer_id"]
        
        # Determine active period for this payment
        if cycle == "Monthly":
            # Contributes to the transaction month
            month_str = tx_date.strftime("%Y-%m")
            if month_str in monthly_data:
                monthly_data[month_str]["mrr"] += amount
                monthly_data[month_str]["active_users"].add(cust_id)
        else: # Annual
            # Contributes amount / 12 to the transaction month and the next 11 months
            monthly_contrib = amount / 12.0
            for i in range(12):
                future_date = tx_date + pd.DateOffset(months=i)
                month_str = future_date.strftime("%Y-%m")
                if month_str in monthly_data:
                    monthly_data[month_str]["mrr"] += monthly_contrib
                    monthly_data[month_str]["active_users"].add(cust_id)
                    
    # Compile metrics
    records = []
    prev_mrr = None
    
    for month in sorted(all_months):
        mrr = round(monthly_data[month]["mrr"], 2)
        active_count = len(monthly_data[month]["active_users"])
        arr = round(mrr * 12, 2)
        arpu = round(mrr / active_count, 2) if active_count > 0 else 0.0
        
        # Calculate Growth Rate
        if prev_mrr is None or prev_mrr == 0:
            growth_rate = 0.0
        else:
            growth_rate = round((mrr - prev_mrr) / prev_mrr, 4)
            
        records.append({
            "month": month,
            "mrr": mrr,
            "arr": arr,
            "active_users": active_count,
            "arpu": arpu,
            "mrr_growth_rate": growth_rate
        })
        prev_mrr = mrr
        
    df_revenue_kpis = pd.DataFrame(records)
    
    # Save processed KPIs
    df_revenue_kpis.to_csv(os.path.join(processed_dir, "monthly_revenue_kpis.csv"), index=False)
    print("Revenue KPIs calculated successfully. Saved monthly_revenue_kpis.csv.")
    print(df_revenue_kpis.tail(6))
    
    return df_revenue_kpis

if __name__ == "__main__":
    calculate_revenue_kpis()
