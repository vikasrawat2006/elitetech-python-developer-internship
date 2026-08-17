"""
Module: data_ingestion.py
Author: Vikas Rawat (Internship Track: Machine Learning & MLOps)
Description: Ingests and validates the enterprise text classification dataset.
"""

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger("EnterpriseML_Pipeline")

def generate_enterprise_corpus(num_samples: int = 2500, random_state: int = 42) -> pd.DataFrame:
    """Simulates an enterprise-grade text corpus with realistic noise and class imbalance."""
    np.random.seed(random_state)
    
    spam_templates = [
        "Congratulations! You've been selected for a free ${amount} gift card. Claim now at {url}",
        "URGENT: Your corporate enterprise subscription payment failed. Update credentials immediately: {url}",
        "Earn ${amount} weekly working from home with zero coding experience! Text 'START' to {phone}",
        "Win an exclusive luxury vacation package to Maldives! Call toll-free {phone} right now.",
        "Exclusive promotional discount code for your enterprise tier upgrade: SAVE{discount}! Claim today.",
        "ALERT: Suspicious login attempt detected on your corporate gateway. Verify identity: {url}",
        "Claim your unclaimed crypto assets worth ${amount} before expiration! Visit {url}"
    ]
    
    ham_templates = [
        "Hi Vikas, are we reviewing the system architecture documents for project '{project}' at {time} today?",
        "Please find attached the quarterly database performance audit report for sprint review.",
        "Could you push the updated React component patch and unit tests to our GitHub repository?",
        "Reminder: The weekly synchronization call with the DevOps squad is scheduled for {time}.",
        "Let's grab coffee after wrapping up the final backend API sprint deliverables.",
        "Can you help me debug this Node.js async/await error in the user authentication module?",
        "The pull request for feature branch '{project}' has been approved and merged successfully."
    ]
    
    projects = ["AlphaSync", "NexusCloud", "DataPulse", "SecureGate", "CoreAPI"]
    urls = ["http://bit.ly/secure-verify", "http://update-login-portal.com", "http://claim-reward-now.net"]
    phones = ["1-800-555-0199", "1-888-444-1234"]
    
    corpus, labels = [], []
    
    for _ in range(num_samples // 2):
        # Generate Spam (1)
        template = np.random.choice(spam_templates)
        text = template.format(
            amount=np.random.choice([500, 1000, 5000, 10000]),
            url=np.random.choice(urls),
            phone=np.random.choice(phones),
            discount=np.random.choice([20, 50, 75])
        )
        corpus.append(text)
        labels.append(1)
        
        # Generate Ham (0)
        template_ham = np.random.choice(ham_templates)
        text_ham = template_ham.format(
            project=np.random.choice(projects),
            time=np.random.choice(["2 PM", "3:30 PM", "10 AM", "4:15 PM"])
        )
        corpus.append(text_ham)
        labels.append(0)
        
    df = pd.DataFrame({'text': corpus, 'label': labels})
    df = df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    
    # Rigorous schema validation
    assert 'text' in df.columns and 'label' in df.columns, "Schema validation failed!"
    assert df.isnull().sum().sum() == 0, "Null values detected in ingestion pipeline!"
    
    logger.info(f"Ingestion successful. Total records: {len(df)}")
    return df