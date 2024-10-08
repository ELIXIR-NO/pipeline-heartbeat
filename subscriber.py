import json

import redis
from loguru import logger

from config import Config
from logging_config import setup_logging
from models import Component

setup_logging()


# Establish connection to Redis
def connect_redis():
    try:
        client = redis.Redis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB)
        client.ping()
        logger.info("Connected to Redis successfully.")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        raise


# Function to normalize and insert heartbeat data into Redis
def process_heartbeat_message(message):
    try:
        # Parse the message (assumed to be in JSON format)
        data = json.loads(message)
        # Connect to Redis
        redis_client = connect_redis()

        # Process the 'hosts' array
        for host in data.get('hosts', []):
            c = Component(**host)
            redis_client.set(f"service:{c.name}:{c.status}", c.timestamp)
            logger.info(f"Set Redis key 'service:{c.name}:{c.status}' with value '{c.timestamp}'")
        # Process the 'rmq_consumers' -> 'services_status'
        for service in data['rmq_consumers'].get('services_status', []):
            c = Component(**service)
            redis_client.set(f"service:{c.name}:{c.status}", c.timestamp)
            logger.info(f"Set Redis key 'service:{c.name}:{c.status}' with value '{c.timestamp}'")

        # Process the 'rmq_consumers' -> 'queues_status'
        for queue in data['rmq_consumers'].get('queues_status', []):
            c = Component(**queue)
            redis_client.set(f"queue:{c.name}:{c.status}", c.timestamp)
            logger.info(f"Set Redis key 'queue:{c.name}:{c.status}' with value '{c.timestamp}'")

    except Exception as e:
        logger.error(f"Error processing heartbeat message: {str(e)}")
        raise


def subscribe_heartbeat(channel):
    def callback(ch, method, properties, body):
        b = body.decode()
        logger.info(f"Received message: {b}")
        logger.info("Processing message...")
        process_heartbeat_message(b)

    channel.basic_consume(queue=Config.RABBITMQ_QUEUE, on_message_callback=callback, auto_ack=True)
    logger.info("Waiting for messages...")
    channel.start_consuming()
