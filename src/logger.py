import logging
import os

# Create logs directory if it doesn't exist
LOG_DIR = "../logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
LOG_FILE = os.path.join(LOG_DIR, "solis_api.log")

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler
file_handler = logging.FileHandler(LOG_FILE, mode="a")
file_handler.setLevel(logging.INFO)

# Create a formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s - %(tags)s")

# Add the formatter to the handler
file_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(file_handler)
