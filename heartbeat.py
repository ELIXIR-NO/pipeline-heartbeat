import pika
from loguru import logger

from config import Config
from logging_config import setup_logging
from publisher import publish_heartbeat
from subscriber import subscribe_heartbeat

setup_logging()


def establish_connection():
    logger.info("Establishing connection to TSD RabbitMQ...")
    if Config.RABBITMQ_TLS:
        # Setup TLS connection if configured
        logger.info("Using TLS for TSD RabbitMQ connection.")
        import ssl
        context = pika.SSLOptions(
            ssl.create_default_context(cafile=Config.RABBITMQ_CA_CERT_PATH),
            Config.RABBITMQ_HOST
        )
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                virtual_host=Config.RABBITMQ_VHOST,
                credentials=pika.PlainCredentials(Config.RABBITMQ_USER, Config.RABBITMQ_PASS),
                ssl_options=context
            )
        )
    else:
        # Non-TLS connection
        logger.info("Continuing without TLS for TSD RabbitMQ connection.")
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=Config.RABBITMQ_HOST,
                port=Config.RABBITMQ_PORT,
                virtual_host=Config.RABBITMQ_VHOST,
                credentials=pika.PlainCredentials(Config.RABBITMQ_USER, Config.RABBITMQ_PASS)
            )
        )

    return connection


def validate_config():
    """Validate the necessary RabbitMQ configurations."""
    missing_configs = []

    if not Config.RABBITMQ_EXCHANGE:
        missing_configs.append("RABBITMQ_EXCHANGE")
    if not Config.RABBITMQ_QUEUE:
        missing_configs.append("RABBITMQ_QUEUE")
    if not Config.RABBITMQ_ROUTING_KEY:
        missing_configs.append("RABBITMQ_ROUTING_KEY")

    if missing_configs:
        logger.error(f"Missing configuration(s): {', '.join(missing_configs)}. Exiting the application.")
        import sys
        sys.exit(1)


def setup_rabbitmq(channel):
    # Ensure the queue and exchange exist (Idempotent)
    # channel.exchange_declare(exchange=Config.RABBITMQ_EXCHANGE, exchange_type='topic', durable=True)
    channel.queue_declare(queue=Config.RABBITMQ_QUEUE, durable=True)
    channel.queue_bind(
        exchange=Config.RABBITMQ_EXCHANGE,
        queue=Config.RABBITMQ_QUEUE,
        routing_key=Config.RABBITMQ_ROUTING_KEY,
    )

    logger.info(f"'{Config.HEARTBEAT_MODE}' connected to exchange "
                f"'{Config.RABBITMQ_EXCHANGE}' and queue '{Config.RABBITMQ_QUEUE}'")


def main():
    connection = None
    try:
        # Establish connection and create channel
        connection = establish_connection()
        channel = connection.channel()
        # Validate configurations
        validate_config()
        # Setup RabbitMQ queue and bindings
        setup_rabbitmq(channel)
        # Check if the mode is 'publisher' or 'subscriber'
        if Config.HEARTBEAT_MODE.lower() == "publisher":
            publish_heartbeat(connection, channel)
        else:
            subscribe_heartbeat(channel)
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"RabbitMQ connection failed: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        if connection is not None:
            connection.close()
            logger.info("Connection to RabbitMQ closed.")


if __name__ == "__main__":
    main()
