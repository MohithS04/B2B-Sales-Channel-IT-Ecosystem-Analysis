import yfinance as yf
import sqlite3
import pandas as pd

def ingest_finance(db_path="data/antigravity.db"):
    """
    Ingests tech sector signals from Yahoo Finance.
    """
    tickers = ["MSFT", "GOOGL", "AMZN", "CRM", "SAP"]
    
    print(f"Fetching Tech Sector Signals for: {tickers}")
    
    try:
        data = []
        for ticker in tickers:
            t = yf.Ticker(ticker)
            info = t.info
            price = info.get('currentPrice', info.get('regularMarketPrice'))
            revenue = info.get('totalRevenue')
            
            data.append({
                'ticker': ticker,
                'price': price,
                'revenue': revenue
            })
            
        df = pd.DataFrame(data)
        
        conn = sqlite3.connect(db_path)
        df.to_sql('tech_signals', conn, if_exists='append', index=False)
        conn.close()
        print("Tech sector signals stored successfully.")
        
    except Exception as e:
        print(f"Error fetching Finance data: {e}")

if __name__ == "__main__":
    ingest_finance()
