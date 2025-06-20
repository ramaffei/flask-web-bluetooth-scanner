import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Nivel global

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
