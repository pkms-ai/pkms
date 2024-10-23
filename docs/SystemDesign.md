# System Design Document

## **Table of Contents**

1. [Introduction](#1-introduction)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Microservices and Components](#3-microservices-and-components)
   - 3.1. [API Gateway](#31-api-gateway)
   - 3.2. [Authentication Service](#32-authentication-service)
   - 3.3. [Content Submission Service](#33-content-submission-service)
   - 3.4. [Content Processing Service](#34-content-processing-service)
   - 3.5. [Database Service](#35-database-service)
   - 3.6. [Message Queue (RabbitMQ)](#36-message-queue-rabbitmq)
4. [Data Flow and Integration](#4-data-flow-and-integration)
5. [Project Folder Structure](#5-project-folder-structure)
6. [Docker Compose Configuration](#6-docker-compose-configuration)
7. [Technology Stack Summary](#7-technology-stack-summary)
8. [Security Considerations](#8-security-considerations)
9. [Scalability and Future Enhancements](#9-scalability-and-future-enhancements)
10. [Conclusion](#10-conclusion)

---

## **1. Introduction**

This document outlines the system design for the core functionalities of the Personal Knowledge Management System (PKMS) MVP. It provides an overview of the architecture, components, data flow, folder structure, and deployment configuration. The design leverages a microservices architecture to ensure modularity, scalability, and maintainability.

---

## **2. System Architecture Overview**

The PKMS MVP is designed as a collection of microservices, each responsible for specific functionalities. The services communicate through RESTful APIs and asynchronous messaging using RabbitMQ. The architecture includes the following layers:

- **Business Logic Layer**: Microservices handling content submission and processing.
- **Data Layer**: Relational database (PostgreSQL) and message queue (RabbitMQ).
- **Integration Layer**: Authentication Service (Keycloak) for security.

**High-Level Architecture Diagram:**

```
[User] <---> [Web Application] <---> [API Gateway] <---> [Microservices] <---> [Databases]
                               \                               |
                                \--> [Telegram Bot] <---> [Notification Service]
```

---

## **3. Microservices and Components**

### **3.1. API Gateway**

- **Purpose**: Acts as the single entry point for all client requests, routing them to the appropriate microservices.
- **Responsibilities**:
  - Handle authentication and authorization.
  - Rate limiting and request validation.
  - Route requests to backend services.
- **Technologies**: Kong, Express Gateway, or custom implementation using Node.js or Python.

### **3.2. Authentication Service**

- **Purpose**: Manages user authentication and authorization.
- **Responsibilities**:
  - User registration and login.
  - Token generation and validation (e.g., JWT).
- **Technologies**: Keycloak, OAuth 2.0, or custom implementation using libraries like Passport.js (Node.js) or Django Authentication (Python).

### **3.3. Content Submission Service**

- **Purpose**: Handles content submissions from users via the web app, Telegram bot, or API.
- **Responsibilities**:
  - Receive and validate content submissions.
  - Publish messages to RabbitMQ for processing.
- **Technologies**: Python (FastAPI), Node.js (Express).

### **3.4. Content Processing Service**

Divided into two processors:

#### **3.4.1. Web Article Processor**

- **Purpose**: Processes web articles for extraction and summarization.
- **Responsibilities**:
  - Extract main content from web pages.
  - Convert content to Markdown.
  - Summarize content.
  - Generate embeddings.
  - Store data in databases.
- **Technologies**: Python, Newspaper3k, Hugging Face Transformers.

#### **3.4.2. YouTube Video Processor**

- **Purpose**: Processes YouTube videos for transcription and summarization.
- **Responsibilities**:
  - Download or access video transcripts.
  - Transcribe audio if necessary.
  - Summarize transcriptions.
  - Generate embeddings.
  - Store data in databases.
- **Technologies**: Python, pytube, OpenAI Whisper.

### **3.5. Database Service**

- **Purpose**: Stores and manages data in the relational database (PostgreSQL) and message queue (RabbitMQ).
- **Responsibilities**:
  - Ensure data integrity and relationships.
  - Queue messages for content processing and notifications.
- **Technologies**: PostgreSQL 13, RabbitMQ with Management Plugin.

### **3.6. Message Queue (RabbitMQ)**

- **Purpose**: Facilitates asynchronous communication between services.
- **Responsibilities**:
  - Queue messages for content processing and notifications.
- **Technologies**: RabbitMQ with Management Plugin.

---

## **4. Data Flow and Integration**

1. **User Submission**:
   - User submits content via the web app or Telegram bot.
   - Content Submission Service validates and publishes a message to RabbitMQ.

2. **Content Processing**:
   - Content Processing Service consumes the message.
   - Processes content (extraction, transcription, summarization).
   - Breaks content into chunks and generates embeddings.
   - Stores data in the relational database, embedding database, and Neo4j.

3. **Notification**:
   - Upon completion, publishes a message to RabbitMQ.
   - Notification Service sends a Telegram message to the user.

4. **User Access**:
   - User accesses the web application to view content.
   - Web application communicates with the API Gateway to fetch data.

5. **Search**:
   - User performs a search via the web application.
   - Search Service handles the query, interacting with the embedding database and Neo4j.

---

## **5. Project Folder Structure**

```
pkms-project/
├── docker-compose.yml
├── .env
├── README.md
├── services/
│   ├── api-gateway/
│   │   ├── Dockerfile
│   │   └── src/
│   ├── auth-service/
│   │   ├── Dockerfile
│   │   └── src/
│   ├── content-submission-service/
│   │   ├── Dockerfile
│   │   └── src/
│   ├── content-processing-service/
│   │   ├── web-article-processor/
│   │   │   ├── Dockerfile
│   │   │   └── src/
│   │   └── youtube-video-processor/
│   │       ├── Dockerfile
│   │       └── src/
│   ├── notification-service/
│   │   ├── Dockerfile
│   │   └── src/
│   ├── search-service/
│   │   ├── Dockerfile
│   │   └── src/
│   ├── content-visualization-service/
│   │   ├── Dockerfile
│   │   └── src/
│   └── web-application/
│       ├── Dockerfile
│       └── src/
├── databases/
│   ├── postgres/
│   │   ├── Dockerfile
│   │   └── init.sql
│   ├── qdrant/
│   │   ├── Dockerfile
│   │   └── config/
│   └── neo4j/
│       ├── Dockerfile
│       └── conf/
├── message-queue/
│   ├── Dockerfile
│   └── config/
├── reverse-proxy/
│   ├── Dockerfile
│   └── nginx.conf
├── shared/
│   └── utils/
│       └── (shared code)
└── logs/
    └── (log files)
```

---

## **6. Docker Compose Configuration**

**docker-compose.yml**

```yaml
version: '3.8'

services:
  reverse-proxy:
    build: ./reverse-proxy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./reverse-proxy/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - api-gateway
    networks:
      - pkms-network

  api-gateway:
    build: ./services/api-gateway
    depends_on:
      - auth-service
    networks:
      - pkms-network

  auth-service:
    build: ./services/auth-service
    environment:
      - KEYCLOAK_USER=admin
      - KEYCLOAK_PASSWORD=admin
    ports:
      - "8081:8080"
    networks:
      - pkms-network

  content-submission-service:
    build: ./services/content-submission-service
    depends_on:
      - message-queue
      - auth-service
    networks:
      - pkms-network

  web-article-processor:
    build: ./services/content-processing-service/web-article-processor
    depends_on:
      - message-queue
      - postgres
      - qdrant
    networks:
      - pkms-network

  youtube-video-processor:
    build: ./services/content-processing-service/youtube-video-processor
    depends_on:
      - message-queue
      - postgres
      - qdrant
    networks:
      - pkms-network

  notification-service:
    build: ./services/notification-service
    depends_on:
      - message-queue
      - auth-service
    networks:
      - pkms-network

  search-service:
    build: ./services/search-service
    depends_on:
      - postgres
      - qdrant
      - neo4j
    networks:
      - pkms-network

  content-visualization-service:
    build: ./services/content-visualization-service
    depends_on:
      - postgres
    networks:
      - pkms-network

  web-application:
    build: ./services/web-application
    ports:
      - "3000:80"
    depends_on:
      - api-gateway
    networks:
      - pkms-network

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_USER=pkms_user
      - POSTGRES_PASSWORD=pkms_pass
      - POSTGRES_DB=pkms_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - pkms-network

  qdrant:
    image: qdrantdb/qdrant:v2.0.0
    volumes:
      - qdrant_data:/var/lib/qdrant
    networks:
      - pkms-network

  neo4j:
    image: neo4j:latest
    ports:
      - "7474:7474"   # HTTP
      - "7687:7687"   # Bolt
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data
    networks:
      - pkms-network

  message-queue:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    networks:
      - pkms-network

networks:
  pkms-network:

volumes:
  postgres_data:
  qdrant_data:
  neo4j_data:
```

---

## **7. Technology Stack Summary**

- **Frontend**:
  - **Web Application**: React.js or Vue.js
- **Backend**:
  - **Languages**: Python, Node.js
  - **Frameworks**: FastAPI, Express.js
- **Databases**:
  - **Relational**: PostgreSQL
  - **Embedding**: qdrant
  - **Graph**: Neo4j
- **Messaging**:
  - **Message Broker**: RabbitMQ
- **AI/NLP Tools**:
  - **Content Extraction**: Newspaper3k
  - **Summarization**: Hugging Face Transformers
  - **Transcription**: OpenAI Whisper
- **Containerization and Orchestration**:
  - **Containers**: Docker
  - **Orchestration**: Docker Compose
- **Other Tools**:
  - **Reverse Proxy**: Nginx
  - **Authentication**: Keycloak or custom OAuth 2.0 implementation

---

## **8. Security Considerations**

- **Authentication and Authorization**:
  - Secure authentication mechanisms.
  - Use JWT tokens for stateless authentication.
- **Data Encryption**:
  - SSL/TLS for all communications.
  - Encrypt sensitive data at rest if necessary.
- **Input Validation**:
  - Sanitize all user inputs to prevent injection attacks.
- **Access Control**:
  - Implement role-based access control where applicable.
- **Network Security**:
  - Use Docker networks to isolate services.
  - Limit exposed ports to only those necessary.

---

## **9. Scalability and Future Enhancements**

- **Microservices Architecture**:
  - Allows independent scaling of services based on load.
- **Containerization**:
  - Facilitates deployment across different environments.
- **Service Discovery and Load Balancing**:
  - Implement service discovery for dynamic scaling (e.g., using Kubernetes in the future).
- **Future Enhancements**:
  - Implement advanced search features using embeddings and graph traversals.
  - Develop mobile applications.
  - Add collaboration and sharing features.

---

## **10. Conclusion**

The system design provides a modular and scalable architecture for the PKMS, focusing on the core functionalities required for the MVP. The use of microservices, containerization, and an organized folder structure allows for flexibility in development and deployment. By integrating key components like RabbitMQ and Neo4j, the system is well-prepared for future enhancements and scaling to meet growing user demands.

---

**Note**: Ensure that all services have proper error handling, logging, and adhere to best practices for security and performance. Regularly update dependencies and monitor system performance to maintain a robust and reliable system.
