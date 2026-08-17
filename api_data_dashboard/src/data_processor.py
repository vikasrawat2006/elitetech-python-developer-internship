"""
Data Processor Module
Cleans raw JSON responses, handles missing values, and constructs Pandas DataFrames.
"""

import logging
import pandas as pd

logger = logging.getLogger(__name__)

class DataProcessor:
    """Handles data transformation and statistical aggregation."""

    @staticmethod
    def process_raw_forecast(raw_data: dict) -> pd.DataFrame:
        """Converts raw JSON payload into a structured Pandas DataFrame with derived features.

        Args:
            raw_data (dict): Raw dictionary returned from API.

        Returns:
            pd.DataFrame: Cleaned and structured time-series dataframe.
        """
        logger.info("Starting data wrangling and feature engineering...")
        try:
            hourly_data = raw_data.get("hourly", {})
            
            df = pd.DataFrame({
                "timestamp": pd.to_datetime(hourly_data.get("time")),
                "temperature": hourly_data.get("temperature_2m"),
                "humidity": hourly_data.get("relative_humidity_2m"),
                "wind_speed": hourly_data.get("wind_speed_10m"),
                "precipitation": hourly_data.get("precipitation")
            })

            # Data cleaning: handle nulls
            initial_count = len(df)
            df.dropna(inplace=True)
            dropped_count = initial_count - len(df)
            if dropped_count > 0:
                logger.warning("Dropped %d rows containing missing values.", dropped_count)

            # Feature Engineering: Add temperature rolling average (smoothed trend)
            df["temp_rolling_avg"] = df["temperature"].rolling(window=3, min_periods=1).mean()

            logger.info("Dataframe successfully processed. Total rows: %d", len(df))
            return df

        except Exception as err:
            logger.error("Error occurred during data processing: %s", err)
            raise

    @staticmethod
    def generate_statistical_summary(df: pd.DataFrame) -> dict:
        """Computes comprehensive analytical metrics for reporting."""
        summary = {
            "total_records": len(df),
            "mean_temp": df["temperature"].mean(),
            "max_temp": df["temperature"].max(),
            "min_temp": df["temperature"].min(),
            "mean_humidity": df["humidity"].mean(),
            "mean_wind_speed": df["wind_speed"].mean(),
            "max_wind_speed": df["wind_speed"].max(),
            "total_precipitation": df["precipitation"].sum()
        }
        return summary