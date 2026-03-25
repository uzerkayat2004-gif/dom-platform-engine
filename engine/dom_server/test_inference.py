import pytest
from engine.dom_server.inference import DOMInference

def test_load_failure_when_model_path_does_not_exist(capsys):
    # Setup
    inference = DOMInference(project_id="test_missing_model_project")

    # Ensure the path really doesn't exist
    assert not inference.model_path.exists()

    # Execute
    result = inference.load()

    # Assert
    assert result is False
    assert inference.loaded is False

    # Check stdout
    captured = capsys.readouterr()
    assert f"DOM model not found at {inference.model_path}" in captured.out
