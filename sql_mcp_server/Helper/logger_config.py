# Helper/logger_config.py
import logging
import os

LOG_FILE_PATH = "logs/app.log"
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

logger = logging.getLogger("sql_agent")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

file_handler = logging.FileHandler(LOG_FILE_PATH, mode="a")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
