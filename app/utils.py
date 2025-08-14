import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logger():
    """Set up the logger for the application."""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    handler = RotatingFileHandler('logs/app.log', maxBytes=1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger

logger = setup_logger()
