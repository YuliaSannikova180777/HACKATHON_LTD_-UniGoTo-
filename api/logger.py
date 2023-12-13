import logging

logging.basicConfig(level=logging.INFO)

def get_logger():
    return logging.getLogger(__name__)