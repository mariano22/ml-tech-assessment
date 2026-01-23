import uuid
import pytest
from fastapi.testclient import TestClient
import httpx

from app.domain.models import TranscriptAnalysis


def test_create_transcript_analysis(client):
    """Test that the POST /transcripts endpoint works correctly."""
    # Arrange
    request_data = {"transcript": "This is a test transcript"}
    
    # Act
    response = client.post("/transcripts", json=request_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["summary"] == "Test summary"
    assert data["action_items"] == ["Action 1", "Action 2"]


def test_create_empty_transcript(client):
    """Test that empty transcripts are rejected with appropriate error messages."""
    # Act - using POST endpoint
    response = client.post("/transcripts", json={"transcript": ""})
    
    # Assert
    assert response.status_code == 400
    assert "detail" in response.json()


def test_list_transcript_ids(client):
    """Test that listing all analysis IDs works correctly."""
    # Arrange - first create an analysis
    request_data = {"transcript": "This is a test transcript"}
    create_response = client.post("/transcripts", json=request_data)
    analysis_id = create_response.json()["id"]
    
    # Act
    response = client.get("/transcripts")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert analysis_id in data
    # Check that data items are UUIDs and not full objects
    for id_str in data:
        # Verify we can parse it as a UUID (would raise ValueError if invalid)
        uuid.UUID(id_str)


def test_get_analysis_by_id(client):
    """Test that getting an analysis by ID works correctly."""
    # Arrange - first create an analysis
    test_transcript = "This is a test transcript"
    create_response = client.post("/transcripts", json={"transcript": test_transcript})
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
    response = await async_client.post("/transcripts/batch", json=batch_request)
    
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
    response = await async_client.post("/transcripts/batch", json=batch_request)
    
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
    response = await async_client.post("/transcripts/batch", json=batch_request)
    
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