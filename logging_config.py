import sys

from loguru import logger


# Configure logging
def setup_logging():
    logger.remove()
    # Add a sink that logs to the console
    logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")

    # Add other sinks (e.g., file logging) as needed:
    # logger.add("heartbeat.log", rotation="1 MB")  # Log to a file with 1MB rotation
