import logging
import os
from logging.handlers import RotatingFileHandler

_logging_configured = False


def configure_logging(
    log_file: str = "app.log",
    log_level: str = "INFO",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 5,
    log_dir: str = "logs",
):
    """Configure application-wide logging with clean format."""
    global _logging_configured

    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)-30s | %(message)s", datefmt="%H:%M:%S")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)
    logging.getLogger("huggingface_hub").setLevel(logging.WARNING)
    logging.getLogger("streamlit").setLevel(logging.ERROR)
    logging.getLogger("watchfiles").setLevel(logging.WARNING)

    if not _logging_configured:
        root_logger.info(f"Logging configured | Level: {log_level} | File: {log_path}")
        _logging_configured = True


if __name__ == "__main__":
    configure_logging(log_file="test_app.log", log_level="DEBUG")
    logger = logging.getLogger(__name__)
    logger.debug("This is a debug message from logging_config.py")
    logger.info("This is an info message from logging_config.py")
    logger.warning("This is a warning message from logging_config.py")
    logger.error("This is an error message from logging_config.py")
