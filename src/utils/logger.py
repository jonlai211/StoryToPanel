import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging():
    # Determine the project root directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    # Define the path to the log file
    log_file = os.path.join(project_root, 'mj.log')

    # Create a root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the root logging level to INFO

    # Avoid adding multiple handlers if setup_logging is called multiple times
    if not logger.handlers:
        # Create a file handler with rotation
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=2)
        file_handler.setLevel(logging.INFO)

        # Create a console handler for real-time feedback
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Define a common log format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers to the root logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
