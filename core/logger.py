import logging
import os
import sys

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

log_file_path = os.path.join(LOG_DIR, "dashboard.log")

logger = logging.getLogger("TalkativeDashboard")
logger.setLevel(logging.INFO)

if not logger.handlers:
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s [%(name)s:%(filename)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
