"""
Module: test_model.py
Description: Unit tests for model artifact integrity and inference consistency.
"""

import os
import joblib

def test_model_artifact_and_inference():
    model_path = '../models/enterprise_spam_classifier.pkl'
    
    # Check if model artifact exists
    assert os.path.exists(model_path), "Model artifact .pkl file not found in registry!"
    
    # Load model
    model = joblib.load(model_path)
    
    # Run test inference
    test_input = ["Congratulations! You've won a free vacation. Claim now at http://bit.ly/claim"]
    prediction = model.predict(test_input)
    probability = model.predict_proba(test_input)
    
    assert len(prediction) == 1, "Prediction output shape mismatch."
    assert probability.shape == (1, 2), "Probability output shape mismatch."
    assert prediction[0] in [0, 1], "Prediction label must be binary (0 or 1)."
    
    print("Model inference unit tests passed successfully!")