import logging

# Set up logger
logger = logging.getLogger("myapp")  # Naming the logger for clarity
logger.setLevel(logging.INFO)  # Can adjust this globally

# You can use StreamHandler for console output or FileHandler for file logging
ch = logging.StreamHandler()  # Console output
ch.setLevel(logging.INFO)

# If you want to log to a file as well, you can use:
# fh = logging.FileHandler("app.log")
# fh.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(ch)

# Optionally, add a file handler as well
# logger.addHandler(fh)

# You can also create a function to return the logger if needed
def get_logger():
    return logger
