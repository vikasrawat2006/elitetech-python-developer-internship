import yaml
import os
from modules.logger import setup_logger

logger = setup_logger()

class ConfigLoader:
    def __init__(self, config_path="config/report_config.yaml"):
        self.config_path = config_path

    def load_config(self):
        if not os.path.exists(self.config_path):
            logger.error(f"Configuration file not found at {self.config_path}")
            raise FileNotFoundError(f"Missing config file: {self.config_path}")
            
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            logger.info("Configuration file successfully loaded.")
            return config