import pandas as pd
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import openpyxl
import os
import numpy as np
from datetime import datetime

DB_PATH = "data/antigravity.db"
REPORTS_DIR = "reports/automated"
os.makedirs(REPORTS_DIR, exist_ok=True)

def perform_data_validation():
    print("Running Data Integrity Checks...")
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    
    # 1. Null/Duplicate detection
    null_counts = df.isnull().sum().sum()
    duplicate_count = df.duplicated().sum()
    
    # 2. Anomaly detection (Z-score on deal_value)
    mean_val = df['deal_value'].mean()
    std_val = df['deal_value'].std()
    df['z_score'] = (df['deal_value'] - mean_val) / std_val
    anomalies = df[df['z_score'].abs() > 3].shape[0]
    
    # 3. Quality Scorecard
    total_records = len(df)
    integrity_score = ((total_records - (null_counts + duplicate_count + anomalies)) / total_records) * 100
    
    report_html = f"""
    <html>
    <head><title>Data Quality Report</title></head>
    <body style='font-family: sans-serif; background: #f4f4f4; padding: 20px;'>
        <div style='background: white; padding: 20px; border-radius: 10px;'>
            <h1>Daily Data Quality Scorecard - {datetime.now().strftime('%Y-%m-%d')}</h1>
            <h2 style='color: {'green' if integrity_score > 95 else 'orange'};'>Integrity Score: {integrity_score:.2f}%</h2>
            <hr>
            <ul>
                <li>Total Records: {total_records}</li>
                <li>Null Values Found: {null_counts}</li>
                <li>Duplicate Records: {duplicate_count}</li>
                <li>Anomalies Detected (Z-score > 3): {anomalies}</li>
            </ul>
        </div>
    </body>
    </html>
    """
    with open(f"{REPORTS_DIR}/data_quality_report.html", "w") as f:
        f.write(report_html)
    
    print(f"Data validation complete. Score: {integrity_score:.2f}%")
    return df

def generate_pdf_report(df):
    print("Generating PDF Executive Summary...")
    filepath = f"{REPORTS_DIR}/Executive_Summary_{datetime.now().strftime('%Y%m%d')}.pdf"
    c = canvas.Canvas(filepath, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 750, "Google Antigravity: B2B Sales Executive Summary")
    c.setFont("Helvetica", 12)
    c.drawString(100, 730, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    c.drawString(100, 700, f"Total Pipeline Value: ${df['deal_value'].sum():,.2f}")
    c.drawString(100, 680, f"Total Deals Managed: {len(df)}")
    c.drawString(100, 660, f"Top Performing Region: {df.groupby('region')['deal_value'].sum().idxmax()}")
    
    c.drawString(100, 620, "Summary Table (Top 5 Active Deals):")
    y = 600
    for idx, row in df.sort_values(by='deal_value', ascending=False).head(5).iterrows():
        c.drawString(120, y, f"ID: {row['customer_id']} | Value: ${row['deal_value']:,.2f} | Region: {row['region']}")
        y -= 20
        
    c.showPage()
    c.save()
    print(f"PDF Report saved to {filepath}")

def generate_excel_report(df):
    print("Generating Excel Data Extract...")
    filepath = f"{REPORTS_DIR}/Sales_Extract_{datetime.now().strftime('%Y%m%d')}.xlsx"
    df.to_excel(filepath, index=False)
    print(f"Excel Report saved to {filepath}")

def main():
    df = perform_data_validation()
    generate_pdf_report(df)
    generate_excel_report(df)

if __name__ == "__main__":
    main()
