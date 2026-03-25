import pytest
from unittest.mock import patch
from engine.dom_server.rule_enforcer import RuleEnforcer

@pytest.fixture
def mock_rule_gen():
    with patch('engine.dom_server.rule_enforcer.RuleGenerator') as MockRuleGen:
        yield MockRuleGen

def test_discount_limit_extraction(mock_rule_gen):
    # Setup mock to return specific limits and security rules
    mock_instance = mock_rule_gen.return_value
    mock_instance.read_all.return_value = {
        "limits_md": "maximum discount: 20%",
        "security_md": "",
        "behavior_md": "",
        "skills_md": "skill: apply discount"
    }

    enforcer = RuleEnforcer("test_project")

    # Check that a discount within the limit is allowed
    result = enforcer.check("apply 10% discount")
    assert result["allowed"] is True

    # Check that a discount exceeding the limit is blocked
    result = enforcer.check("apply 25% discount")
    assert result["allowed"] is False
    assert "exceeds 20% maximum" in result["reason"]

def test_discount_limit_extraction_edge_cases(mock_rule_gen):
    # Test with varying spacing, case, and phrasing
    test_cases = [
        ("Maximum discount allowed: 15%", 15),
        ("maximum discount:   12%", 12),
        ("Maximum Discount limit is set to: 50%", 50),
        ("MAXIMUM DISCOUNT: 5%", 5),
    ]

    for rule_text, expected_limit in test_cases:
        mock_instance = mock_rule_gen.return_value
        mock_instance.read_all.return_value = {
            "limits_md": rule_text,
            "security_md": "",
            "behavior_md": "",
            "skills_md": "skill: apply discount"
        }

        enforcer = RuleEnforcer("test_project")

        # Test just below the limit
        result = enforcer.check(f"apply {expected_limit - 1}% discount")
        assert result["allowed"] is True, f"Failed for limit {expected_limit} with {expected_limit - 1}%"

        # Test at the limit
        result = enforcer.check(f"apply {expected_limit}% discount")
        assert result["allowed"] is True, f"Failed for limit {expected_limit} with {expected_limit}%"

        # Test above the limit
        result = enforcer.check(f"apply {expected_limit + 1}% discount")
        assert result["allowed"] is False, f"Failed for limit {expected_limit} with {expected_limit + 1}%"
        assert f"exceeds {expected_limit}% maximum" in result["reason"]

def test_discount_limit_default(mock_rule_gen):
    # Test fallback to default when rule is missing or malformed
    mock_instance = mock_rule_gen.return_value
    mock_instance.read_all.return_value = {
        "limits_md": "no discount limit specified here",
        "security_md": "some other rules",
        "behavior_md": "",
        "skills_md": "skill: apply discount"
    }

    enforcer = RuleEnforcer("test_project")

    # Default is 30%
    result = enforcer.check("apply 30% discount")
    assert result["allowed"] is True

    result = enforcer.check("apply 31% discount")
    assert result["allowed"] is False
    assert "exceeds 30% maximum" in result["reason"]
