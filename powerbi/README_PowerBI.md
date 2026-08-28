# Power BI Dashboard Design Guide - RevenueIQ — SaaS Business Intelligence & Customer Analytics Platform

This folder contains details for configuring the **Product Intelligence Dashboard** in Microsoft Power BI using the star schema database created by the ETL pipeline.

---

## 1. Data Model Configuration
Connect Power BI to your MySQL / SQLite warehouse and set up the following relationships:

* **`fact_sales` [Many] ─── [1] `dim_customers`** on `customer_id` (Active relationship, Single direction)
* **`fact_sales` [Many] ─── [1] `dim_products`** on `product_id` (Active relationship, Single direction)
* **`fact_sales` [Many] ─── [1] `dim_dates`** on `date_key` (Active relationship, Single direction)

---

## 2. Calculated DAX Measures

### A. Monthly Recurring Revenue (MRR)
Spreads annual contract revenue over 12 billing months:
```dax
MRR = 
SUMX(
    fact_sales,
    IF(
        fact_sales[billing_cycle] = "Annual",
        fact_sales[amount] / 12,
        fact_sales[amount]
    )
)
```

### B. Average Revenue Per User (ARPU)
```dax
ARPU = 
DIVIDE(
    [MRR],
    DISTINCTCOUNT(fact_sales[customer_id]),
    0
)
```

### C. Churn Rate (%)
```dax
Churn Rate = 
VAR TotalCustomers = DISTINCTCOUNT(dim_customers[customer_id])
VAR ChurnedCustomers = CALCULATE(COUNT(dim_customers[customer_id]), dim_customers[is_churned] = 1)
RETURN
DIVIDE(ChurnedCustomers, TotalCustomers, 0)
```

---

## 3. Visual Layout Recommendations

### Page 1: Revenue Operations
* **KPI Card Visuals**: MRR, ARR Run Rate, ARPU, Active Customers.
* **Line Chart**: MRR Trend over months (X-axis: `dim_dates[month_name]`, Y-axis: `[MRR]`).
* **Donut Chart**: Revenue share by Customer Segment (`dim_customers[segment]`).
* **Map Visual**: Sales by Customer Country (`dim_customers[country]`).

### Page 2: Customer Retention & Segmentation
* **Matrix Heatmap**: Cohort Retention Matrix (Rows: `dim_customers[cohort_month]`, Columns: `cohort_index`, Values: `% Retention`).
* **Clustered Bar Chart**: RFM Segments Distribution (X-axis: Customer Count, Y-axis: `rfm_segment`).
* **Scatter Plot**: Frequency vs. Monetary value by Segment.
