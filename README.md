# Transcript Analysis API

[![Tests Status](https://img.shields.io/badge/tests-passing-brightgreen)](docker-compose.test.yml)

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

## Usage Examples

Below are examples for using each API endpoint with curl commands.

### Health Check

```bash
# Check if the API is up and running
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy"}
```

### Analyze a Transcript (GET method)

```bash
# URL-encode your transcript
curl "http://localhost:8000/transcripts/analyze?transcript=Today%20we%20discussed%20the%20new%20product%20launch%20scheduled%20for%20next%20month.%20We%20need%20to%20prepare%20marketing%20materials%20and%20contact%20our%20distributors."
```

Expected response:
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "summary": "Discussion about upcoming product launch next month.",
  "action_items": [
    "Prepare marketing materials for the new product",
    "Contact distributors about the launch",
    "Finalize launch timeline"
  ]
}
```

### Analyze a Transcript (POST method)

```bash
curl -X POST http://localhost:8000/transcripts/analyze \
  -H "Content-Type: application/json" \
  -d '{"transcript":"The team needs to improve our testing process. We should adopt TDD and aim for higher code coverage. Also, we need to automate our deployment pipeline."}'
```

Expected response:
```json
{
  "id": "59a76d43-8c45-4dca-9a5c-0c82e8f9e182",
  "summary": "Discussion on improving testing processes and deployment automation.",
  "action_items": [
    "Implement Test-Driven Development (TDD)",
    "Increase code coverage in tests",
    "Automate the deployment pipeline"
  ]
}
```

### Retrieve a Transcript Analysis by ID

```bash
# Use the ID returned from a previous analysis
curl http://localhost:8000/transcripts/59a76d43-8c45-4dca-9a5c-0c82e8f9e182
```

Expected response:
```json
{
  "id": "59a76d43-8c45-4dca-9a5c-0c82e8f9e182",
  "summary": "Discussion on improving testing processes and deployment automation.",
  "action_items": [
    "Implement Test-Driven Development (TDD)",
    "Increase code coverage in tests",
    "Automate the deployment pipeline"
  ]
}
```

### Batch Analysis of Multiple Transcripts

```bash
curl -X POST http://localhost:8000/transcripts/analyze/batch \
  -H "Content-Type: application/json" \
  -d '{
    "transcripts": [
      "Customer service team reports increased call volumes regarding the mobile app login issues.",
      "Marketing wants to run a promotion for our premium tier in Q3 with a 15% discount."
    ]
  }'
```

Expected response:
```json
{
  "results": [
    {
      "id": "7f8d9a6b-1c2d-3e4f-5a6b-7c8d9e0f1a2b",
      "summary": "Increased customer service calls about mobile app login problems.",
      "action_items": [
        "Investigate mobile app login issues",
        "Prepare communication plan for affected users",
        "Monitor call volumes to track resolution progress"
      ]
    },
    {
      "id": "2a3b4c5d-6e7f-8a9b-0c1d-2e3f4a5b6c7d",
      "summary": "Marketing plan for Q3 premium tier promotion with 15% discount.",
      "action_items": [
        "Create promotion assets for the premium tier",
        "Set up the 15% discount in the billing system",
        "Prepare Q3 marketing campaign timeline"
      ]
    }
  ]
}
```

### Python Example with Requests

You can also use Python with the requests library:

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(f"Health check response: {response.json()}")

# Analyze a transcript (POST method)
transcript_data = {
    "transcript": "We need to schedule the quarterly review meeting with all department heads next week."
}
response = requests.post(
    f"{BASE_URL}/transcripts/analyze",
    headers={"Content-Type": "application/json"},
    data=json.dumps(transcript_data)
)
analysis = response.json()
print(f"Analysis ID: {analysis['id']}")
print(f"Summary: {analysis['summary']}")
print("Action items:")
for item in analysis['action_items']:
    print(f"- {item}")

# Retrieve a previously analyzed transcript
analysis_id = analysis['id']  # Use the ID from the previous response
response = requests.get(f"{BASE_URL}/transcripts/{analysis_id}")
retrieved_analysis = response.json()
print(f"\nRetrieved analysis with ID: {analysis_id}")
print(f"Summary: {retrieved_analysis['summary']}")
```

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
