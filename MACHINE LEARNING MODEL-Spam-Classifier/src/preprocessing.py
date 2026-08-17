"""
Module: preprocessing.py
Description: Feature engineering and linguistic attribute extraction.
"""

import re
import pandas as pd

def extract_linguistic_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extracts structural metadata features from raw text strings."""
    df_processed = df.copy()
    
    df_processed['char_count'] = df_processed['text'].apply(len)
    df_processed['word_count'] = df_processed['text'].apply(lambda x: len(x.split()))
    df_processed['uppercase_ratio'] = df_processed['text'].apply(
        lambda x: sum(1 for c in x if c.isupper()) / (len(x) + 1)
    )
    df_processed['has_url'] = df_processed['text'].apply(
        lambda x: 1 if re.search(r'http[s]?://|www\.', x) else 0
    )
    
    return df_processed