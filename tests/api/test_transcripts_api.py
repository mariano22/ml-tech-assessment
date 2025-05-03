import uuid
import pytest
from fastapi.testclient import TestClient
import httpx

from app.domain.models import TranscriptAnalysis


def test_analyze_transcript_get(client):
    """Test that the GET /transcripts/analyze endpoint works correctly."""
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
    """Test that the POST /transcripts/analyze endpoint works correctly."""
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
    """Test that empty transcripts are rejected with appropriate error messages."""
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
    """Test that getting an analysis by ID works correctly."""
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
    """Test that appropriate error is returned when analysis is not found."""
    # Arrange
    nonexistent_id = str(uuid.uuid4())
    
    # Act
    response = client.get(f"/transcripts/{nonexistent_id}")
    
    # Assert
    assert response.status_code == 404
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_analyze_batch(async_client):
    """Test that batch analysis works correctly for multiple transcripts."""
    # Arrange
    batch_request = {
        "transcripts": [
            "Transcript 1",
            "Transcript 2",
            "Transcript 3"
        ]
    }
    
    # Act
    response = await async_client.post("/transcripts/analyze/batch", json=batch_request)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 3
    
    # Check all results have correct structure
    for result in data["results"]:
        assert "id" in result
        assert result["summary"] == "Test summary"
        assert result["action_items"] == ["Action 1", "Action 2"]


@pytest.mark.asyncio
async def test_analyze_batch_empty_list(async_client):
    """Test that batch analysis rejects empty transcript lists."""
    # Arrange
    batch_request = {"transcripts": []}
    
    # Act
    response = await async_client.post("/transcripts/analyze/batch", json=batch_request)
    
    # Assert
    assert response.status_code == 400
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_analyze_batch_with_empty_transcript(async_client):
    """Test that batch analysis rejects lists containing empty transcripts."""
    # Arrange
    batch_request = {
        "transcripts": ["Valid transcript", ""]
    }
    
    # Act
    response = await async_client.post("/transcripts/analyze/batch", json=batch_request)
    
    # Assert
    assert response.status_code == 400
    assert "detail" in response.json()


def test_health_check(client):
    """Test that the health check endpoint returns 200 OK and the expected response."""
    # Act
    response = client.get("/health")
    
    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"} 