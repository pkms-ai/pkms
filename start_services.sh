#!/bin/bash

# Define the services you want to start
SERVICES=("reverse-proxy" "api-gateway" "content-submission-service" "message-queue")

docker-compose build "${SERVICES[@]}"
# Start the specified services without their dependencies
docker-compose up --no-deps "${SERVICES[@]}"