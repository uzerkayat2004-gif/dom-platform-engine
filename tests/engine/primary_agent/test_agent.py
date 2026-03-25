import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from engine.primary_agent.agent import PrimaryAgent
from engine.primary_agent.conversation import CreationStep

@pytest.fixture
def mock_dependencies():
    with patch('engine.primary_agent.agent.get_provider') as mock_get_provider, \
         patch('engine.primary_agent.agent.conversation_manager') as mock_conversation_manager, \
         patch('engine.primary_agent.agent.RuleGenerator') as mock_rule_generator, \
         patch('engine.primary_agent.agent.GlassBoxLogger') as mock_glass_box_logger:

        mock_provider = AsyncMock()
        mock_get_provider.return_value = mock_provider

        mock_state = MagicMock()
        mock_conversation_manager.get_or_create.return_value = mock_state

        mock_rule_gen_instance = MagicMock()
        mock_rule_generator.return_value = mock_rule_gen_instance

        yield {
            'provider': mock_provider,
            'state': mock_state,
            'rule_generator': mock_rule_gen_instance
        }

@pytest.mark.asyncio
async def test_handle_reviewing_rules_invalid_json(mock_dependencies):
    agent = PrimaryAgent(
        provider="dummy",
        api_key="dummy_key",
        project_id="dummy_project"
    )

    # Setup state
    agent.state.step = CreationStep.REVIEWING_RULES

    # Mock the LLM provider to return invalid JSON
    mock_dependencies['provider'].send_message.return_value = "This is not valid JSON."

    # Mock rule generator read_all
    mock_dependencies['rule_generator'].read_all.return_value = {"old": "rules"}

    # Call the method
    response, next_action = await agent._handle_reviewing_rules("Change this rule")

    # Assertions
    # Ensure provider was called
    mock_dependencies['provider'].send_message.assert_called_once()

    # Ensure save was NOT called due to invalid JSON
    mock_dependencies['rule_generator'].save.assert_not_called()

    # Ensure the method completes gracefully
    assert next_action == "show_rules"
