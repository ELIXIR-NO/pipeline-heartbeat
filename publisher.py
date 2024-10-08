import json
import re
import socket
import time
from datetime import datetime, timezone

import requests
from loguru import logger

from config import Config
from logging_config import setup_logging
from models import Component

setup_logging()


def check_rmq_consumers(rmq_consumers_conf):
    """Check RabbitMQ consumers for specified queues using the RabbitMQ Management API."""
    results = []
    protocol = "https" if Config.RABBITMQ_TLS else "http"
    base_url = f"{protocol}://{Config.RABBITMQ_HOST}:{Config.RABBITMQ_MANAGEMENT_PORT}/api"
    for rmq in rmq_consumers_conf:
        vhost = Config.RABBITMQ_VHOST
        queue = rmq['queue']
        url = f"{base_url}/queues/{vhost}/{queue}"
        logger.info(f"Checking RabbitMQ consumers for queue '{queue}' in vhost '{vhost}'")
        try:
            # if mutual TLS: verify="/path/to/ca.pem"
            response = requests.get(url, auth=(Config.RABBITMQ_USER, Config.RABBITMQ_PASS))
            if response.status_code == 200:
                queue_info = response.json()
                consumers = queue_info.get('consumer_details', [])
                results.append({'queue': queue, 'consumers': consumers})
            else:
                logger.error(f"Failed to retrieve consumer info for queue '{queue}': {response.status_code}")
                results.append({'queue': queue, 'consumers': []})
        except requests.RequestException as e:
            logger.error(f"Error connecting to RabbitMQ API for queue '{queue}': {str(e)}")
            results.append({'vhost': vhost, 'queue': queue, 'consumers': []})

    return normalize_rmq_consumers_response(rmq_consumers_conf, results)


def normalize_rmq_consumers_response(rmq_consumers_conf, actual_consumers_data):
    """
    Transform the results by comparing expected listeners to actual consumers.
    Returns a summary for queue and service status.
    """
    queues_status = []
    services_status = []

    for consumer_config in rmq_consumers_conf:
        queue_name = consumer_config['queue']
        expected_listeners = consumer_config['listeners']
        logger.info(f"Checking expected listeners for queue: {queue_name}")
        # Find the actual consumers for this queue
        actual_consumers = next((q['consumers'] for q in actual_consumers_data if q['queue'] == queue_name), [])
        # Track queue status and service status
        queue_ok = True
        for listener in expected_listeners:
            expected_tag = listener['tag']
            name = listener['name']
            logger.info(f"Checking for service '{name}' with "
                        f"expected tag '{expected_tag}' in queue '{queue_name}'")
            # Find if the expected consumer tag is present in the actual consumers using regex
            found = any(
                re.search(expected_tag, consumer['consumer_tag']) and consumer['activity_status'] == 'up'
                for consumer in actual_consumers
            )
            if found:
                services_status.append(Component(name, "ok").to_dict())
            else:
                services_status.append(Component(name, "not_ok").to_dict())
                queue_ok = False  # Mark queue as not ok if any listener is missing
        # Append queue status
        queues_status.append(Component(queue_name, "ok" if queue_ok else "not_ok").to_dict())
    # Return the transformed result
    return {
        "queues_status": queues_status,
        "services_status": services_status
    }


def check_hosts(hosts):
    """Check if specified hosts and ports are reachable."""
    results = []
    for host_info in hosts:
        host = host_info['host']
        port = int(host_info['port'])
        name = host_info.get('name', host)
        logger.info(f"Checking host '{host}' on port '{port}' for service '{name}'")
        try:
            sock = socket.create_connection((host, port), timeout=5)
            sock.close()
            results.append(Component(name, "ok").to_dict())
        except (socket.timeout, socket.error) as e:
            logger.error(f"Host '{host}' on port '{port}' is down: {str(e)}")
            results.append(Component(name, "not_ok").to_dict())
    return results


def publish_heartbeat(_, channel):
    # Read the publisher config json
    # If not path is specified, we look the configuration file in the
    # HOME directory of the container.
    with open("/publisher_config.json", "r") as f:
        config = json.load(f)
        logger.info("Publisher configuration loaded.")
    # Extract hosts and RabbitMQ consumers from config
    hosts = config.get('heartbeat', {}).get('hosts', [])
    rmq_consumers = config.get('heartbeat', {}).get('rmq_consumers', [])
    utc_timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
    # Infinite loop to send heartbeat every minute (or configured interval)
    while True:
        # Check hosts and RabbitMQ consumers
        hosts_result = check_hosts(hosts)
        rmq_result = check_rmq_consumers(rmq_consumers)
        message = {
            "status": "heartbeat",
            "service": "publisher",
            "timestamp": utc_timestamp,
            "hosts": hosts_result,
            "rmq_consumers": rmq_result
        }
        message_body = json.dumps(message)
        logger.info(f"Preparing to publish heartbeat: {message_body}")
        # Determine the routing key (fallback to queue name if RABBITMQ_ROUTING_KEY is not provided)
        routing_key = Config.RABBITMQ_ROUTING_KEY or Config.RABBITMQ_QUEUE
        # Publish to the specified exchange
        logger.info(f"Publishing to exchange '{Config.RABBITMQ_EXCHANGE}' with routing key '{routing_key}'")
        try:
            channel.basic_publish(
                exchange=Config.RABBITMQ_EXCHANGE,  # Use the provided exchange
                routing_key=routing_key,  # Use the configured routing key or queue name as fallback
                body=message_body
            )
            logger.info(f"Heartbeat sent. Sleeping for {Config.PUBLISH_INTERVAL} seconds.")
            time.sleep(Config.PUBLISH_INTERVAL)
        except Exception as e:
            logger.error(f"Failed to publish message: {str(e)}")
            raise  # Re-raise the exception for handling by the caller or logging system
