import pandas as pd
from modules.validator import DataValidator
from modules.logger import setup_logger

logger = setup_logger()

class DataTransformer:
    def __init__(self, csv_path):
        self.csv_path = csv_path

    def process(self):
        logger.info(f"Ingesting raw data stream from {self.csv_path}")
        df = pd.read_csv(self.csv_path)
        
        # Validate data schema
        DataValidator.validate_schema(df)
        
        # Feature Engineering & Analytics
        df["Performance_Ratio"] = (df["Actual_Value"] / df["Target_Value"]) * 100
        df["Variance"] = df["Actual_Value"] - df["Target_Value"]
        
        def assign_status(ratio):
            if ratio >= 100:
                return "Exceeded"
            elif ratio >= 90:
                return "Optimal"
            else:
                return "Warning"
                
        df["Status"] = df["Performance_Ratio"].apply(assign_status)
        logger.info("Data transformation and KPI computations completed.")
        return df