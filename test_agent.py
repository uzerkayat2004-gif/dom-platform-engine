import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

from engine.primary_agent.agent import PrimaryAgent
from engine.primary_agent.conversation import CreationStep

@pytest.mark.asyncio
async def test_fallback_rules_on_invalid_json():
    """
    Test that invalid JSON from the provider triggers the fallback rules logic
    during the QUESTIONING step when rules are generated.
    """
    # Setup mock provider to return invalid JSON
    with patch('engine.primary_agent.agent.get_provider') as mock_get_provider:
        mock_provider = MagicMock()
        mock_provider.send_message = AsyncMock(return_value="Invalid JSON Response")
        mock_get_provider.return_value = mock_provider

        # Setup conversation state
        with patch('engine.primary_agent.agent.conversation_manager') as mock_conv_manager:
            mock_state = MagicMock()
            mock_state.step = CreationStep.QUESTIONING
            mock_state.get_messages_for_api.return_value = []
            mock_conv_manager.get_or_create.return_value = mock_state

            # Setup RuleGenerator mock
            with patch('engine.primary_agent.agent.RuleGenerator') as mock_rule_gen:
                mock_gen_instance = MagicMock()
                mock_rule_gen.return_value = mock_gen_instance
                mock_gen_instance.save = MagicMock()
                mock_gen_instance.save.return_value = ["security.md", "behavior.md", "limits.md", "skills.md"]

                # Create agent
                agent = PrimaryAgent(provider="dummy", api_key="dummy", project_id="test_proj")

                # Mock get_fallback_rules to spy on it and assert it is called
                with patch.object(agent, '_get_fallback_rules', wraps=agent._get_fallback_rules) as mock_get_fallback:

                    # Run the questioning step
                    await agent._handle_questioning("Here are my answers")

                    # Verify fallback was called
                    mock_get_fallback.assert_called_once()

                    # Verify rule_generator.save was called with fallback rules
                    fallback_rules = agent._get_fallback_rules()
                    mock_gen_instance.save.assert_called_once_with(fallback_rules)
