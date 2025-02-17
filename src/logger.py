import logging
import os

# Create logs directory if it doesn't exist
LOG_DIR = "../logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
LOG_FILE = os.path.join(LOG_DIR, "solis_api.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a"),  # Log to file
    ],
)

# Get logger
logger = logging.getLogger(__name__)
