# Transcript Analysis API

A Python web API that analyzes plain text transcripts and returns a summary along with a list of next actions. The implementation follows clean architectural practices with proper separation of concerns.

## Features

- Analyze transcripts using OpenAI's API
- Get previously analyzed transcripts by ID
- In-memory storage of analysis results
- RESTful API with proper error handling
- Swagger documentation

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

### Get Transcript Analysis by ID

- **GET /transcripts/{id}**
  - Retrieves a previously generated analysis by ID

## Setup and Running

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
5. Access the Swagger documentation at: http://localhost:8000/swagger

## Testing

Run the tests with:

```
pytest
```

The tests include:
- Unit tests for the analyzer service
- API integration tests
