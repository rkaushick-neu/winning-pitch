import logging
import os
from logging.handlers import TimedRotatingFileHandler

# Create a logs folder if it doesn't exist
LOG_DIR = "./../data/logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str):
    """
    Returns a logger instance with:
    - Daily rotating log files
    - Retains last 7 days
    - Console + file output
    - Uniform format
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        log_file_path = os.path.join(LOG_DIR, f"{name}.log")

        # 🌀 Rotates daily and keeps 7 days of history
        rotating_handler = TimedRotatingFileHandler(
            log_file_path,
            when="midnight",   # rotate every midnight
            interval=1,        # every 1 day
            backupCount=7,     # keep 7 old log files
            encoding="utf-8"
        )

        console_handler = logging.StreamHandler()

        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        rotating_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(rotating_handler)
        logger.addHandler(console_handler)

    return logger