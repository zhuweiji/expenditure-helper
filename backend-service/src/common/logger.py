import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(
    name: str,
    log_file: str = "app.log",
    max_bytes: int = 10485760,
    backup_count: int = 5,
) -> logging.Logger:
    """
    Get a logger that writes to both file (with rotation) and console.

    Args:
        name: Logger name (typically __name__)
        log_file: Path to log file (default: app.log)
        max_bytes: Maximum file size before rotation (default: 10MB)
        backup_count: Number of backup files to keep (default: 5)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only add handlers if they haven't been added yet
    if not logger.handlers:
        logger.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter("%(name)s-%(levelname)s|%(lineno)d:  %(message)s")

        # File handler with rotation
        os.makedirs(
            os.path.dirname(log_file) if os.path.dirname(log_file) else ".",
            exist_ok=True,
        )
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger
