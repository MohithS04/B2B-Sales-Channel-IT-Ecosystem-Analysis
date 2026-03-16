import pandas as pd
import numpy as np
import sqlite3
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.ensemble import StackingClassifier, StackingRegressor, RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, mean_absolute_error, mean_squared_error
from xgboost import XGBClassifier, XGBRegressor
from prophet import Prophet
import joblib
import shap
import matplotlib.pyplot as plt
import os

DB_PATH = "data/antigravity.db"
MODEL_PATH = "models"
os.makedirs(MODEL_PATH, exist_ok=True)

def load_and_preprocess():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM transactions", conn)
    trends_df = pd.read_sql_query("SELECT * FROM market_trends", conn)
    econ_df = pd.read_sql_query("SELECT * FROM economic_indicators", conn)
    conn.close()
    
    # Feature Engineering
    df['target_win'] = df['sales_stage'].apply(lambda x: 1 if x == 'Closed Won' else 0)
    
    # Simple market trend index (mean of interest score)
    avg_trend = trends_df['interest_score'].mean() if not trends_df.empty else 50
    df['market_trend_index'] = avg_trend
    
    # One-hot encoding for categoricals
    categorical_cols = ['region', 'product', 'channel_type']
    df_encoded = pd.get_dummies(df, columns=categorical_cols)
    
    # Drop unnecessary columns
    drop_cols = ['transaction_id', 'customer_id', 'sales_stage', 'rep_id', 'close_date', 'timestamp']
    df_final = df_encoded.drop(columns=drop_cols)
    
    return df_final, df[['close_date', 'deal_value']]

def train_classification_model(df):
    print("Training Classification Models (Deal Close Probability)...")
    X = df.drop(columns=['target_win', 'deal_value'])
    y = df['target_win']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Baseline: Logistic Regression
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_train, y_train)
    lr_preds = lr.predict(X_test)
    print(f"Logistic Regression Accuracy: {accuracy_score(y_test, lr_preds):.4f}")
    
    # Advanced: XGBoost
    xgb = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    xgb.fit(X_train, y_train)
    xgb_preds = xgb.predict(X_test)
    print(f"XGBoost Accuracy: {accuracy_score(y_test, xgb_preds):.4f}")
    
    # Ensemble: Stacking
    estimators = [
        ('rf', RandomForestClassifier(n_estimators=10, random_state=42)),
        ('xgb', XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42))
    ]
    clf = StackingClassifier(estimators=estimators, final_estimator=LogisticRegression())
    clf.fit(X_train, y_train)
    clf_preds = clf.predict(X_test)
    print(f"Stacking Ensemble Accuracy: {accuracy_score(y_test, clf_preds):.4f}")
    
    # Save best model
    joblib.dump(clf, f"{MODEL_PATH}/deal_close_model.pkl")
    
    # SHAP Explainability
    print("Generating SHAP plots...")
    explainer = shap.Explainer(xgb) # SHAP works best with XGB native
    shap_values = explainer(X_test)
    plt.figure()
    shap.summary_plot(shap_values, X_test, show=False)
    plt.savefig("reports/eda_plots/shap_importance.png")
    plt.close()

def train_time_series_forecast(df_ts):
    print("Training Time Series Revenue Forecast (Prophet)...")
    df_ts.columns = ['ds', 'y']
    df_ts['ds'] = pd.to_datetime(df_ts['ds'])
    
    # Daily aggregation
    df_ts = df_ts.groupby('ds').sum().reset_index()
    
    model = Prophet(yearly_seasonality=True, daily_seasonality=False)
    model.fit(df_ts)
    
    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)
    
    # Save prophet model
    joblib.dump(model, f"{MODEL_PATH}/revenue_forecast_model.pkl")
    
    # Save forecast results for dashboard
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_csv("data/processed/revenue_forecast.csv", index=False)
    print("Prophet forecast saved.")

def main():
    df, df_ts = load_and_preprocess()
    train_classification_model(df)
    train_time_series_forecast(df_ts)
    print("Modeling phase complete. Models saved in models/")

if __name__ == "__main__":
    main()
