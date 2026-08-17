import os
import logging

def setup_enterprise_logger(log_dir: str = "logs", level: str = "DEBUG") -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "session_audit.log")

    logger = logging.getLogger("VREnterpriseLogger")
    numeric_level = getattr(logging, level.upper(), logging.DEBUG)
    logger.setLevel(numeric_level)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(numeric_level)
        formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | [%(filename)s:%(lineno)d] | %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger