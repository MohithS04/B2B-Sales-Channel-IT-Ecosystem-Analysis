from pytrends.request import TrendReq
import sqlite3
import pandas as pd
import time
import os

def ingest_trends(db_path="data/antigravity.db"):
    """
    Ingests market demand signals from Google Trends.
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    keywords = ["Cloud Computing", "Cybersecurity", "Enterprise AI", "CRM Software", "IT Infrastructure"]
    
    print(f"Fetching Google Trends for: {keywords}")
    
    try:
        pytrends.build_payload(keywords, cat=0, timeframe='today 3-m', geo='', gprop='')
        df = pytrends.interest_over_time()
        
        if df.empty:
            print("No trend data found.")
            return
            
        # Clean and Melt
        df = df.drop(columns=['isPartial']).reset_index()
        df_melted = df.melt(id_vars=['date'], value_vars=keywords, var_name='keyword', value_name='interest_score')
        
        # Save to SQLite
        conn = sqlite3.connect(db_path)
        # We'll map 'date' to 'timestamp' in the DB if needed, but the interest_score table has its own timestamp
        # Actually, let's keep the date from Trends as part of the record
        to_save = df_melted.rename(columns={'date': 'trend_date'})
        # Note: the tech_signals table in db_setup was id, keyword, region, interest_score, timestamp
        # I'll adjust the insertion to match
        
        for _, row in to_save.iterrows():
            conn.execute('''
                INSERT INTO market_trends (keyword, region, interest_score, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (row['keyword'], 'Global', row['interest_score'], str(row['trend_date'])))
            
        conn.commit()
        conn.close()
        print("Google Trends data stored successfully.")
        
    except Exception as e:
        print(f"Error fetching Google Trends: {e}")

if __name__ == "__main__":
    ingest_trends()
