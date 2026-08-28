# Project Documentation - RevenueIQ — SaaS Business Intelligence & Customer Analytics Platform

## 1. System Architecture

The RevenueIQ Analytics Platform is built on a standard modular data warehousing architecture utilizing a star schema layout. 

```
               [Raw Source Datasets (CSVs)]
                            │
                            ▼
              [ETL Pipeline (etl_pipeline.py)]
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          [Extract]     [Transform]     [Load]
                            │
                            ▼
              [MySQL / SQLite Database]
              ┌─────────────┴─────────────┐
              ▼                           ▼
      [Star Schema Tables]        [Analytics Calculations]
      - dim_customers             - Churn Risk Analysis
      - dim_products              - RFM Segmentation
      - dim_dates                 - Customer Lifetime Value (CLV)
      - fact_sales                - Cohort Retention
                            │
                            ▼
           [Streamlit & Power BI Dashboards]
```

- **Extraction Layer**: Reads or dynamically simulates raw SaaS transactions, client sign-ups, and subscription tier specifications.
- **Transformation Layer**: Models records into dimensional representations. Computes index values and groups cohorts by signup timeline.
- **Loading Layer**: Performs transactional commits into the target data warehouse (supporting local SQLite engine or MySQL connection).
- **Analytics Layer**: Executed programmatically to output customer metrics, scoring files, and matrices.
- **Presentation Layer**: Streamlit web dashboard and Power BI template reporting tools.

---

## 2. Business Analytics Methodology

### A. Customer Lifetime Value (CLV) Calculation
Historical CLV is the absolute total dollar amount a customer has spent on successfully processed plan cycles:
$$\text{Historical CLV} = \sum (\text{Transaction Amount}) \quad \text{where status} = \text{'Paid'}$$

SaaS Predictive CLV is modelled at the customer segment level (SMB, Mid-Market, Enterprise) and mapped to active customer classes:
$$\text{Predictive CLV} = \frac{\text{ARPU} \times \text{Gross Margin}}{\text{Monthly Churn Rate}}$$
- **ARPU**: Average Revenue Per User calculated per segment.
- **Gross Margin**: Standardized to 85% for Cloud SaaS providers.
- **Monthly Churn Rate**: Segment Churn rate normalized to monthly duration.

### B. RFM Segmentation Logic
Customers are segmented based on their transaction history using Recency (R), Frequency (F), and Monetary (M) scores. Scores range from 1 (worst) to 5 (best) based on quintiles of the customer base.

- **Champions**: R: 4-5, F: 4-5.
- **Loyal Customers**: R: 3-5, F: 3-5.
- **New Customers**: R: 4-5, F: 1.
- **At Risk**: R: 2, F: 4-5.
- **Lost**: R: 1, F: 1-2.

### C. Cohort Retention Analysis
We group users into monthly cohorts based on their `signup_date`. The retention rate for each cohort in Month $N$ is calculated as:
$$\text{Retention Rate}_{Cohort, Month\ N} = \frac{\text{Unique Active Customers in Month}\ N}{\text{Cohort Size}}$$
where active engagement is defined as having at least one successful subscription payment in that month.
