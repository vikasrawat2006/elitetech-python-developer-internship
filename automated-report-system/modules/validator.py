import pandas as pd
from modules.logger import setup_logger

logger = setup_logger()

class DataValidator:
    @staticmethod
    def validate_schema(df: pd.DataFrame) -> bool:
        required_columns = ["Department", "Metric_Name", "Target_Value", "Actual_Value"]
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Validation Error: Missing required column '{col}'")
                raise ValueError(f"Missing required dataset column: {col}")
        
        if df.empty:
            logger.error("Validation Error: Dataset is empty.")
            raise ValueError("Provided dataset contains no records.")
            
        logger.info("Data schema validation passed successfully.")
        return True