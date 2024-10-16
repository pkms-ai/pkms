# System Design Document with Folder Structure

## **Table of Contents**

1. [Introduction](#1-introduction)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Microservices and Components](#3-microservices-and-components)
   - 3.1. [API Gateway](#31-api-gateway)
   - 3.2. [Authentication Service](#32-authentication-service)
   - 3.3. [Content Submission Service](#33-content-submission-service)
   - 3.4. [Content Processing Service](#34-content-processing-service)
   - 3.5. [Notification Service](#35-notification-service)
   - 3.6. [Search Service](#36-search-service)
   - 3.7. [Content Visualization Service](#37-content-visualization-service)
   - 3.8. [Web Application (Frontend)](#38-web-application-frontend)
   - 3.9. [Databases](#39-databases)
   - 3.10. [Message Queue (RabbitMQ)](#310-message-queue-rabbitmq)
   - 3.11. [Graph Database (Neo4j)](#311-graph-database-neo4j)
   - 3.12. [Reverse Proxy](#312-reverse-proxy)
4. [Data Flow and Integration](#4-data-flow-and-integration)
5. [Project Folder Structure](#5-project-folder-structure)
6. [Docker Compose Configuration](#6-docker-compose-configuration)
7. [Inter-Service Communication](#7-inter-service-communication)
8. [Technology Stack Summary](#8-technology-stack-summary)
9. [Security Considerations](#9-security-considerations)
10. [Scalability and Future Enhancements](#10-scalability-and-future-enhancements)
11. [Conclusion](#11-conclusion)

---

## **1. Introduction**

This document outlines the system design for the core functionalities of the Personal Knowledge Management System (PKMS). It provides a detailed overview of the architecture, components, data flow, folder structure, and deployment configuration. The design leverages microservices architecture to ensure modularity, scalability, and maintainability. Each service is containerized using Docker, and the entire system can be orchestrated using Docker Compose.

---

## **2. System Architecture Overview**

The PKMS is designed as a collection of microservices, each responsible for specific functionalities. The services communicate through RESTful APIs and asynchronous messaging using RabbitMQ. The architecture includes the following layers:

- **Presentation Layer**: Web application (frontend) and Telegram bot for user interaction.
- **Business Logic Layer**: Microservices handling content submission, processing, notification, and search.
- **Data Layer**: Relational database (PostgreSQL), embedding database (Milvus), graph database (Neo4j), and message queue (RabbitMQ).
- **Integration Layer**: API Gateway and Reverse Proxy for routing and security.

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

### **3.5. Notification Service**

- **Purpose**: Sends notifications to users via Telegram when content processing is complete.
- **Responsibilities**:
  - Receive messages from RabbitMQ about processing completion.
  - Send messages using the Telegram Bot API.
- **Technologies**: Python, python-telegram-bot library.

### **3.6. Search Service**

- **Purpose**: Provides search capabilities over the stored content.
- **Responsibilities**:
  - Handle search queries.
  - Perform full-text and semantic searches.
  - Interface with the embedding database.
- **Technologies**: Python, Elasticsearch, Milvus.

### **3.7. Content Visualization Service**

- **Purpose**: Generates thumbnails and screenshots for content visualization.
- **Responsibilities**:
  - Capture screenshots of web pages.
  - Generate thumbnails for videos.
  - Store visual assets.
- **Technologies**: Node.js with Puppeteer, Python with Selenium.

### **3.8. Web Application (Frontend)**

- **Purpose**: Provides the user interface for interacting with the PKMS.
- **Responsibilities**:
  - Display content lists with summaries and thumbnails.
  - Allow content submission and search.
- **Technologies**: React.js, Vue.js, or Angular.

### **3.9. Databases**

#### **3.9.1. Relational Database (PostgreSQL)**

- **Purpose**: Stores structured data like user profiles, content metadata, summaries.
- **Responsibilities**:
  - Ensure data integrity and relationships.
- **Technologies**: PostgreSQL 13.

#### **3.9.2. Embedding Database (Milvus)**

- **Purpose**: Stores vector embeddings for semantic search.
- **Responsibilities**:
  - Perform similarity searches over embeddings.
- **Technologies**: Milvus v2.0.

### **3.10. Message Queue (RabbitMQ)**

- **Purpose**: Facilitates asynchronous communication between services.
- **Responsibilities**:
  - Queue messages for content processing and notifications.
- **Technologies**: RabbitMQ with Management Plugin.

### **3.11. Graph Database (Neo4j)**

- **Purpose**: Stores and manages relationships between content entities for enhanced search and recommendations.
- **Responsibilities**:
  - Store nodes and relationships representing content, users, tags, and concepts.
  - Provide graph traversal capabilities.
- **Technologies**: Neo4j.

### **3.12. Reverse Proxy**

- **Purpose**: Routes external HTTP requests to internal services and handles SSL termination.
- **Responsibilities**:
  - Serve as an entry point for web traffic.
  - Manage SSL certificates.
- **Technologies**: Nginx.

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
│   ├── milvus/
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
      - milvus
    networks:
      - pkms-network

  youtube-video-processor:
    build: ./services/content-processing-service/youtube-video-processor
    depends_on:
      - message-queue
      - postgres
      - milvus
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
      - milvus
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

  milvus:
    image: milvusdb/milvus:v2.0.0
    volumes:
      - milvus_data:/var/lib/milvus
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
  milvus_data:
  neo4j_data:
```

---

## **7. Inter-Service Communication**

- **API Gateway**:
  - Routes HTTP requests to appropriate services.
  - Interacts with the Authentication Service for user validation.

- **RabbitMQ**:
  - Content Submission Service publishes messages to queues.
  - Content Processing Services consume messages for processing tasks.
  - Notification Service consumes messages to send user notifications.

- **Databases**:
  - Services interact with databases to store and retrieve data.
  - Content Processing Services write to PostgreSQL, Milvus, and Neo4j.
  - Search Service reads from Milvus and Neo4j.

- **Reverse Proxy**:
  - Exposes services to the external network.
  - Handles SSL termination and load balancing.

---

## **8. Technology Stack Summary**

- **Frontend**:
  - **Web Application**: React.js or Vue.js
- **Backend**:
  - **Languages**: Python, Node.js
  - **Frameworks**: FastAPI, Express.js
- **Databases**:
  - **Relational**: PostgreSQL
  - **Embedding**: Milvus
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

## **9. Security Considerations**

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

## **10. Scalability and Future Enhancements**

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

## **11. Conclusion**

The system design provides a modular and scalable architecture for the PKMS, focusing on the core functionalities required for the MVP. The use of microservices, containerization, and an organized folder structure allows for flexibility in development and deployment. By integrating key components like RabbitMQ and Neo4j, the system is well-prepared for future enhancements and scaling to meet growing user demands.

---

**Note**: Ensure that all services have proper error handling, logging, and adhere to best practices for security and performance. Regularly update dependencies and monitor system performance to maintain a robust and reliable system.