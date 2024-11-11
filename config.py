import os


class Config:
    # Fetch configuration from environment variables
    HEARTBEAT_MODE = os.getenv("HEARTBEAT_MODE", "publisher")  # 'publisher' or 'subscriber'
    PUBLISHER_CONFIG_PATH = os.getenv("PUBLISHER_CONFIG_PATH", "/publisher_config.json")
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')
    RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', 'my_topic_exchange')
    RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', 'my_queue')
    RABBITMQ_ROUTING_KEY = os.getenv('RABBITMQ_ROUTING_KEY', 'service.heartbeat')
    RABBITMQ_TLS = os.getenv('RABBITMQ_TLS', 'false').lower() == 'true'
    RABBITMQ_CA_CERT_PATH = os.getenv('RABBITMQ_CA_CERT_PATH', '')
    RABBITMQ_TLS_PORT = int(os.getenv('RABBITMQ_TLS_PORT', 5671))
    PUBLISH_INTERVAL = int(os.getenv('PUBLISH_INTERVAL', 60))  # Publish interval in seconds
    RABBITMQ_MANAGEMENT_PORT = int(os.getenv('RABBITMQ_MANAGEMENT_PORT', 15672))
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    @staticmethod
    def get_rabbitmq_url():
        protocol = "amqps" if Config.RABBITMQ_TLS else "amqp"
        port = Config.RABBITMQ_TLS_PORT if Config.RABBITMQ_TLS else Config.RABBITMQ_PORT
        return f"{protocol}://{Config.RABBITMQ_USER}:{Config.RABBITMQ_PASS}@{Config.RABBITMQ_HOST}:{port}{Config.RABBITMQ_VHOST}"
