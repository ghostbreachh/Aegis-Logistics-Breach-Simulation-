#!/usr/bin/env python3
"""
Qilin_Extortion_Predictor.py

Machine Learning and Data Visualization pipeline. Trains a Random Forest
Classifier on synthetic Threat Intel data to identify which attributes
drive victims to pay Qilin data extortion demands.

Author: GHOST BREACH Threat Labs (Data Science Node)
"""

import pandas as pd
import numpy as np
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

# Configure Logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_and_preprocess(file_path: str) -> tuple:
    """Loads CSV data and preprocesses categorical variables."""
    try:
        df = pd.read_csv(file_path)
        logger.info(f"Successfully loaded {len(df)} records from {file_path}")
    except FileNotFoundError:
        logger.error(f"Data file {file_path} not found. Run the generator script first.")
        raise

    # Drop non-predictive ID column
    df = df.drop(columns=['Incident_ID'])

    # Encode categorical variables
    encoders = {}
    for col in ['Industry', 'Regulatory_Region']:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    X = df.drop(columns=['Paid_Ransom'])
    y = df['Paid_Ransom']

    return train_test_split(X, y, test_size=0.25, random_state=42), X.columns, encoders

def train_and_evaluate(X_train, X_test, y_train, y_test) -> RandomForestClassifier:
    """Trains the Random Forest model and outputs performance metrics."""
    logger.info("Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    logger.info("\n--- Classification Report ---")
    print(classification_report(y_test, y_pred))

    logger.info("\n--- Confusion Matrix ---")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)
    
    return model

def visualize_threat_landscape(model, feature_names, original_csv_path: str):
    """Generates a dark-mode visualization of cartel economics."""
    logger.info("Generating threat landscape visualization...")
    
    # Configure dark theme for cyber aesthetic
    plt.style.use('dark_background')
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.patch.set_facecolor('#0d1117')
    
    # Subplot 1: Feature Importance
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    sns.barplot(
        x=importances[indices], 
        y=[feature_names[i] for i in indices], 
        ax=axes[0], 
        palette='magma'
    )
    axes[0].set_title('Extortion Leverage: Predictive Feature Importance', color='#00ff9f', pad=15)
    axes[0].set_xlabel('Relative Importance (Gini)', color='#c9d1d9')
    axes[0].set_ylabel('Features', color='#c9d1d9')
    axes[0].tick_params(colors='#c9d1d9')
    
    # Subplot 2: Payment Rates by Industry
    raw_df = pd.read_csv(original_csv_path)
    payment_rates = raw_df.groupby('Industry')['Paid_Ransom'].mean().sort_values(ascending=False)
    
    sns.barplot(
        x=payment_rates.values, 
        y=payment_rates.index, 
        ax=axes[1], 
        palette='viridis'
    )
    axes[1].set_title('Extortion Capitulation: Payment Probability by Industry', color='#00ff9f', pad=15)
    axes[1].set_xlabel('Probability of Paying Ransom Demand', color='#c9d1d9')
    axes[1].set_ylabel('Industry Sector', color='#c9d1d9')
    axes[1].tick_params(colors='#c9d1d9')

    plt.tight_layout()
    plt.savefig('Qilin_Extortion_Landscape.png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    logger.info("Visualization saved as 'Qilin_Extortion_Landscape.png'.")

if __name__ == "__main__":
    csv_file = "qilin_campaign_data.csv"
    (X_train, X_test, y_train, y_test), features, _ = load_and_preprocess(csv_file)
    rf_model = train_and_evaluate(X_train, X_test, y_train, y_test)
    visualize_threat_landscape(rf_model, features, csv_file)
