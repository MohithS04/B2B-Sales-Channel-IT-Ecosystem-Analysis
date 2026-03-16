import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.seasonal import STL
import datetime
import os

DB_PATH = "data/antigravity.db"
OUTPUT_DIR = "reports/eda_plots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    # Convert dates
    df['close_date'] = pd.to_datetime(df['close_date'])
    conn.close()
    return df

def rfm_analysis(df):
    print("Performing RFM Analysis...")
    # Reference date is the max date in dataset
    snapshot_date = df['close_date'].max() + datetime.timedelta(days=1)
    
    rfm = df.groupby('customer_id').agg({
        'close_date': lambda x: (snapshot_date - x.max()).days,
        'transaction_id': 'count',
        'deal_value': 'sum'
    })
    
    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    
    # Segmentation logic (simple quartiles)
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=[4, 3, 2, 1])
    rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=[1, 2, 3, 4])
    
    rfm['RFM_Segment'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=rfm, x='Recency', y='Monetary', hue='Frequency', size='Monetary', palette='viridis')
    plt.title('RFM Segmentation: Recency vs Monetary')
    plt.savefig(f"{OUTPUT_DIR}/rfm_scatter.png")
    plt.close()
    
    rfm.to_csv(f"data/processed/rfm_analysis.csv")
    return rfm

def regional_analysis(df):
    print("Performing Regional Analysis...")
    regional = df.groupby('region').agg({'deal_value': 'sum', 'transaction_id': 'count'}).sort_values(by='deal_value', ascending=False)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=regional.index, y=regional['deal_value'], palette='magma')
    plt.title('Total Deal Value by Region')
    plt.savefig(f"{OUTPUT_DIR}/regional_sales.png")
    plt.close()
    
    return regional

def funnel_analysis(df):
    print("Performing Funnel Analysis...")
    stages_order = ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
    funnel = df['sales_stage'].value_counts().reindex(stages_order).fillna(0)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=funnel.values, y=funnel.index, palette='coolwarm')
    plt.title('Sales Funnel Conversion Stages')
    plt.savefig(f"{OUTPUT_DIR}/sales_funnel.png")
    plt.close()

def channel_analysis(df):
    print("Performing Channel Analysis...")
    channel = df.groupby('channel_type')['deal_value'].sum().reset_index()
    
    plt.figure(figsize=(8, 8))
    plt.pie(channel['deal_value'], labels=channel['channel_type'], autopct='%1.1f%%', colors=sns.color_palette('pastel'))
    plt.title('Revenue by Channel')
    plt.savefig(f"{OUTPUT_DIR}/channel_performance.png")
    plt.close()

def seasonality_analysis(df):
    print("Performing Seasonality Decomposition...")
    # Group by month
    monthly = df.set_index('close_date').resample('M')['deal_value'].sum().fillna(0)
    
    if len(monthly) >= 24: # STL needs enough points, but we only have 1 year in synthetic
        # Fallback to simple line plot if not enough data for meaningful STL
        plt.figure(figsize=(12, 6))
        monthly.plot()
        plt.title('Monthly Revenue Trend')
        plt.savefig(f"{OUTPUT_DIR}/revenue_trend.png")
        plt.close()
    else:
        plt.figure(figsize=(12, 6))
        monthly.plot(marker='o')
        plt.title('Monthly Sales Trend (Historical)')
        plt.savefig(f"{OUTPUT_DIR}/revenue_trend.png")
        plt.close()

def correlation_analysis(df):
    print("Performing Correlation Matrix...")
    # Encode categorical
    df_encoded = df.copy()
    df_encoded['region'] = df_encoded['region'].astype('category').cat.codes
    df_encoded['product'] = df_encoded['product'].astype('category').cat.codes
    df_encoded['channel_type'] = df_encoded['channel_type'].astype('category').cat.codes
    df_encoded['sales_stage'] = df_encoded['sales_stage'].apply(lambda x: 1 if x == 'Closed Won' else 0)
    
    corr = df_encoded[['deal_value', 'churn_risk_score', 'region', 'product', 'channel_type', 'sales_stage']].corr()
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, annot=True, cmap='RdBu_r', center=0)
    plt.title('Correlation Matrix: Drivers of Deal Closure')
    plt.savefig(f"{OUTPUT_DIR}/correlation_matrix.png")
    plt.close()

def main():
    df = load_data()
    rfm_analysis(df)
    regional_analysis(df)
    funnel_analysis(df)
    channel_analysis(df)
    seasonality_analysis(df)
    correlation_analysis(df)
    
    # Export summary CSV
    summary = df.describe()
    summary.to_csv("data/processed/eda_summary.csv")
    print("EDA completed. Plots saved to reports/eda_plots/")

if __name__ == "__main__":
    main()
