import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

def get_db_connection(db_type="sqlite", connection_details=None):
    """
    Establishes and returns a database engine / connection.
    Supports SQLite locally or MySQL via parameters.
    """
    if db_type == "mysql" and connection_details:
        # Expected details: user, password, host, port, database
        user = connection_details.get("user", "root")
        password = connection_details.get("password", "")
        host = connection_details.get("host", "localhost")
        port = connection_details.get("port", "3306")
        db_name = connection_details.get("database", "product_intelligence")
        
        conn_str = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"
        engine = create_engine(conn_str)
        return engine
    else:
        # Default SQLite
        db_path = connection_details.get("sqlite_path", "product_intelligence.db") if connection_details else "product_intelligence.db"
        engine = create_engine(f"sqlite:///{db_path}")
        return engine

def load_data(processed_dir="data/processed", db_type="sqlite", connection_details=None):
    """
    Loads processed dimension and fact files into target SQL database tables.
    """
    print(f"Loading data into database ({db_type})...")
    engine = get_db_connection(db_type, connection_details)
    
    # Read files
    df_cust = pd.read_csv(os.path.join(processed_dir, "dim_customers.csv"))
    df_prod = pd.read_csv(os.path.join(processed_dir, "dim_products.csv"))
    df_dates = pd.read_csv(os.path.join(processed_dir, "dim_dates.csv"))
    df_fact = pd.read_csv(os.path.join(processed_dir, "fact_sales.csv"))
    
    # Write to SQL (replace tables if they exist)
    df_cust.to_sql("dim_customers", con=engine, if_exists="replace", index=False)
    df_prod.to_sql("dim_products", con=engine, if_exists="replace", index=False)
    df_dates.to_sql("dim_dates", con=engine, if_exists="replace", index=False)
    df_fact.to_sql("fact_sales", con=engine, if_exists="replace", index=False)
    
    print("Database loading complete.")
    
    # Print record count verification
    with engine.connect() as conn:
        for table in ["dim_customers", "dim_products", "dim_dates", "fact_sales"]:
            res = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = res.scalar()
            print(f"Table '{table}': {count} records loaded.")

if __name__ == "__main__":
    # Standard SQLite test run
    load_data()
