-- ============================================================================
-- SQL Views for Business Reporting
-- Target Database System: MySQL / MariaDB
-- ============================================================================

USE product_intelligence;

-- 1. View: Active Subscriptions Summary
-- Shows the last subscription tier and status details for each customer
CREATE OR REPLACE VIEW v_active_subscriptions AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    c.segment,
    c.country,
    p.product_name,
    p.tier,
    f.billing_cycle,
    f.amount as last_paid_amount,
    f.date_key as last_payment_date
FROM dim_customers c
JOIN (
    -- Get only the latest payment transaction for each customer
    SELECT f1.customer_id, f1.product_id, f1.billing_cycle, f1.amount, f1.date_key
    FROM fact_sales f1
    INNER JOIN (
        SELECT customer_id, MAX(date_key) as max_date
        FROM fact_sales
        WHERE payment_status = 'Paid'
        GROUP BY customer_id
    ) f2 ON f1.customer_id = f2.customer_id AND f1.date_key = f2.max_date
    WHERE f1.payment_status = 'Paid'
) f ON c.customer_id = f.customer_id
JOIN dim_products p ON f.product_id = p.product_id;


-- 2. View: Monthly Sales and Revenue Aggregates
-- Sums paid sales by month, product, and customer segment
CREATE OR REPLACE VIEW v_monthly_revenue_summary AS
SELECT 
    d.year,
    d.month,
    d.month_name,
    c.segment,
    p.tier as product_tier,
    COUNT(DISTINCT f.customer_id) as active_paying_customers,
    SUM(f.amount) as total_collected_revenue,
    SUM(CASE WHEN f.billing_cycle = 'Annual' THEN f.amount / 12 ELSE f.amount END) as monthly_recurring_revenue_est
FROM fact_sales f
JOIN dim_dates d ON f.date_key = d.date_key
JOIN dim_customers c ON f.customer_id = c.customer_id
JOIN dim_products p ON f.product_id = p.product_id
WHERE f.payment_status = 'Paid'
GROUP BY d.year, d.month, d.month_name, c.segment, p.tier;


-- 3. View: Customer RFM Aggregate Core
-- Computes raw RFM metrics for direct reporting
CREATE OR REPLACE VIEW v_customer_rfm_metrics AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.segment,
    c.country,
    DATEDIFF((SELECT MAX(date_actual) FROM dim_dates), MAX(d.date_actual)) as recency_days,
    COUNT(f.transaction_id) as frequency_total,
    SUM(f.amount) as monetary_total
FROM dim_customers c
LEFT JOIN fact_sales f ON c.customer_id = f.customer_id AND f.payment_status = 'Paid'
LEFT JOIN dim_dates d ON f.date_key = d.date_key
GROUP BY c.customer_id, c.customer_name, c.segment, c.country;
