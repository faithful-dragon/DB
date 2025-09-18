import logging
import os

# Log file path
LOG_FILE_PATH = "logs/app.log"

# Ensure the directory exists
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

# Create logger
logger = logging.getLogger("my_app_logger")
logger.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

# Console handler (optional)
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler(LOG_FILE_PATH, mode="a")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
