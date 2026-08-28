-- ============================================================================
-- SQL KPI Queries
-- Calculations for MRR, ARR, Churn, Retention, ARPU, and Growth Rate
-- Target Database System: MySQL / MariaDB
-- ============================================================================

USE product_intelligence;

-- 1. Monthly Recurring Revenue (MRR) & Annual Recurring Revenue (ARR)
-- Spreads Annual subscriptions over 12 months for proper accounting
SELECT 
    d.year,
    d.month,
    ROUND(SUM(CASE 
        WHEN f.billing_cycle = 'Annual' THEN f.amount / 12.0 
        ELSE f.amount 
    END), 2) as MRR,
    ROUND(SUM(CASE 
        WHEN f.billing_cycle = 'Annual' THEN f.amount / 12.0 
        ELSE f.amount 
    END) * 12, 2) as ARR
FROM fact_sales f
JOIN dim_dates d ON f.date_key = d.date_key
WHERE f.payment_status = 'Paid'
GROUP BY d.year, d.month
ORDER BY d.year, d.month;


-- 2. Average Revenue Per User (ARPU)
-- MRR divided by total active users who made transactions or had active amortized subscriptions in that month
-- Using a temporary query matching the monthly recurrence:
WITH MonthlyPayments AS (
    SELECT 
        f.customer_id,
        d.year,
        d.month,
        CASE WHEN f.billing_cycle = 'Annual' THEN f.amount / 12.0 ELSE f.amount END as monthly_amount
    FROM fact_sales f
    JOIN dim_dates d ON f.date_key = d.date_key
    WHERE f.payment_status = 'Paid'
),
ActiveUsersByMonth AS (
    -- Group all months active (for annual plans, spread across 12 calendar months)
    -- We can model this by looking at transaction dates
    SELECT 
        customer_id,
        year,
        month,
        monthly_amount
    FROM MonthlyPayments
)
SELECT 
    year,
    month,
    COUNT(DISTINCT customer_id) as active_paying_users,
    ROUND(SUM(monthly_amount), 2) as estimated_mrr,
    ROUND(SUM(monthly_amount) / COUNT(DISTINCT customer_id), 2) as ARPU
FROM ActiveUsersByMonth
GROUP BY year, month
ORDER BY year, month;


-- 3. Monthly Churn Rate
-- Calculated as: (Customers lost in month) / (Total active customers at start of month)
-- For simplified SQL: Customers who were active in month N-1 but NOT active in month N
WITH MonthlyActiveUsers AS (
    SELECT DISTINCT 
        customer_id, 
        d.year, 
        d.month,
        (d.year * 12 + d.month) as month_index
    FROM fact_sales f
    JOIN dim_dates d ON f.date_key = d.date_key
    WHERE f.payment_status = 'Paid'
),
CohortComparison AS (
    SELECT 
        curr.year,
        curr.month,
        curr.month_index,
        COUNT(DISTINCT curr.customer_id) as active_this_month,
        -- Count how many of last month's active users are missing this month
        COUNT(DISTINCT prev.customer_id) as active_last_month,
        SUM(CASE WHEN next_m.customer_id IS NULL THEN 1 ELSE 0 END) as churned_next_month
    FROM MonthlyActiveUsers curr
    LEFT JOIN MonthlyActiveUsers prev ON curr.customer_id = prev.customer_id AND curr.month_index = prev.month_index + 1
    LEFT JOIN MonthlyActiveUsers next_m ON curr.customer_id = next_m.customer_id AND curr.month_index + 1 = next_m.month_index
    GROUP BY curr.year, curr.month, curr.month_index
)
SELECT 
    year,
    month,
    active_this_month as active_users,
    churned_next_month as churned_users,
    ROUND((churned_next_month / active_this_month) * 100, 2) as Churn_Rate_Percent
FROM CohortComparison
ORDER BY year, month;


-- 4. MoM Revenue Growth Rate
-- Calculates month-over-month percentage change in MRR
WITH MonthlyMRR AS (
    SELECT 
        d.year,
        d.month,
        (d.year * 12 + d.month) as month_index,
        SUM(CASE 
            WHEN f.billing_cycle = 'Annual' THEN f.amount / 12.0 
            ELSE f.amount 
        END) as mrr
    FROM fact_sales f
    JOIN dim_dates d ON f.date_key = d.date_key
    WHERE f.payment_status = 'Paid'
    GROUP BY d.year, d.month
)
SELECT 
    curr.year,
    curr.month,
    ROUND(curr.mrr, 2) as Current_MRR,
    ROUND(prev.mrr, 2) as Previous_MRR,
    ROUND(((curr.mrr - prev.mrr) / prev.mrr) * 100, 2) as Growth_Rate_Percent
FROM MonthlyMRR curr
LEFT JOIN MonthlyMRR prev ON curr.month_index = prev.month_index + 1
ORDER BY curr.year, curr.month;
