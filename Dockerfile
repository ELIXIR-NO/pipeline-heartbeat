# Use official Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables (can be overridden at runtime)
ENV HEARTBEAT_MODE=publisher
ENV RABBITMQ_HOST=localhost
ENV RABBITMQ_PORT=5672
ENV RABBITMQ_USER=guest
ENV RABBITMQ_PASS=guest
ENV RABBITMQ_VHOST=/
ENV RABBITMQ_EXCHANGE=my_topic_exchange
ENV RABBITMQ_QUEUE=my_queue
ENV RABBITMQ_ROUTING_KEY=service
ENV RABBITMQ_TLS=true
ENV RABBITMQ_CA_CERT_PATH=/path/to/ca_cert.pem
ENV RABBITMQ_TLS_PORT=5671
ENV PUBLISH_INTERVAL=60
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379
ENV REDIS_DB=0

ENV LOGURU_AUTOINIT=False

# Run the Python script
CMD ["python", "heartbeat.py"]
