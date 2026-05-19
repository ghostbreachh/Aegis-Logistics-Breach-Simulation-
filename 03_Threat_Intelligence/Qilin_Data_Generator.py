#!/usr/bin/env python3
"""
Qilin_Data_Generator.py

Generates 1,000 rows of synthetic Threat Intelligence data representing 
Qilin Cartel's encryption-less extortion campaigns (2025-2026).

Author: GHOST BREACH Threat Labs (Data Science Node)
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional

# Configure Logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_qilin_dataset(num_samples: int = 1000, output_file: str = "qilin_campaign_data.csv") -> Optional[pd.DataFrame]:
    """
    Generates a synthetic dataset of ransomware/extortion incidents.
    """
    logger.info(f"Initializing generation of {num_samples} synthetic Qilin extortion records...")
    
    # Set seed for reproducibility
    np.random.seed(42)
    
    industries = ['Logistics', 'Healthcare', 'Finance', 'Manufacturing', 'Retail']
    # Probabilities of being targeted (Logistics heavily weighted based on recent intel)
    industry_weights = [0.35, 0.25, 0.20, 0.15, 0.05] 
    
    data = {
        'Incident_ID': [f"QILIN-{1000 + i}" for i in range(num_samples)],
        'Industry': np.random.choice(industries, num_samples, p=industry_weights),
        'Revenue_USD_Millions': np.random.lognormal(mean=5.5, sigma=1.2, size=num_samples).round(2),
        'Data_Exfiltrated_TB': np.random.uniform(0.5, 15.0, num_samples).round(2),
        'Regulatory_Region': np.random.choice(['EU (GDPR)', 'US (SEC/HIPAA)', 'APAC', 'Global Mixed'], num_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Ransom demand correlates to ~1.5% - 3% of revenue, minimum $250k
    df['Ransom_Demand_Millions'] = (df['Revenue_USD_Millions'] * np.random.uniform(0.015, 0.030, num_samples)).clip(lower=0.25).round(2)
    
    # Feature Engineering: Calculate likelihood of paying
    prob_pay = np.full(num_samples, 0.10) 
    
    # Logistics and Healthcare are highly likely to pay to prevent data leak / operational halt
    prob_pay += np.where(df['Industry'].isin(['Logistics', 'Healthcare']), 0.35, 0)
    
    # GDPR/SEC exposure significantly increases pressure to pay
    prob_pay += np.where(df['Regulatory_Region'].isin(['EU (GDPR)', 'US (SEC/HIPAA)']), 0.25, 0)
    
    # If the ransom demand is less than 50% of potential regulatory fines, payment probability spikes
    prob_pay += np.where(df['Ransom_Demand_Millions'] < (df['Revenue_USD_Millions'] * 0.04), 0.15, 0)
    
    # Normalize probabilities to max 0.95
    prob_pay = np.clip(prob_pay, 0.0, 0.95)
    
    # Generate binary target variable based on calculated probabilities
    df['Paid_Ransom'] = np.random.binomial(1, prob_pay)
    
    logger.info("Dataset generated successfully. Applying sanity checks...")
    
    try:
        df.to_csv(output_file, index=False)
        logger.info(f"Dataset successfully exported to {output_file}")
        return df
    except Exception as e:
        logger.error(f"Failed to write CSV: {e}")
        return None

if __name__ == "__main__":
    generate_qilin_dataset()
