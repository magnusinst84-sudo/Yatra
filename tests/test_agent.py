import pytest
from unittest.mock import patch, MagicMock
from backend.agent.world_state import generate_world_state
from backend.models import WorldState, AgentError, ValidationError
from google.genai.errors import APIError

@pytest.mark.asyncio
async def test_generate_world_state_happy_path():
    # We will use real generation for the happy path but we need to ensure the key is set.
    # To save time and quota in automated tests, one could mock this, but the prompt asks to 
    # test "what the code actually does". I'll use real generation for the happy path.
    place = "Taxila"
    era = "Maurya Empire"
    rag = "Taxila was a famous ancient university."
    state = await generate_world_state(place, era, rag, "test_user")
    
    assert isinstance(state, WorldState)
    assert 3 <= len(state.stops) <= 5
    for stop in state.stops:
        word_count = len(stop.narration_script.split())
        assert word_count >= 120, f"Narration too short: {word_count} words"
        assert len(stop.daily_life_facts) >= 3

@pytest.mark.asyncio
async def test_generate_world_state_empty_rag():
    # Empty RAG context shouldn't crash the agent.
    place = "Taxila"
    era = "Maurya Empire"
    state = await generate_world_state(place, era, "", "test_user")
    assert isinstance(state, WorldState)
    assert 3 <= len(state.stops) <= 5

@pytest.mark.asyncio
async def test_generate_world_state_retry_exhaustion():
    # Mock the Gemini client to raise a persistent non-quota APIError (e.g. 500) 
    # and confirm AgentError is raised.
    with patch("backend.agent.gemini_client.get_gemini_client") as mock_get_client:
        mock_client = MagicMock()
        # APIError in genai SDK takes (message, code, status) etc. We'll mock the exception directly 
        # or mock the generate_content method to raise it.
        # It's easier to patch _call_model inside world_state to raise GeminiAPIError
        from google.genai.errors import APIError
        # Provide response_json as required by APIError
        with patch("backend.agent.world_state._call_model", side_effect=APIError("Mocked failure", response_json={})):
            with pytest.raises(AgentError) as exc_info:
                await generate_world_state("FailCity", "FailEra", "Rag", "user")
            
            assert "exhausted retries" in str(exc_info.value).lower() or "gemini api failure after" in str(exc_info.value).lower()
