FROM python:3.11-slim

# Install poetry
RUN pip install poetry

WORKDIR /app

# Copy only pyproject.toml and poetry.lock first to cache dependencies
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install

# Copy the rest of the project, including the src/ directory
COPY . .

# Set Python path
ENV PYTHONPATH=/app

# Run the application
CMD ["poetry", "run", "python", "-m", "src.main"]


