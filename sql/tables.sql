-- ============================================================================
-- SQL Star Schema Tables
-- Target Database System: MySQL / MariaDB
-- ============================================================================

USE product_intelligence;

-- 1. Dimension: Customers
CREATE TABLE IF NOT EXISTS dim_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    signup_date DATE NOT NULL,
    country VARCHAR(100),
    segment VARCHAR(50),
    cohort_month VARCHAR(7), -- e.g., '2023-01'
    INDEX idx_customer_segment (segment),
    INDEX idx_customer_country (country)
);

-- 2. Dimension: Products
CREATE TABLE IF NOT EXISTS dim_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    tier VARCHAR(50) NOT NULL,
    monthly_price DECIMAL(10, 2) NOT NULL,
    annual_price DECIMAL(10, 2) NOT NULL
);

-- 3. Dimension: Dates
CREATE TABLE IF NOT EXISTS dim_dates (
    date_key VARCHAR(10) PRIMARY KEY, -- YYYY-MM-DD
    date_actual DATE NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    month INT NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    day INT NOT NULL,
    day_of_week INT NOT NULL, -- 1 (Mon) to 7 (Sun)
    is_weekend TINYINT(1) DEFAULT 0,
    INDEX idx_date_year_month (year, month)
);

-- 4. Fact: Sales / Transactions
CREATE TABLE IF NOT EXISTS fact_sales (
    transaction_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    date_key VARCHAR(10) NOT NULL, -- FK to dim_dates
    amount DECIMAL(10, 2) NOT NULL,
    billing_cycle VARCHAR(20) NOT NULL, -- 'Monthly', 'Annual'
    payment_status VARCHAR(50) NOT NULL, -- 'Paid', 'Failed', 'Refunded'
    FOREIGN KEY (customer_id) REFERENCES dim_customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES dim_products(product_id),
    FOREIGN KEY (date_key) REFERENCES dim_dates(date_key),
    INDEX idx_fact_payment_status (payment_status),
    INDEX idx_fact_customer (customer_id),
    INDEX idx_fact_product (product_id)
);
