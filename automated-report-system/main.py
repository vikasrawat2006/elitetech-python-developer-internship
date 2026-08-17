import argparse
import os
import pandas as pd
from modules.config_loader import ConfigLoader
from modules.transformer import DataTransformer
from modules.charts import ChartGenerator
from modules.pdf_builder import PDFReportBuilder
from modules.logger import setup_logger

logger = setup_logger()

def seed_sample_data(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Check if file doesn't exist OR is completely empty (0 bytes)
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        data = {
            "Department": ["Engineering", "Engineering", "Marketing", "Marketing", "Sales", "Sales", "Operations", "Operations"],
            "Metric_Name": ["Server Uptime", "Bug Resolution", "Campaign Reach", "Conversion Rate", "Q1 Revenue", "Client Retention", "Supply Efficiency", "Logistics Cost"],
            "Target_Value": [99.9, 95.0, 50000, 3.5, 120000, 90.0, 98.0, 15000],
            "Actual_Value": [99.85, 96.2, 54200, 3.2, 128500, 91.5, 97.5, 14200]
        }
        pd.DataFrame(data).to_csv(path, index=False)
        logger.info(f"Seeded sample CSV input at {path}")

def main():
    parser = argparse.ArgumentParser(description="Enterprise Automated Report Generation Pipeline")
    parser.add_argument("--input", default="data/raw/business_metrics.csv", help="Path to input raw CSV file")
    parser.add_argument("--output", default="exports/Enterprise_Report.pdf", help="Path to output PDF file")
    args = parser.parse_args()

    logger.info("==========================================")
    logger.info("=== STARTING REPORT GENERATION PIPELINE ===")
    logger.info("==========================================")

    # 1. Initialize Seed Data if missing
    seed_sample_data(args.input)

    # 2. Load Configuration Settings
    config_loader = ConfigLoader()
    config = config_loader.load_config()

    # 3. Data Transformation & Analytics
    transformer = DataTransformer(args.input)
    df = transformer.process()

    # 4. Generate Visual Chart Assets
    chart_path = ChartGenerator.generate_bar_chart(df)

    # 5. Build Enterprise PDF Document
    pdf_builder = PDFReportBuilder(config, df, chart_path, args.output)
    pdf_builder.build()

    logger.info("==========================================")
    logger.info("=== PIPELINE EXECUTED SUCCESSFULLY =======")
    logger.info("==========================================")

if __name__ == "__main__":
    main()