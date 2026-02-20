> **Disclaimer:** Only interview processes where sharing the submitted material was not explicitly restricted are published here. Original assignments/prompts are not included. If you would like your process to be taken down, please contact marianojosecrosetti@gmail.com.

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

## RESTful API Design

The API follows RESTful principles:

- **Resource-Based URLs**: Endpoints are organized around resources (transcripts)
- **HTTP Verbs**: Using HTTP methods semantically (GET to retrieve, POST to create)
- **Idempotence**: GET operations are idempotent and don't modify state
- **Statelessness**: Each request contains all necessary information
- **Collection Pattern**: Using plural nouns for resource collections (e.g., /transcripts)
- **Consistent Responses**: Structured JSON responses with appropriate status codes

## API Endpoints

### Create Transcript Analysis

- **POST /transcripts**
  - Request body: `{ "transcript": "text" }`
  - Creates a new analysis and returns a summary and action items

### Batch Analysis (Concurrent Processing)

- **POST /transcripts/batch**
  - Request body: `{ "transcripts": ["text1", "text2", ...] }`
  - Processes multiple transcripts concurrently
  - Returns an array of results: `{ "results": [{ id, summary, action_items }, ...] }`

### List All Transcript Analyses

- **GET /transcripts**
  - Retrieves a list of all analysis IDs

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

### Analyze a Transcript

```bash
curl -X POST http://localhost:8000/transcripts \
  -H "Content-Type: application/json" \
  -d '{"transcript":"The team needs to improve our testing process. We should adopt TDD and aim for higher code coverage. Also, we need to automate our deployment pipeline."}'
```

Expected response:
```json
{
  "id": "4e59823b-4877-4569-b50c-8572dfcebe0e",
  "summary": "The team discussed the need to enhance their testing process by implementing Test-Driven Development (TDD) and increasing their code coverage to ensure higher quality code. Furthermore, there is a necessity to automate the deployment pipeline to streamline operations and improve efficiency.",
  "action_items": [
    "Research and implement Test-Driven Development (TDD) practices within the team.",
    "Set specific targets for code coverage improvements and regularly monitor progress.",
    "Identify tools and resources required for testing improvements and conduct training sessions if necessary.",
    "Assess current deployment processes to identify bottlenecks and areas for automation.",
    "Select a suitable deployment automation tool, possibly integrating with existing systems, and plan its implementation.",
    "Develop a timeline and project plan for rolling out improvements in both testing and deployment processes."
  ]
}
```

### List All Transcript Analyses

```bash
curl http://localhost:8000/transcripts
```

Expected response:
```json
[
  "4e59823b-4877-4569-b50c-8572dfcebe0e",
  "71dfb2fd-52b2-43ab-8550-51cb12ca0629",
  "3287e11e-9a31-4534-9060-0e46e334eeba"
]
```

### Batch Analysis of Multiple Transcripts

```bash
curl -X POST http://localhost:8000/transcripts/batch \
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
      "id": "71dfb2fd-52b2-43ab-8550-51cb12ca0629",
      "summary": "The customer service team has experienced a rise in call volumes, specifically related to problems users are encountering with logging into the mobile app.",
      "action_items": [
        "Investigate the root cause of the mobile app login issues.",
        "Deploy a dedicated technical team to address and fix the login problems promptly.",
        "Communicate with users about the known issue and provide regular updates on the resolution status.",
        "Consider implementing a temporary workaround for users while a permanent fix is being developed.",
        "Enhance system monitoring to detect early warning signs of similar issues in the future.",
        "Review and improve the QA process to prevent similar issues from occurring post-deployment."
      ]
    },
    {
      "id": "3287e11e-9a31-4534-9060-0e46e334eeba",
      "summary": "The marketing team plans to implement a Q3 promotion offering a 15% discount on the premium tier product.",
      "action_items": [
        "Evaluate the potential impact of a 15% discount on the premium tier's revenue and profit margins.",
        "Design a marketing strategy to effectively communicate the promotion to the target audience.",
        "Coordinate with sales and customer service teams to prepare for potential customer inquiries and increased interest during the promotion.",
        "Monitor and analyze the promotion's performance to assess its success and inform future promotional strategies."
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

# Create a transcript analysis
transcript_data = {
    "transcript": "We need to schedule the quarterly review meeting with all department heads next week."
}
response = requests.post(
    f"{BASE_URL}/transcripts",
    headers={"Content-Type": "application/json"},
    data=json.dumps(transcript_data)
)
analysis = response.json()
print(f"Analysis ID: {analysis['id']}")
print(f"Summary: {analysis['summary']}")
print("Action items:")
for item in analysis['action_items']:
    print(f"- {item}")

# List all analyses
response = requests.get(f"{BASE_URL}/transcripts")
all_analysis_ids = response.json()
print(f"\nRetrieved {len(all_analysis_ids)} analysis IDs")
print(f"Analysis IDs: {', '.join(all_analysis_ids)}")

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
