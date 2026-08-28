import os
import sys
import argparse
from extract import generate_synthetic_data, save_raw_data
from transform import transform_data
from load import load_data

# Add parent directory to path so we can import from analytics
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from analytics.customer_segmentation import calculate_rfm_segments
from analytics.churn_analysis import analyze_churn
from analytics.clv_analysis import calculate_clv
from analytics.cohort_analysis import calculate_cohort_retention
from analytics.revenue_analysis import calculate_revenue_kpis

def run_pipeline(num_customers=10000, num_transactions=120000, db_type="sqlite", db_details=None):
    """
    Main ETL Orchestrator function. Runs extract, transform, and load steps sequentially.
    Then executes the downstream analytics calculations.
    """
    print("=" * 60)
    print("STARTING RevenueIQ Analytics Platform ETL PIPELINE")
    print("=" * 60)
    
    # 1. Extraction (Generation)
    print("\n[STEP 1/4] Extracting (Generating) Synthetic Data...")
    df_cust, df_prod, df_trans = generate_synthetic_data(
        num_customers=num_customers, 
        num_transactions=num_transactions
    )
    save_raw_data(df_cust, df_prod, df_trans)
    
    # 2. Transformation
    print("\n[STEP 2/4] Transforming Data to Star Schema...")
    transform_data()
    
    # 3. Loading
    print("\n[STEP 3/4] Loading Dimensional Models to Target Database...")
    load_data(db_type=db_type, connection_details=db_details)
    
    # 4. Analytics Calculations
    print("\n[STEP 4/4] Running Downstream Business Analytics Calculations...")
    calculate_rfm_segments()
    analyze_churn()
    calculate_clv()
    calculate_cohort_retention()
    calculate_revenue_kpis()
    
    print("\n" + "=" * 60)
    print("ETL & ANALYTICS PIPELINE EXECUTED SUCCESSFULLY")
    print("=" * 60)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Orchestration for Product Intelligence Platform")
    parser.add_argument("--customers", type=int, default=10000, help="Number of customers to generate")
    parser.add_argument("--transactions", type=int, default=120000, help="Target number of transactions")
    parser.add_argument("--db-type", type=str, choices=["sqlite", "mysql"], default="sqlite", help="Target database type")
    
    args = parser.parse_args()
    
    run_pipeline(
        num_customers=args.customers,
        num_transactions=args.transactions,
        db_type=args.db_type
    )
