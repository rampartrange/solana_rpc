from time import time
import logging
import sys


def now_ms():
    return int(time() * 1000)


def init_logger(name):
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)  # Stream logs to stdout
        ]
    )
    logger = logging.getLogger(name)
    return logger

