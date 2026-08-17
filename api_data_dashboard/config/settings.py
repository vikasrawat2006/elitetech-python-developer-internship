"""
Configuration module for API Integration and Data Visualization Project.
Handles API endpoints, coordinate parameters, and output paths.
"""

import os

# Base Directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# API Configuration
API_BASE_URL = "https://api.open-meteo.com/v1/forecast"
DEFAULT_LATITUDE = 51.5074   # London Latitude
DEFAULT_LONGITUDE = -0.1278  # London Longitude
HOURLY_METRICS = "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
FORECAST_DAYS = 1

# File Paths
DATA_DIR = os.path.join(BASE_DIR, "data")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

OUTPUT_IMAGE_PATH = os.path.join(DATA_DIR, "weather_dashboard.png")
LOG_FILE_PATH = os.path.join(LOGS_DIR, "app.log")