import logging, os
from logging.handlers import TimedRotatingFileHandler


def logger_config(
    module: str = "default", 
    log_file: str = "./logs/app.log", 
    log_level: int = logging.DEBUG, 
    console: bool = False,
    when: str = "midnight", 
    interval: int = 1,
    backup_count: int = 7
):
    """
    Configures a logger with daily rotation settings.
    
    Args:
        module (str): Name of the module using the logger (e.g., __name__).
        log_file (str): Path to the log file.
        log_level (int): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        console (bool): Whether to enable console logging.
        when (str): Specifies the type of time interval for rotation (e.g., 'midnight').
        interval (int): Number of intervals between rotations.
        backup_count (int): Number of backup files to keep.

    Returns:
        logging.Logger: Configured logger object.
    """
    # Ensure the directory for log files exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Define formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Create or get the logger
    custom_logger = logging.getLogger(module)
    custom_logger.setLevel(log_level)

    # Avoid adding duplicate handlers
    if not custom_logger.handlers:
        # Timed rotating file handler
        rotating_handler = TimedRotatingFileHandler(
            log_file, when=when, interval=interval, backupCount=backup_count
        )
        rotating_handler.setFormatter(formatter)
        custom_logger.addHandler(rotating_handler)

        # Console handler (optional)
        if console:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            custom_logger.addHandler(console_handler)

    # Prevent propagation to the root logger
    custom_logger.propagate = False

    return custom_logger


# Example Usage
if __name__ == "__main__":
    logger = logger_config(
        __name__,
        log_file="./logs/app.log",
        log_level=logging.INFO,
        when="midnight",  # Rotate logs at midnight
        backup_count=30   # Keep 30 days of logs
    )
    logger.info("This is an info message.")
    logger.error("This is an error message.")
