"""
Script: run_pipeline.py
Description: Master orchestrator script executing the end-to-end ML pipeline.
"""

import logging
import os
import joblib
from sklearn.model_selection import train_test_split

from src.data_ingestion import generate_enterprise_corpus
from src.preprocessing import extract_linguistic_features
from src.train import benchmark_models, optimize_hyperparameters
from src.evaluate import evaluate_model_performance

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("EnterpriseML_Master")

if __name__ == "__main__":
    logger.info("Starting Enterprise Machine Learning Pipeline Execution...")
    
    # Step 1: Data Ingestion
    df = generate_enterprise_corpus(num_samples=2500)
    
    # Step 2: Feature Engineering
    df_features = extract_linguistic_features(df)
    
    # Step 3: Train-Test Split
    X = df_features['text']
    y = df_features['label']
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    
    # Step 4: Benchmark Candidate Models
    benchmark_results = benchmark_models(X_train, y_train)
    
    # Step 5: Hyperparameter Tuning & Best Model Selection
    best_model = optimize_hyperparameters(X_train, y_train)
    
    # Step 6: Comprehensive Evaluation
    metrics = evaluate_model_performance(best_model, X_test, y_test)
    
    # Step 7: Model Artifact Serialization
    os.makedirs('models', exist_ok=True)
    model_path = 'models/enterprise_spam_classifier.pkl'
    joblib.dump(best_model, model_path)
    logger.info(f"Pipeline execution completed successfully. Artifact saved to {model_path}")