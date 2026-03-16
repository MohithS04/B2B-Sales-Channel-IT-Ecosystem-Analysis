import pandas as pd
from faker import Faker
import random
import sqlite3
import datetime
import os

def generate_transactions(num_records=100, db_path="data/antigravity.db"):
    """
    Generates synthetic B2B transaction records and saves them to the database.
    """
    fake = Faker()
    regions = ['North America', 'EMEA', 'APAC', 'LATAM']
    products = ['Cloud Suite Pro', 'CyberGuard Enterprise', 'DataSync AI', 'EdgeEdge Connect']
    stages = ['Prospecting', 'Qualification', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']
    channels = ['Direct', 'Partner', 'Digital']
    
    data = []
    for _ in range(num_records):
        close_date = fake.date_between(start_date='-1y', end_date='today')
        data.append({
            'customer_id': fake.company_suffix() + "_" + str(fake.random_int(min=1000, max=9999)),
            'region': random.choice(regions),
            'product': random.choice(products),
            'deal_value': round(random.uniform(5000, 250000), 2),
            'sales_stage': random.choice(stages),
            'churn_risk_score': round(random.uniform(0, 1), 2),
            'rep_id': "REP_" + str(fake.random_int(min=1, max=50)),
            'close_date': close_date.strftime('%Y-%m-%d'),
            'channel_type': random.choice(channels)
        })
    
    df = pd.DataFrame(data)
    
    # Save to SQLite
    conn = sqlite3.connect(db_path)
    df.to_sql('transactions', conn, if_exists='append', index=False)
    conn.close()
    
    print(f"Generated {num_records} synthetic transactions and stored in {db_path}")
    return df

if __name__ == "__main__":
    # Ensure current directory is correct or use absolute path
    generate_transactions(200)
