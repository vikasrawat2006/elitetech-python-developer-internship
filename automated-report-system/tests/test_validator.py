import pandas as pd
import pytest
from modules.validator import DataValidator

def test_validator_success():
    df = pd.DataFrame({
        "Department": ["IT"],
        "Metric_Name": ["Uptime"],
        "Target_Value": [99.9],
        "Actual_Value": [99.8]
    })
    assert DataValidator.validate_schema(df) is True

def test_validator_missing_column():
    df = pd.DataFrame({
        "Department": ["IT"],
        "Target_Value": [99.9]
    })
    with pytest.raises(ValueError):
        DataValidator.validate_schema(df)