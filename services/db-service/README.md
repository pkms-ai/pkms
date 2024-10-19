# DB Service

This service provides database operations for content management.

## Setup

1. Install dependencies:   ```
   poetry install   ```

2. Initialize the database:   ```
   # Create schema only
   poetry run initialize-db --create-schema

   # Create schema and populate with sample data (for development)
   poetry run initialize-db --create-schema --populate-data

   # Update existing schema
   poetry run initialize-db --update-schema   ```

3. Run the service:   ```
   poetry run uvicorn db_service.main:app --reload   ```

## API Endpoints

- `GET /check_url`: Check if a URL exists in the database
  - Query parameter: `url`
  - Returns: `{"url": "<url>", "exists": true/false}`

## Docker

To build and run the Docker container:

