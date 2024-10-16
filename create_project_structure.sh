#!/bin/bash

# Create the main project directory
mkdir -p pkms-project

# Change to the project directory
cd pkms-project

# Create root level files
touch docker-compose.yml .env README.md

# Create services directories and files
mkdir -p services/{api-gateway,auth-service,content-submission-service,content-processing-service/{web-article-processor,youtube-video-processor},notification-service,search-service,content-visualization-service,web-application}

# Create Dockerfiles and src directories for each service
for service in api-gateway auth-service content-submission-service notification-service search-service content-visualization-service web-application; do
    touch services/$service/Dockerfile
    mkdir -p services/$service/src
done

# Create Dockerfiles and src directories for content processing subservices
for subservice in web-article-processor youtube-video-processor; do
    touch services/content-processing-service/$subservice/Dockerfile
    mkdir -p services/content-processing-service/$subservice/src
done

# Create databases directories and files
mkdir -p databases/{postgres,milvus,neo4j}
touch databases/postgres/{Dockerfile,init.sql}
touch databases/milvus/Dockerfile
mkdir -p databases/milvus/config
touch databases/neo4j/Dockerfile
mkdir -p databases/neo4j/conf

# Create message-queue directory and files
mkdir -p message-queue/config
touch message-queue/Dockerfile

# Create reverse-proxy directory and files
mkdir -p reverse-proxy
touch reverse-proxy/{Dockerfile,nginx.conf}

# Create shared and logs directories
mkdir -p shared/utils logs

echo "Project structure created successfully!"
