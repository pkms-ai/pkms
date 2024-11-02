#!/bin/bash

echo "Building Docker images for all services"

echo "Building pkms-web"
docker build --target production -t pkms-web -f ./services/web-application/Dockerfile ./services/web-application/

echo "Building db-manager"
docker build -t db-manager -f ./services/db-service/Dockerfile ./services/db-service/

echo "Building content-manager"
docker build --target production -t content-manager -f ./services/content-submission-service/Dockerfile ./services/content-submission-service/

echo "Building universal-worker"
docker build --target production -t universal-worker -f ./services/universal_worker/Dockerfile ./services/universal_worker/
