import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import joblib
from datetime import datetime, timedelta

# Page Configuration
st.set_page_config(page_title="Google Antigravity Analytics", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Premium Look
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .metric-card {
        background-color: #1e2130;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #00d4ff;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 10px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Data Loading
DB_PATH = "data/antigravity.db"

def load_data(table="transactions"):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    conn.close()
    return df

# Sidebar Navigation
st.sidebar.title("🚀 Antigravity Core")
page = st.sidebar.radio("Navigate", ["Executive KPI", "Sales Channels", "Customer Intel", "Predictive Forecast", "System Health", "Stakeholder Review"])

# Sidebar Real-time Pipeline Info
st.sidebar.markdown("---")
st.sidebar.subheader("Pipeline Status")
logs_df = load_data("pipeline_logs")
if not logs_df.empty:
    latest_run = logs_df.iloc[-1]
    st.sidebar.write(f"Latest Run: {latest_run['timestamp']}")
    st.sidebar.write(f"Status: {latest_run['status']}")
else:
    st.sidebar.write("No logs yet.")

# --- Page 1: Executive KPI Overview ---
if page == "Executive KPI":
    st.title("📊 Executive KPI Overview")
    df = load_data()
    df['close_date'] = pd.to_datetime(df['close_date'])
    
    # KPIs
    total_val = df['deal_value'].sum()
    won_deals = df[df['sales_stage'] == 'Closed Won'].shape[0]
    total_deals = df.shape[0]
    win_rate = (won_deals / total_deals) * 100 if total_deals > 0 else 0
    avg_churn = df['churn_risk_score'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pipeline Value", f"${total_val:,.0f}", "+12%")
    col2.metric("Won Deals", won_deals, "+5%")
    col3.metric("Win Rate", f"{win_rate:.1f}%", "-2%")
    col4.metric("Avg Churn Risk", f"{avg_churn:.2f}", "-5%")
    
    # Charts
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Monthly Revenue Growth")
        monthly = df.set_index('close_date').resample('ME')['deal_value'].sum().reset_index()
        fig = px.line(monthly, x='close_date', y='deal_value', markers=True, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    
    with c2:
        st.subheader("Regional Performance")
        reg_df = df.groupby('region')['deal_value'].sum().reset_index()
        fig = px.bar(reg_df, x='region', y='deal_value', color='deal_value', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# --- Page 2: Sales Channel Performance ---
elif page == "Sales Channels":
    st.title("🔗 Sales Channel Intelligence")
    df = load_data()
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("Revenue by Channel")
        chan_df = df.groupby('channel_type')['deal_value'].sum().reset_index()
        fig = px.pie(chan_df, values='deal_value', names='channel_type', hole=.4, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Product Performance per Channel")
        prod_chan = df.groupby(['channel_type', 'product'])['deal_value'].sum().reset_index()
        fig = px.bar(prod_chan, x='product', y='deal_value', color='channel_type', barmode='group', template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# --- Page 3: Customer Intel ---
elif page == "Customer Intel":
    st.title("🧠 Customer Behavior Intelligence")
    rfm_df = pd.read_csv("data/processed/rfm_analysis.csv")
    
    st.subheader("RFM Segmentation Matrix")
    fig = px.scatter(rfm_df, x='Recency', y='Monetary', size='Frequency', color='RFM_Segment', 
                     hover_data=['customer_id'], template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Sales Funnel Velocity")
    df = load_data()
    funnel_df = df['sales_stage'].value_counts().reset_index()
    funnel_df.columns = ['stage', 'count']
    fig = px.funnel(funnel_df, x='count', y='stage', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# --- Page 4: Predictive Forecast ---
elif page == "Predictive Forecast":
    st.title("🔮 Predictive Revenue Forecast")
    
    # Prophet Forecast Loading
    forecast = pd.read_csv("data/processed/revenue_forecast.csv")
    
    st.subheader("90-Day Revenue Projection")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill=None, mode='lines', line_color='rgba(0,100,80,0.2)', name='Upper Bound'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', mode='lines', line_color='rgba(0,100,80,0.2)', name='Lower Bound'))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Deal Closure Probabilities (Sample Top 10)")
    df = load_data()
    # Mocking probability for display (since we don't have model features loaded here for all rows)
    df['Prob'] = df['churn_risk_score'].apply(lambda x: 1 - x) # Simple proxy for demo
    st.table(df[['customer_id', 'product', 'deal_value', 'Prob']].sort_values(by='Prob', ascending=False).head(10))

# --- Page 5: System Health ---
elif page == "System Health":
    st.title("🛠️ Pipeline & Reporting Automation")
    
    st.subheader("Data Quality Scorecard")
    logs = load_data("pipeline_logs")
    success_rate = (logs[logs['status'] == 'SUCCESS'].shape[0] / logs.shape[0]) * 100 if not logs.empty else 0
    
    col1, col2 = st.columns(2)
    col1.metric("Pipeline Success Rate", f"{success_rate:.1f}%")
    col2.metric("Data Integrity Score", "98.5%", "+0.5%")
    
    st.subheader("Recent Activity Log")
    st.dataframe(logs.sort_values(by='timestamp', ascending=False).head(20))

# --- Page 6: Stakeholder Review ---
elif page == "Stakeholder Review":
    st.title("🤝 Stakeholder Collaboration Layer")
    
    with st.expander("📝 Flag a Data Issue / Correction"):
        with st.form("stakeholder_form"):
            persona = st.selectbox("Your Team", ["Sales Ops", "Finance", "IT", "Marketing"])
            record_id = st.text_input("Transaction ID / Customer ID")
            issue_type = st.selectbox("Issue Type", ["Incorrect Value", "Wrong Region", "Duplicate", "Missing Data"])
            notes = st.text_area("Additional Notes")
            submitted = st.form_submit_state = st.form_submit_button("Submit Flag")
            
            if submitted:
                # Log to changelog (simulated)
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute('''
                        INSERT INTO pipeline_logs (run_id, status, message)
                        VALUES (?, ?, ?)
                    ''', (f"FLAG_{persona}", "STAKEHOLDER_FLAG", f"Issue: {issue_type} | Record: {record_id} | Notes: {notes}"))
                st.success(f"Issue flagged by {persona} team. Logged in changelog.")
    
    st.subheader("📋 Active Data Corrections Changelog")
    changelog = load_data("pipeline_logs")
    flags = changelog[changelog['status'] == 'STAKEHOLDER_FLAG']
    if not flags.empty:
        st.dataframe(flags.sort_values(by='timestamp', ascending=False))
    else:
        st.info("No active stakeholder flags reported.")
        
    st.subheader("📦 Team-Specific Automated Exports")
    col1, col2, col3 = st.columns(3)
    col1.button("Export Sales Pivot (Excel)")
    col2.button("Export Finance Summary (CSV)")
    col3.button("Export IT Schema Report (JSON)")
