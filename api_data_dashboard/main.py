"""
Main Application Orchestrator
Coordinates API data ingestion, processing pipelines, statistical logging, and dashboard generation.
"""

import sys
import logging
from config.settings import (
    API_BASE_URL, DEFAULT_LATITUDE, DEFAULT_LONGITUDE,
    HOURLY_METRICS, FORECAST_DAYS, OUTPUT_IMAGE_PATH, LOG_FILE_PATH
)
from src.api_client import WeatherAPIClient
from src.data_processor import DataProcessor
from src.visualizer import DashboardVisualizer

# Configure dual logging (Console + File output)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    ]
)
logger = logging.getLogger("MainOrchestrator")


def print_summary_report(stats: dict) -> None:
    """Prints a neatly formatted professional console analytics report."""
    print("\n" + "=" * 60)
    print("               METEOROLOGICAL ANALYTICAL REPORT               ")
    print("=" * 60)
    print(f"• Total Hourly Samples Processed : {stats['total_records']}")
    print(f"• Mean Ambient Temperature       : {stats['mean_temp']:.2f} °C")
    print(f"• Maximum Peak Temperature       : {stats['max_temp']:.2f} °C")
    print(f"• Minimum Recorded Temperature   : {stats['min_temp']:.2f} °C")
    print(f"• Average Relative Humidity      : {stats['mean_humidity']:.2f} %")
    print(f"• Mean Wind Speed                : {stats['mean_wind_speed']:.2f} km/h")
    print(f"• Peak Wind Velocity             : {stats['max_wind_speed']:.2f} km/h")
    print(f"• Total Precipitation            : {stats['total_precipitation']:.2f} mm")
    print("=" * 60 + "\n")


def main():
    """Execution entry point."""
    logger.info("Starting API Integration and Data Visualization Pipeline...")
    
    try:
        # Step 1: Ingest Data
        client = WeatherAPIClient(API_BASE_URL)
        raw_data = client.fetch_hourly_forecast(
            DEFAULT_LATITUDE, DEFAULT_LONGITUDE, HOURLY_METRICS, FORECAST_DAYS
        )

        # Step 2: Process Data & Feature Engineering
        processor = DataProcessor()
        df = processor.process_raw_forecast(raw_data)
        stats = processor.generate_statistical_summary(df)

        # Step 3: Render Visualization Dashboard
        DashboardVisualizer.render_and_save(df, OUTPUT_IMAGE_PATH)

        # Step 4: Output Console Summary
        print_summary_report(stats)
        logger.info("Pipeline executed successfully from end to end.")

    except Exception as e:
        logger.critical("Pipeline failed due to unhandled exception: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()