# core/utils/logger.py

import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("LOG_FILE", "quantumbotx.log")

# Formatter gaya cinta coding 😘
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')

# File handler
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(formatter)

# Stream (console) handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Logger utama
logger = logging.getLogger("QuantumBotX")
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.propagate = False
