import os


class Config:
    # Fetch configuration from environment variables
    HEARTBEAT_MODE = os.getenv("HEARTBEAT_MODE", "publisher")  # 'publisher' or 'subscriber'
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
    RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
    RABBITMQ_PASS = os.getenv('RABBITMQ_PASS', 'guest')
    RABBITMQ_VHOST = os.getenv('RABBITMQ_VHOST', '/')
    RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', '')
    RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', '')
    RABBITMQ_ROUTING_KEY = os.getenv('RABBITMQ_ROUTING_KEY', '')
    RABBITMQ_TLS = os.getenv('RABBITMQ_TLS', 'false').lower() == 'true'
    RABBITMQ_CA_CERT_PATH = os.getenv('RABBITMQ_CA_CERT_PATH', '')
    RABBITMQ_TLS_PORT = int(os.getenv('RABBITMQ_TLS_PORT', 5671))
    PUBLISH_INTERVAL = int(os.getenv('PUBLISH_INTERVAL', 60))  # Publish interval in seconds
    RABBITMQ_MANAGEMENT_PORT = int(os.getenv('RABBITMQ_MANAGEMENT_PORT', 15672))
    REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO') # DEBUG
