import uuid
from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.domain.models import TranscriptAnalysis


@pytest.fixture
def client():
    with patch("app.adapters.openai.OpenAIAdapter") as mock_adapter_class:
        # Configure the mock to return appropriate values
        mock_adapter = mock_adapter_class.return_value
        mock_adapter.run_completion.return_value = type(
            "Response",
            (),
            {"summary": "Test summary", "action_items": ["Action 1", "Action 2"]}
        )
        
        app = create_app()
        with TestClient(app) as test_client:
            yield test_client


def test_analyze_transcript_get(client):
    # Arrange
    test_transcript = "This is a test transcript"
    
    # Act
    response = client.get(f"/transcripts/analyze?transcript={test_transcript}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["summary"] == "Test summary"
    assert data["action_items"] == ["Action 1", "Action 2"]


def test_analyze_transcript_post(client):
    # Arrange
    request_data = {"transcript": "This is a test transcript"}
    
    # Act
    response = client.post("/transcripts/analyze", json=request_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["summary"] == "Test summary"
    assert data["action_items"] == ["Action 1", "Action 2"]


def test_analyze_empty_transcript(client):
    # Act - using GET endpoint
    response = client.get("/transcripts/analyze?transcript=")
    
    # Assert
    assert response.status_code == 400
    assert "detail" in response.json()
    
    # Act - using POST endpoint
    response = client.post("/transcripts/analyze", json={"transcript": ""})
    
    # Assert
    assert response.status_code == 400
    assert "detail" in response.json()


def test_get_analysis_by_id(client):
    # Arrange - first create an analysis
    test_transcript = "This is a test transcript"
    create_response = client.get(f"/transcripts/analyze?transcript={test_transcript}")
    analysis_id = create_response.json()["id"]
    
    # Act
    response = client.get(f"/transcripts/{analysis_id}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == analysis_id
    assert data["summary"] == "Test summary"
    assert data["action_items"] == ["Action 1", "Action 2"]


def test_get_analysis_not_found(client):
    # Arrange
    nonexistent_id = str(uuid.uuid4())
    
    # Act
    response = client.get(f"/transcripts/{nonexistent_id}")
    
    # Assert
    assert response.status_code == 404
    assert "detail" in response.json() 