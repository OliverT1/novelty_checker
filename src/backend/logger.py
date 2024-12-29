import logging
import sys
from backend.config import get_settings

settings = get_settings()

# Create logger
logger = logging.getLogger("novelty_checker")
logger.setLevel(getattr(logging, settings.LOG_LEVEL))

# Create console handler and set level
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))

# Create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add formatter to console handler
console_handler.setFormatter(formatter)

# Add console handler to logger
logger.addHandler(console_handler) 