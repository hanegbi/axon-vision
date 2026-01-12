import logging
import os
import sys
from datetime import datetime
from logging.handlers import QueueHandler, QueueListener


def setup_logging(log_queue):
    """Setp logging to a file and console for multiprocessing.

    Args:
        log_queue: Multiprocessing queue for log messages.

    Returns:
        QueueListener
    """
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/run_{timestamp}.log"

    formatter = logging.Formatter(
        fmt="%(asctime)s - %(processName)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    listener = QueueListener(log_queue, file_handler, console_handler)
    return listener


def get_logger(name, log_queue):
    """Get a logger with a QueueHandler.

    Args:
        name: Logger name.
        log_queue: Multiprocessing queue for log messages.

    Returns:
        Logger configured with QueueHandler.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        queue_handler = QueueHandler(log_queue)
        logger.addHandler(queue_handler)

    return logger
