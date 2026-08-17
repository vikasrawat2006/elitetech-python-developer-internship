"""
Module: train.py
Description: Multi-model benchmarking and hyperparameter optimization functions.
"""

import logging
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, GridSearchCV, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC

logger = logging.getLogger("EnterpriseML_Pipeline")

def benchmark_models(X_train, y_train) -> dict:
    """Benchmarks multiple candidate classifiers using stratified cross-validation."""
    models = {
        'Naive Bayes': MultinomialNB(),
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'Linear SVM': LinearSVC(random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42)
    }
    
    cv_results = {}
    cv_strategy = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for name, model in models.items():
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1, 2))),
            ('clf', model)
        ])
        scores = cross_val_score(pipeline, X_train, y_train, cv=cv_strategy, scoring='f1', n_jobs=-1)
        cv_results[name] = {'Mean F1': scores.mean(), 'Std F1': scores.std()}
        logger.info(f"Model Benchmarked -> {name}: Mean F1-Score = {scores.mean():.4f}")
        
    return cv_results

def optimize_hyperparameters(X_train, y_train):
    """Executes GridSearchCV to find optimal hyperparameters for Logistic Regression."""
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english')),
        ('clf', LogisticRegression(random_state=42, max_iter=1000))
    ])
    
    param_grid = {
        'tfidf__max_df': [0.85, 0.95, 1.0],
        'tfidf__ngram_range': [(1, 1), (1, 2)],
        'tfidf__sublinear_tf': [True, False],
        'clf__C': [0.1, 1.0, 5.0, 10.0],
        'clf__solver': ['liblinear', 'lbfgs']
    }
    
    grid_search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
        scoring='f1',
        n_jobs=-1
    )
    
    grid_search.fit(X_train, y_train)
    logger.info(f"Optimal Hyperparameters: {grid_search.best_params_}")
    return grid_search.best_estimator_