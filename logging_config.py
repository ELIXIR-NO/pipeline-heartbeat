import sys

from loguru import logger

from config import Config


# Configure logging
def setup_logging():
    logger.remove()
    print(f"Log level is set to {Config.LOG_LEVEL}")
    # Add a sink that logs to the console
    logger.add(sys.stdout, format="{time} {level} {message}", level=Config.LOG_LEVEL)

    # Add other sinks (e.g., file logging) as needed:
    # logger.add("heartbeat.log", rotation="1 MB")  # Log to a file with 1MB rotation
