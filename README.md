# 🚀 B2B Sales Channel & IT Ecosystem Analysis

Google Antigravity is a production-grade analytics and intelligence platform designed to provide real-time insights into B2B sales cycles and the broader IT ecosystem. By combining live market data, economic indicators, and advanced predictive modeling, the platform empowers Sales Ops, Finance, and IT teams to make data-driven decisions.

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| **Data Ingestion** | Python, `pytrends`, `wbgapi`, `yfinance`, `Faker` |
| **Storage** | SQLite (Normalized Schema) |
| **EDA & Modeling** | Pandas, Scikit-learn, XGBoost, Facebook Prophet, SHAP |
| **Dashboard** | Streamlit, Plotly |
| **Automation** | `schedule`, `reportlab`, `openpyxl` |
| **Logging** | SQLite-based Pipeline Logs |

## ✨ Key Features

### 1. Real-Time Data Pipeline
- **Automated Ingestion**: Scheduled via `pipeline_orchestrator.py` to run every 15 minutes.
- **Multi-Source Logic**: Ingests market demand (Google Trends), GDP/Economic signals (World Bank), and Tech Sector valuation (Yahoo Finance).
- **Synthetic Transactions**: Generates realistic B2B sales records (deal size, stage, churn risk) for simulation.

### 2. Exploratory Data Analysis (EDA)
- **RFM Excellence**: Deep-dive Customer behavior segmentation.
- **Channel Intel**: Direct vs Partner vs Digital performance analysis.
- **Seasonality**: Revenue decomposition and trend forecasting.
- **Visualization**: Auto-generated heatmaps and correlation matrices in `reports/eda_plots/`.

### 3. Predictive Intelligence
- **Deal Close Probability**: High-accuracy stacking ensemble (XGBoost + RandomForest) predicting won/lost status.
- **Revenue Forecasting**: 90-day time-series projections using Prophet.
- **Explainable AI**: SHAP importance plots reveal the drivers behind every prediction.

### 4. Interactive Command Center (Streamlit)
- **Executive KPI Page**: Total pipeline value, win rates, and MoM growth tracking.
- **Product & Channel Insights**: Granular drill-down into regional performance.
- **Stakeholder Collaboration**: Built-in review module for Sales Ops, Finance, and IT to flag and resolve data issues.

### 5. Automated Reporting & Integrity
- **Daily Summaries**: Automated generation of Executive PDF reports and Excel data extracts.
- **Data Quality Scorecard**: anomaly detection using Z-score and automated structural validation.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd "B2B Sales Channel and IT Channel Ecosystem Analysis"

# Install dependencies
pip install -r requirements.txt
```

### Running the Platform
```bash
# Initialize DB and run the first ingestion cycle
python3 scripts/utils/db_setup.py
python3 scripts/ingestion/pipeline_orchestrator.py

# Launch the Dashboard
streamlit run scripts/dashboard.py
```

## 📂 Project Structure
- `scripts/`: Implementation logic (Ingestion, EDA, ML, Dashboard).
- `data/`: SQLite database and processed team exports.
- `models/`: Trained `.pkl` model files.
- `reports/`: Automated PDF/Excel reports and EDA visualizations.
- `logs/`: Application and system health logs.

## 📈 Success Metrics
- **Forecasting Accuracy**: ≥ 85% on deal closure predictions.
- **Automation**: 100% reduction in manual reporting time for standard executive summaries.
- **Integrity**: ≥ 98% Data Quality Score across all ingested records.

---
*Built with ❤️ for the Google Antigravity Intelligence Team.*
