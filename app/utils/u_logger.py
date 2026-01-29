import logging


def logger_config(module, log_file="app.log"):
    """
    Logger function. Extends Python loggin module and set a custom config.
    params: 
        Module Name. e.i: logger_config(__name__).
        log_file (str): Path to the log file.
    return: 
        Custom logger_config Object.
    """
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)    

    custom_logger = logging.getLogger(module)
    custom_logger.setLevel(logging.DEBUG)

    custom_logger.addHandler(file_handler)

    return custom_logger
