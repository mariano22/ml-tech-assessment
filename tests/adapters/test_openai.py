from app import configurations
from tests.adapters import mock_data
from app.adapters import openai
from app.dto.analysis import AnalysisDTO


def test_openai_adapter() -> None:
    # Configuration
    env_variables = configurations.EnvConfigs()

    system_prompt = mock_data.SYSTEM_PROMPT
    raw_user_prompt = mock_data.RAW_USER_PROMPT
    transcript = mock_data.TRANSCRIPT

    user_prompt = raw_user_prompt.format(
        transcript=transcript)
    openai_adapter = openai.OpenAIAdapter(env_variables.OPENAI_API_KEY, env_variables.OPENAI_MODEL)

    # action
    response = openai_adapter.run_completion(system_prompt, user_prompt, AnalysisDTO)
    serialized_response = response.model_dump()

    # assert
    print(serialized_response)
    assert "summary" in serialized_response.keys()
    assert "action_items" in serialized_response.keys()
    
    # Test conversion to domain model
    domain_model = response.to_domain_model()
    assert domain_model.summary == response.summary
    assert domain_model.action_items == response.action_items
