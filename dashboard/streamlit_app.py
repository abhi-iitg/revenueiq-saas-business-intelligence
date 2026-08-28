import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page configuration for wide layout and premium title
st.set_page_config(
    page_title="RevenueIQ — SaaS Business Intelligence & Customer Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------
# Custom Styling
# ------------------
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .metric-card {
        background-color: #1f2937;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
        border: 1px solid #374151;
    }
    .metric-title {
        font-size: 14px;
        color: #9ca3af;
        margin-bottom: 5px;
        font-weight: 500;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #60a5fa;
    }
    .metric-change {
        font-size: 12px;
        margin-top: 5px;
    }
    .metric-positive {
        color: #10b981;
    }
    .metric-negative {
        color: #ef4444;
    }
</style>
""", unsafe_allow_html=True)

# ------------------
# Load Data
# ------------------
@st.cache_data
def load_processed_data():
    base_path = "data/processed"
    
    # Load files
    df_rfm = pd.read_csv(os.path.join(base_path, "customer_rfm.csv"))
    df_churn = pd.read_csv(os.path.join(base_path, "customer_churn.csv"))
    df_clv = pd.read_csv(os.path.join(base_path, "customer_clv.csv"))
    df_cohort = pd.read_csv(os.path.join(base_path, "cohort_retention.csv"), index_col=0)
    df_revenue = pd.read_csv(os.path.join(base_path, "monthly_revenue_kpis.csv"))
    df_sales = pd.read_csv(os.path.join(base_path, "fact_sales.csv"))
    df_prod = pd.read_csv(os.path.join(base_path, "dim_products.csv"))
    
    # Pre-merge customer and CLV details
    df_cust_analytics = pd.merge(df_churn, df_rfm[["customer_id", "recency", "frequency", "monetary", "rfm_segment"]], on="customer_id", how="left")
    df_cust_analytics = pd.merge(df_cust_analytics, df_clv[["customer_id", "historical_clv", "predicted_clv"]], on="customer_id", how="left")
    
    return df_cust_analytics, df_cohort, df_revenue, df_sales, df_prod

try:
    df_cust, df_cohort, df_revenue, df_sales, df_prod = load_processed_data()
except Exception as e:
    st.error(f"Error loading processed data. Please ensure the ETL pipeline has run. Details: {e}")
    st.stop()

# ------------------
# Sidebar Controls
# ------------------
st.sidebar.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=400&q=80", use_column_width=True)
st.sidebar.title("Product Intelligence Control Center")
st.sidebar.markdown("---")

# Segment Filter
all_segments = ["All"] + list(df_cust["segment"].unique())
selected_segment = st.sidebar.selectbox("Customer Segment", all_segments)

# Country Filter
all_countries = ["All"] + list(df_cust["country"].unique())
selected_country = st.sidebar.selectbox("Country/Region", all_countries)

# Subscription Tier Filter
all_tiers = ["All"] + list(df_prod["tier"].unique())
selected_tier = st.sidebar.selectbox("Product Tier", all_tiers)

# Apply filters
df_cust_filtered = df_cust.copy()
if selected_segment != "All":
    df_cust_filtered = df_cust_filtered[df_cust_filtered["segment"] == selected_segment]
if selected_country != "All":
    df_cust_filtered = df_cust_filtered[df_cust_filtered["country"] == selected_country]
if selected_tier != "All":
    # Link product tier
    df_cust_filtered = df_cust_filtered[df_cust_filtered["customer_id"].isin(
        df_cust[df_cust["product_id"].isin(df_prod[df_prod["tier"] == selected_tier]["product_id"])]["customer_id"]
    )]

# ------------------
# Main Dashboard Header
# ------------------
st.title("🚀 Product Intelligence Platform")
st.markdown("Enterprise Dashboard for customer retention, churn, cohort analysis, and recurring revenue growth.")
st.markdown("---")

# ------------------
# KPI Cards Section
# ------------------
col1, col2, col3, col4, col5 = st.columns(5)

# Calculate latest MRR and MoM growth
latest_rev_row = df_revenue.iloc[-1]
prev_rev_row = df_revenue.iloc[-2] if len(df_revenue) > 1 else latest_rev_row

mrr_val = latest_rev_row["mrr"]
arr_val = latest_rev_row["arr"]
growth_val = latest_rev_row["mrr_growth_rate"] * 100

active_users_count = len(df_cust_filtered[df_cust_filtered["is_churned"] == 0])
total_users_count = len(df_cust_filtered)
churn_rate_val = (df_cust_filtered["is_churned"].sum() / total_users_count) * 100 if total_users_count > 0 else 0.0

avg_clv_val = df_cust_filtered["historical_clv"].mean()

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Monthly Rec. Revenue</div>
        <div class="metric-value">${mrr_val:,.0f}</div>
        <div class="metric-change metric-positive">▲ {growth_val:.1f}% MoM</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Annual Rec. Revenue</div>
        <div class="metric-value">${arr_val:,.0f}</div>
        <div class="metric-change metric-positive">Run Rate</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Active Customers</div>
        <div class="metric-value">{active_users_count:,}</div>
        <div class="metric-change" style="color: #9ca3af;">Total: {total_users_count:,}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Churn Rate (LTV)</div>
        <div class="metric-value">{churn_rate_val:.1f}%</div>
        <div class="metric-change metric-negative">▼ At risk</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Avg Historical CLV</div>
        <div class="metric-value">${avg_clv_val:,.2f}</div>
        <div class="metric-change metric-positive">▲ Per User</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ------------------
# Visualizations
# ------------------
tab_rev, tab_seg, tab_cohort, tab_churn = st.tabs([
    "📈 Revenue Analysis", 
    "👥 Customer Segmentation", 
    "📅 Cohort Retention", 
    "📉 Churn Insights"
])

# TAB 1: Revenue Analysis
with tab_rev:
    st.subheader("Monthly Recurring Revenue (MRR) & ARR Growth Trend")
    
    fig_mrr = go.Figure()
    fig_mrr.add_trace(go.Scatter(
        x=df_revenue["month"], 
        y=df_revenue["mrr"],
        mode='lines+markers',
        name='MRR ($)',
        line=dict(color='#3b82f6', width=3),
        fill='tozeroy',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))
    fig_mrr.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Billing Month",
        yaxis_title="MRR ($)",
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_mrr, use_container_width=True)
    
    # Revenue distribution metrics
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("ARR Contribution by Segment")
        fig_seg_pie = px.pie(
            df_cust_filtered, 
            names='segment', 
            values='historical_clv',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.4
        )
        fig_seg_pie.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_seg_pie, use_container_width=True)
        
    with c2:
        st.subheader("Revenue by Country")
        country_rev = df_cust_filtered.groupby("country")["historical_clv"].sum().reset_index()
        fig_country_bar = px.bar(
            country_rev.sort_values(by="historical_clv", ascending=True),
            x='historical_clv',
            y='country',
            orientation='h',
            color='historical_clv',
            color_continuous_scale='Blues'
        )
        fig_country_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Total Historical Sales ($)"
        )
        st.plotly_chart(fig_country_bar, use_container_width=True)

# TAB 2: Customer Segmentation
with tab_seg:
    st.subheader("Customer Distribution by RFM Segmentation")
    
    segment_counts = df_cust_filtered["rfm_segment"].value_counts().reset_index()
    segment_counts.columns = ["RFM Segment", "Customer Count"]
    
    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        fig_rfm_bar = px.bar(
            segment_counts,
            x="Customer Count",
            y="RFM Segment",
            orientation="h",
            color="Customer Count",
            color_continuous_scale="Viridis",
            text="Customer Count"
        )
        fig_rfm_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_rfm_bar, use_container_width=True)
        
    with col_s2:
        st.markdown("### Segment Descriptions")
        st.markdown("""
        * **Champions**: Bought recently, buy frequently, and spend the most!
        * **Loyal Customers**: Spend good money and buy regularly.
        * **New Customers**: Signed up recently but haven't placed many orders yet.
        * **At Risk**: Spent big money and purchased frequently, but been active long ago.
        * **About to Sleep**: Below average recency, frequency, and monetary scores.
        * **Lost**: Lowest recency, frequency, and monetary scores.
        """)

# TAB 3: Cohort Retention
with tab_cohort:
    st.subheader("Monthly Cohort Retention Heatmap (%)")
    st.markdown("Tracks customer sign-up month and percentage retention over subsequent months.")
    
    # We display up to 12 periods for visual clarity
    cohort_heatmap_data = df_cohort.iloc[:, :13].copy()
    
    # Format values as percentages
    fig_cohort = px.imshow(
        cohort_heatmap_data * 100,
        labels=dict(x="Months Since Signup", y="Cohort Month", color="Retention (%)"),
        x=cohort_heatmap_data.columns,
        y=cohort_heatmap_data.index,
        color_continuous_scale="Tealgrn",
        aspect="auto",
        text_auto=".1f"
    )
    
    fig_cohort.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=550
    )
    st.plotly_chart(fig_cohort, use_container_width=True)

# TAB 4: Churn Insights
with tab_churn:
    st.subheader("Churn Insights & Correlation")
    
    col_ch1, col_ch2 = st.columns(2)
    with col_ch1:
        st.markdown("### Churn Rate by Customer Segment")
        churn_seg = df_cust_filtered.groupby("segment")["is_churned"].mean().reset_index()
        churn_seg["is_churned"] *= 100
        fig_ch_seg = px.bar(
            churn_seg,
            x="segment",
            y="is_churned",
            color="segment",
            labels={"is_churned": "Churn Rate (%)"},
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_ch_seg.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_ch_seg, use_container_width=True)
        
    with col_ch2:
        st.markdown("### Churn Rate by Billing Cycle")
        churn_bill = df_cust_filtered.groupby("billing_cycle")["is_churned"].mean().reset_index()
        churn_bill["is_churned"] *= 100
        fig_ch_bill = px.bar(
            churn_bill,
            x="billing_cycle",
            y="is_churned",
            color="billing_cycle",
            labels={"is_churned": "Churn Rate (%)"},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_ch_bill.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_ch_bill, use_container_width=True)

st.markdown("---")
st.markdown("© 2026 Product Intelligence Platform. Built with Streamlit, Pandas, and Plotly.")
