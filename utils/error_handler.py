import logging


# Function to log errors
def log_error(exception, message):
    logging.error(f"{exception}: {message}")
