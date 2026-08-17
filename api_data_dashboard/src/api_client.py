"""
API Client Module
Handles robust HTTP requests with timeout, status verification, and retry logic.
"""

import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

class WeatherAPIClient:
    """Client for securely fetching meteorological time-series data."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = self._create_resilient_session()

    @staticmethod
    def _create_resilient_session() -> requests.Session:
        """Configures requests session with automated exponential backoff retries."""
        session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            raise_on_status=False
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def fetch_hourly_forecast(self, latitude: float, longitude: float, metrics: str, days: int) -> dict:
        """Fetches live meteorological data from the Open-Meteo endpoint.

        Args:
            latitude (float): Target location latitude.
            longitude (float): Target location longitude.
            metrics (str): Comma-separated list of hourly metrics.
            days (int): Number of forecast days.

        Returns:
            dict: Parsed JSON response payload.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": metrics,
            "forecast_days": days
        }
        
        logger.info("Initiating API request to endpoint: %s", self.base_url)
        try:
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            logger.info("Successfully retrieved payload from API.")
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            logger.error("HTTP error encountered: %s", http_err)
            raise
        except requests.exceptions.ConnectionError as conn_err:
            logger.error("Network connection failure: %s", conn_err)
            raise
        except requests.exceptions.Timeout as timeout_err:
            logger.error("Request timed out: %s", timeout_err)
            raise
        except ValueError as json_err:
            logger.error("Failed to parse JSON response: %s", json_err)
            raise