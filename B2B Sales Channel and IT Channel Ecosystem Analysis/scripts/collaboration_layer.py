import pandas as pd
import sqlite3
import json
import os
from datetime import datetime

DB_PATH = "data/antigravity.db"
EXPORT_DIR = "data/team_exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

def export_sales_team(df):
    print("Exporting Sales Team Review (Excel Pivot)...")
    path = f"{EXPORT_DIR}/sales_team_extract.xlsx"
    # Create a pivot table for them
    pivot = df.pivot_table(index='region', columns='product', values='deal_value', aggfunc='sum')
    pivot.to_excel(path)
    print(f"Sales export saved: {path}")

def export_finance_team(df):
    print("Exporting Finance Team Review (Aggregated CSV)...")
    path = f"{EXPORT_DIR}/finance_revenue_summary.csv"
    summary = df.groupby(['region', 'channel_type'])['deal_value'].agg(['sum', 'mean', 'count']).reset_index()
    summary.to_csv(path, index=False)
    print(f"Finance export saved: {path}")

def export_it_team(df):
    print("Exporting IT Team Review (Schema JSON)...")
    path = f"{EXPORT_DIR}/it_schema_report.json"
    report = {
        "report_date": datetime.now().strftime('%Y-%m-%d'),
        "table": "transactions",
        "record_count": len(df),
        "columns": list(df.columns),
        "data_types": df.dtypes.apply(lambda x: str(x)).to_dict()
    }
    with open(path, 'w') as f:
        json.dump(report, f, indent=4)
    print(f"IT export saved: {path}")

def main():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    conn.close()
    
    export_sales_team(df)
    export_finance_team(df)
    export_it_team(df)
    print("Collaboration exports completed.")

if __name__ == "__main__":
    main()
