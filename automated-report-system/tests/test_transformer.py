import pandas as pd
import os
from modules.transformer import DataTransformer

def test_transformer_logic(tmp_path):
    csv_file = tmp_path / "test_metrics.csv"
    df_sample = pd.DataFrame({
        "Department": ["Sales"],
        "Metric_Name": ["Revenue"],
        "Target_Value": [100.0],
        "Actual_Value": [110.0]
    })
    df_sample.to_csv(csv_file, index=False)
    
    transformer = DataTransformer(str(csv_file))
    res_df = transformer.process()
    
    assert "Performance_Ratio" in res_df.columns
    assert res_df.loc[0, "Status"] == "Exceeded"