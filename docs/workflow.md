```
sequenceDiagram
    participant WebClient
    participant ProcessingService as Processing Service
    participant RabbitMQ as RabbitMQ
    participant CrawlerService as Crawler Service
    participant SummarizerService as Summarizer Service
    participant DatabaseService as Database Service
    participant EmbeddingService as Embedding Service
    participant VectorDBService as Vector DB Service
    
    WebClient->>ProcessingService: Send URL
    ProcessingService->>RabbitMQ: Publish URL to crawl_queue
    RabbitMQ->>CrawlerService: New URL in crawl_queue
    CrawlerService->>RabbitMQ: Publish crawled content to summarize_queue
    RabbitMQ->>SummarizerService: New content in summarize_queue
    SummarizerService->>RabbitMQ: Publish summarized content to store_db_queue
    RabbitMQ->>DatabaseService: New summarized content in store_db_queue
    DatabaseService->>RabbitMQ: Acknowledgement of stored summary
    SummarizerService->>RabbitMQ: Publish summarized content to embedding_queue
    RabbitMQ->>EmbeddingService: New summarized content in embedding_queue
    EmbeddingService->>RabbitMQ: Publish embeddings to store_vector_db_queue
    RabbitMQ->>VectorDBService: New embeddings in store_vector_db_queue
    VectorDBService->>RabbitMQ: Acknowledgement of stored embeddings

    Note over WebClient,VectorDBService: Flow of data through services and queues
```