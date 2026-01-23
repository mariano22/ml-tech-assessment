from unittest.mock import patch, Mock
import pytest

from app import configurations
from tests.adapters import mock_data
from app.adapters import openai
from app.dto.analysis import AnalysisDTO
from app.domain.models import TranscriptAnalysis
from tests.conftest import MockDTO


@pytest.fixture
def mock_openai_client():
    """Mock the OpenAI client for testing"""
    with patch("openai.OpenAI") as mock_client_class, \
         patch("openai.AsyncOpenAI") as mock_async_client_class:
        # Configure mock client
        mock_client = mock_client_class.return_value
        mock_async_client = mock_async_client_class.return_value
        
        # Create a mock DTO
        mock_dto = MockDTO(TranscriptAnalysis(
            summary="Test summary",
            action_items=["Action 1", "Action 2"]
        ))
        
        # Setup the client.beta.chat.completions.parse method
        mock_completion = mock_client.beta.chat.completions
        mock_completion.parse = Mock(return_value=type('Response', (), {
            'choices': [
                type('Choice', (), {
                    'message': type('Message', (), {
                        'parsed': mock_dto
                    })
                })
            ]
        }))
        
        # Same for async version
        mock_async_completion = mock_async_client.beta.chat.completions
        mock_async_completion.parse = Mock(return_value=type('Response', (), {
            'choices': [
                type('Choice', (), {
                    'message': type('Message', (), {
                        'parsed': mock_dto
                    })
                })
            ]
        }))
        
        yield


def test_openai_adapter(mock_openai_client) -> None:
    """Test the OpenAI adapter with mocked responses"""
    # Configuration
    env_variables = configurations.EnvConfigs()

    system_prompt = mock_data.SYSTEM_PROMPT
    raw_user_prompt = mock_data.RAW_USER_PROMPT
    transcript = mock_data.TRANSCRIPT

    user_prompt = raw_user_prompt.format(transcript=transcript)
    openai_adapter = openai.OpenAIAdapter(api_key="dummy_key", model="gpt-4")

    # Action - This should use the mocked OpenAI client
    response = openai_adapter.run_completion(system_prompt, user_prompt, AnalysisDTO)

    # Assert
    assert hasattr(response, "summary")
    assert hasattr(response, "action_items")
    assert response.summary == "Test summary"
    assert response.action_items == ["Action 1", "Action 2"]
    
    # Test conversion to domain model
    domain_model = response.to_domain_model()
    assert domain_model.summary == response.summary
    assert domain_model.action_items == response.action_items
