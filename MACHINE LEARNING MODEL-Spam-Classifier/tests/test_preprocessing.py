"""
Module: test_preprocessing.py
Description: Unit tests for linguistic feature extraction pipeline.
"""

import pandas as pd
from src.preprocessing import extract_linguistic_features

def test_extract_linguistic_features():
    sample_df = pd.DataFrame({'text': ["URGENT CLICK NOW", "Hello Vikas"]})
    processed_df = extract_linguistic_features(sample_df)
    
    assert 'char_count' in processed_df.columns
    assert 'uppercase_ratio' in processed_df.columns
    assert processed_df.loc[0, 'uppercase_ratio'] > processed_df.loc[1, 'uppercase_ratio']
    print("Preprocessing unit tests passed successfully!")