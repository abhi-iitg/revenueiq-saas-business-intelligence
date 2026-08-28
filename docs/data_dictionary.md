# Data Dictionary - RevenueIQ — SaaS Business Intelligence & Customer Analytics Platform

This document describes the structure of the data models used in the RevenueIQ — SaaS Business Intelligence & Customer Analytics Platform's star schema database.

---

## 1. Table: `dim_customers`
Contains demographic and subscription-start attributes for customers.

| Column Name | Data Type | Key Type | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `customer_id` | `VARCHAR(50)` | Primary Key | Unique identifier for a customer. | `C00001` |
| `customer_name` | `VARCHAR(255)` | - | Full name of the customer. | `John Smith` |
| `email` | `VARCHAR(255)` | - | Contact email address. | `john.smith@example.com` |
| `signup_date` | `DATE` | - | Date the customer signed up. | `2023-01-15` |
| `country` | `VARCHAR(100)` | - | Country where customer is located. | `United States` |
| `segment` | `VARCHAR(50)` | - | Business scale segment: `SMB`, `Mid-Market`, `Enterprise`. | `SMB` |
| `cohort_month` | `VARCHAR(7)` | - | Calculated cohort month (YYYY-MM). | `2023-01` |

---

## 2. Table: `dim_products`
Defines the software-as-a-service (SaaS) products/plans offered.

| Column Name | Data Type | Key Type | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `product_id` | `VARCHAR(50)` | Primary Key | Unique identifier for the product. | `P001` |
| `product_name` | `VARCHAR(255)` | - | Name of the product tier. | `CloudSuite Starter` |
| `tier` | `VARCHAR(50)` | - | Plan tier level: `Basic`, `Pro`, `Enterprise`. | `Basic` |
| `monthly_price` | `DECIMAL(10,2)` | - | List price for monthly billing cycle. | `29.00` |
| `annual_price` | `DECIMAL(10,2)` | - | List price for annual billing cycle. | `290.00` |

---

## 3. Table: `dim_dates`
Enterprise calendar dimension for complex time-intelligence queries.

| Column Name | Data Type | Key Type | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `date_key` | `VARCHAR(10)` | Primary Key | Date formatted as string key (YYYY-MM-DD). | `2023-01-15` |
| `date_actual` | `DATE` | - | Calendar date value. | `2023-01-15` |
| `year` | `INT` | - | Calendar year. | `2023` |
| `quarter` | `INT` | - | Calendar quarter (1-4). | `1` |
| `month` | `INT` | - | Month index (1-12). | `1` |
| `month_name` | `VARCHAR(20)` | - | Full name of the month. | `January` |
| `day` | `INT` | - | Day of the month (1-31). | `15` |
| `day_of_week` | `INT` | - | Day index: 1 (Monday) to 7 (Sunday). | `7` |
| `is_weekend` | `TINYINT(1)` | - | Flag indicating weekend (1) or weekday (0). | `1` |

---

## 4. Table: `fact_sales`
Fact table capturing all subscription and payment transactions.

| Column Name | Data Type | Key Type | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `transaction_id` | `VARCHAR(50)` | Primary Key | Unique payment transaction identifier. | `T0000001` |
| `customer_id` | `VARCHAR(50)` | Foreign Key | References `dim_customers`. | `C00001` |
| `product_id` | `VARCHAR(50)` | Foreign Key | References `dim_products`. | `P001` |
| `date_key` | `VARCHAR(10)` | Foreign Key | References `dim_dates` (transaction date). | `2023-01-15` |
| `amount` | `DECIMAL(10,2)` | - | Transacted currency amount. | `29.00` |
| `billing_cycle` | `VARCHAR(20)` | - | Plan contract type: `Monthly`, `Annual`. | `Monthly` |
| `payment_status` | `VARCHAR(50)` | - | Payment result: `Paid`, `Failed`, `Refunded`. | `Paid` |
