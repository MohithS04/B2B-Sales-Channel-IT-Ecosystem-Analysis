import sqlite3
import os

def setup_database(db_path="data/antigravity.db"):
    """
    Initializes the SQLite database with normalized schema.
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # B2B Transactions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            region TEXT,
            product TEXT,
            deal_value REAL,
            sales_stage TEXT,
            churn_risk_score REAL,
            rep_id TEXT,
            close_date TEXT,
            channel_type TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Market Trends Table (Google Trends)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT,
            region TEXT,
            interest_score INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Economic Indicators Table (World Bank)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS economic_indicators (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            indicator_code TEXT,
            country_code TEXT,
            value REAL,
            year INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tech Sector Signals Table (Yahoo Finance)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tech_signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            price REAL,
            revenue REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Pipeline Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pipeline_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            status TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database setup complete at {db_path}")

if __name__ == "__main__":
    setup_database()
