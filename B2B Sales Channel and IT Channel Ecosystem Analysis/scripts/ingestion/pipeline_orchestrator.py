import schedule
import time
import subprocess
import os
import uuid
import sqlite3
from datetime import datetime

DB_PATH = "data/antigravity.db"

def run_script(script_path):
    """
    Runs a python script and logs the result.
    """
    print(f"[{datetime.now()}] Running {script_path}...")
    run_id = str(uuid.uuid4())
    try:
        result = subprocess.run(["python3", script_path], capture_output=True, text=True)
        status = "SUCCESS" if result.returncode == 0 else "FAILURE"
        message = result.stdout if result.returncode == 0 else result.stderr
        
        log_to_db(run_id, script_path, status, message[:500]) # Truncate message for DB
        print(f"Finished {script_path} with status {status}")
    except Exception as e:
        log_to_db(run_id, script_path, "ERROR", str(e))
        print(f"Error running {script_path}: {e}")

def log_to_db(run_id, script, status, message):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''
        INSERT INTO pipeline_logs (run_id, status, message)
        VALUES (?, ?, ?)
    ''', (f"{script}_{run_id}", status, message))
    conn.commit()
    conn.close()

def pipeline_job():
    print(f"\n--- Starting Pipeline Cycle at {datetime.now()} ---")
    scripts = [
        "scripts/ingestion/transaction_gen.py",
        "scripts/ingestion/trends_ingest.py",
        "scripts/ingestion/world_bank_ingest.py",
        "scripts/ingestion/finance_ingest.py"
    ]
    
    for script in scripts:
        run_script(script)
    print(f"--- Pipeline Cycle Completed ---\n")

def main():
    # Initial run
    pipeline_job()
    
    # Schedule every 15 minutes as per requirement
    schedule.every(15).minutes.do(pipeline_job)
    
    print("Orchestrator is running. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
