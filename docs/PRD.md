# Core Functionalities for the MVP

Based on the current service structure and the Product Requirements Document, the following are the core functionalities to be included in the **Minimum Viable Product (MVP)** of the Personal Knowledge Management System (PKMS):

---

## **1. Content Submission**

- **Multi-Platform Input Methods**
  - Users can submit content via:
    - **Content Submission Service**
    - **Web application** (to be implemented)
    - **API endpoints**
  - Supported content types:
    - **Web articles**
    - **YouTube videos**
    - **Useful web links/bookmarks**

---

## **2. Content Processing**

- **Content Processing Service**
  - **Classify and route** submitted content to appropriate processing queues
  - **Web Article Processing**
    - **Crawl or scrape** web pages to extract the main content
    - **Convert content to Markdown** format
    - **Clean content** by removing ads and irrelevant sections
    - **Summarize content** using AI-powered tools
  - **YouTube Video Processing**
    - **Transcribe YouTube video links** to extract audio content
    - **Summarize transcribed content**
  - **Store** original content, transcriptions, and summaries in the database and embedding database

---

## **3. Data Storage and Management**

- **Database Systems**
  - Utilize databases to store content, summaries, and embeddings:
    - **Relational database** for structured data (PostgreSQL)
    - **Embedding database** for semantic search capabilities (to be implemented)

---

## **4. User Interface**

- **Web Application**
  - **Basic interface** to list all summaries with thumbnails and links to original content
  - Provide **intuitive navigation** and a **responsive design** for desktop and mobile browsers
  - To be implemented in future iterations

---

## **5. User Management**

- **Authentication and Profiles**
  - Implement **secure user authentication** using Keycloak
  - Provide **basic user profile management** for managing preferences

---

## **6. Notifications and Reporting**

- **Summary Reports**
  - **Generate and send summary reports** via a notification service (to be implemented)
  - Allow users to receive **instant notifications** when content is processed

---

## **7. Search and Retrieval**

- **Basic Search Functionality**
  - Implement **full-text search** to retrieve stored content and summaries
  - Allow users to **search by keywords** and **filter by content type**
  - To be implemented in future iterations

---

## **8. Content Visualization**

- **Thumbnails and Screenshots**
  - **Generate thumbnails or screenshots** of web pages and YouTube videos
  - Display visuals alongside summaries in the web application
  - To be implemented in future iterations

---

## **9. Essential Features**

- **Content Storage**
  - Store and manage content securely in the system
- **Scalability and Performance**
  - Ensure the system can handle multiple users and content submissions efficiently
  - Utilize message queues (RabbitMQ) for asynchronous processing
- **Security Measures**
  - Implement **encryption** for data in transit (e.g., SSL/TLS)
  - Protect user data and maintain **data integrity**

---

## **10. Service Architecture**

- **Microservices-based Architecture**
  - Content Submission Service
  - Content Processing Service
  - Authentication Service (Keycloak)
  - Database Service
  - API Gateway (to be implemented)
  - Web Application (to be implemented)

---

These core functionalities constitute the essential features required to deliver a functional MVP of the Personal Knowledge Management System. The current service structure provides a solid foundation for:

- **Collecting** information from various sources
- **Processing and summarizing** content for quick understanding
- **Storing and managing** the personal knowledge base
- **Securing** user data and content

Additional features and enhancements, such as the web application, advanced search, mobile applications, collaboration tools, and AI-driven recommendations, can be developed in subsequent phases to further improve the user experience and system capabilities.
