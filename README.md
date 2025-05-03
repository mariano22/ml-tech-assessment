# Transcript Analysis API

A Python web API that analyzes plain text transcripts and returns a summary along with a list of next actions. The implementation follows clean architectural practices with proper separation of concerns.

## Features

- Analyze transcripts using OpenAI's API
- Get previously analyzed transcripts by ID
- In-memory storage of analysis results
- RESTful API with proper error handling
- Swagger documentation
- Asynchronous batch processing for concurrent transcript analysis

## Architecture

The project follows a Hexagonal (Ports & Adapters) Architecture:

- **Domain Layer**: Core business entities
- **Application Layer**: Use cases and services
- **Adapters Layer**: Inbound (API controllers) and outbound (OpenAI) adapters
- **Infrastructure Layer**: Technical implementations (repositories)
- **Ports**: Interfaces defining the boundaries between layers

## API Endpoints

### Analyze Transcript

- **GET /transcripts/analyze?transcript={text}**
  - Accepts a plain text transcript
  - Returns a summary and action items

- **POST /transcripts/analyze**
  - Request body: `{ "transcript": "text" }`
  - Returns a summary and action items

### Batch Analysis (Concurrent Processing)

- **POST /transcripts/analyze/batch**
  - Request body: `{ "transcripts": ["text1", "text2", ...] }`
  - Processes multiple transcripts concurrently
  - Returns an array of results: `{ "results": [{ id, summary, action_items }, ...] }`

### Get Transcript Analysis by ID

- **GET /transcripts/{id}**
  - Retrieves a previously generated analysis by ID

## Setup and Running

### Option 1: Local Setup

1. Clone the repository
2. Set up environment variables:
   ```
   OPENAI_API_KEY=your_api_key
   OPENAI_MODEL=gpt-4o-2024-08-06
   ```
3. Install dependencies:
   ```
   poetry install
   ```
4. Run the API:
   ```
   uvicorn app.main:app --reload
   ```

### Option 2: Run with Docker Compose

1. Clone the repository
2. Run the setup script to configure environment variables:
   ```
   ./setup.sh
   ```
   This will create a `.env` file with your OpenAI API key and other settings.
3. Start the services:
   ```
   docker-compose up -d
   ```
4. To stop the services:
   ```
   docker-compose down
   ```

### Accessing the API

Access the Swagger documentation at: http://localhost:8000/swagger

## Tests

The project includes a comprehensive testing infrastructure:

- Unit tests for all application layers
- Integration tests for the API endpoints
- Tests for asynchronous functionality
- Mocks for external dependencies (OpenAI API)
- Complete test coverage (>95%)
- Docker-based testing environment

### Running Tests with Docker

Run the entire test suite:

```bash
# Using the main docker-compose.yml
docker-compose run --rm test poetry run pytest

# Using dedicated test docker-compose.test.yml
docker-compose -f docker-compose.test.yml up test

# Run with test coverage report
docker-compose -f docker-compose.test.yml up test-coverage
```

Run specific tests:

```bash
# Run a specific test file
docker-compose run --rm test poetry run pytest tests/api/test_transcripts_api.py

# Run a specific test
docker-compose run --rm test poetry run pytest tests/api/test_transcripts_api.py::test_health_check

# Run with verbose output
docker-compose run --rm test poetry run pytest -v
```

### Test Coverage

Generate a test coverage report:

```bash
# Basic coverage report
docker-compose run --rm test poetry run pytest --cov=app tests/

# Generate HTML coverage report
docker-compose run --rm test poetry run pytest --cov=app --cov-report=html tests/
# The HTML report will be in htmlcov/ directory
```

The tests use mocks to avoid making actual calls to the OpenAI API, so you don't need a valid API key to run the tests.
