import wbgapi as wb
import sqlite3
import pandas as pd
import datetime

def ingest_world_bank(db_path="data/antigravity.db"):
    """
    Ingests economic indicators from World Bank.
    """
    # Indicators: GDP (NY.GDP.MKTP.CD), High-tech exports (TX.VAL.TECH.CD)
    indicators = {'NY.GDP.MKTP.CD': 'GDP', 'TX.VAL.TECH.CD': 'Tech_Exports'}
    countries = ['USA', 'CHN', 'IND', 'GBR', 'DEU'] # Top economies
    
    print(f"Fetching World Bank data for indicators: {list(indicators.keys())}")
    
    try:
        # Fetching data for the last available year
        # wbgapi.data.DataFrame returns multi-index index=[economy, series] by default if multiple types
        df = wb.data.DataFrame(list(indicators.keys()), countries, mrv=1)
        
        conn = sqlite3.connect(db_path)
        # Iterate over multi-index
        for (country_code, indicator_code), value in df.stack().items():
            # value here is the GDP/Export value
            # The column name in the original df is usually YR2023 etc.
            
            conn.execute('''
                INSERT INTO economic_indicators (indicator_code, country_code, value, year)
                VALUES (?, ?, ?, ?)
            ''', (indicator_code, country_code, value, datetime.datetime.now().year))
            
        conn.commit()
        conn.close()
        print("World Bank data stored successfully.")
        
    except Exception as e:
        print(f"Error fetching World Bank data: {e}")

if __name__ == "__main__":
    ingest_world_bank()
