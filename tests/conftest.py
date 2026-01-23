"""Global pytest fixtures and configuration"""

import uuid
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock, Mock
import httpx
from typing import AsyncGenerator, Generator, Any
import asyncio
from fastapi.testclient import TestClient

from app.domain.models import TranscriptAnalysis
from app.ports import LLm


def pytest_configure(config):
    """Register the asyncio marker"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio coroutine"
    )


@pytest.fixture
def mock_domain_model():
    """Return a mock TranscriptAnalysis object with a valid UUID"""
    return TranscriptAnalysis(
        id=uuid.uuid4(),
        summary='Test summary',
        action_items=['Action 1', 'Action 2']
    )


class MockDTO:
    """Mock DTO that allows to_domain_model to be called"""
    def __init__(self, mock_model):
        self.summary = "Test summary"
        self.action_items = ["Action 1", "Action 2"]
        self._mock_model = mock_model
        
    def to_domain_model(self, id=None):
        """Return the mock domain model"""
        return self._mock_model


class MockLLM(LLm):
    """Mock LLM implementation for testing"""
    def __init__(self, mock_dto):
        self.mock_dto = mock_dto
        
    def run_completion(self, system_prompt, user_prompt, dto):
        return self.mock_dto
        
    async def run_completion_async(self, system_prompt, user_prompt, dto):
        return self.mock_dto


@pytest.fixture
def mock_llm(mock_domain_model) -> Generator[MockLLM, None, None]:
    """Mock LLM adapter for testing"""
    mock_dto = MockDTO(mock_domain_model)
    yield MockLLM(mock_dto)


@pytest.fixture
def client(mock_llm) -> Generator[TestClient, None, None]:
    """Test client with mocked dependencies"""
    from app.main import create_app
    
    app = create_app(llm_adapter=mock_llm)
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def async_client(mock_llm) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async client for testing."""
    from app.main import create_app
    
    app = create_app(llm_adapter=mock_llm)
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac 