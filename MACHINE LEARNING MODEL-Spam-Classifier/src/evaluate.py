"""
Module: evaluate.py
Description: Comprehensive model evaluation metrics and visualizations.
"""

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, classification_report, confusion_matrix, roc_curve
)

def evaluate_model_performance(model, X_test, y_test) -> dict:
    """Computes comprehensive evaluation metrics and renders plots."""
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1_score': f1_score(y_test, y_pred),
        'roc_auc': roc_auc_score(y_test, y_proba)
    }
    
    print("--- Classification Report ---")
    print(classification_report(y_test, y_pred, target_names=['Legitimate (0)', 'Spam (1)']))
    
    # Plotting Confusion Matrix and ROC Curve
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt='d', cmap='Blues', cbar=False, ax=axes[0],
                xticklabels=['Pred: Legitimate', 'Pred: Spam'], yticklabels=['Actual: Legitimate', 'Actual: Spam'])
    axes[0].set_title('Confusion Matrix Heatmap', fontweight='bold')
    
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    axes[1].plot(fpr, tpr, color='#2b5c8f', lw=2, label=f'ROC Curve (AUC = {metrics["roc_auc"]:.4f})')
    axes[1].plot([0, 1], [0, 1], color='gray', linestyle='--')
    axes[1].set_title('ROC Curve', fontweight='bold')
    axes[1].legend(loc='lower right')
    
    plt.tight_layout()
    plt.show()
    
    return metrics