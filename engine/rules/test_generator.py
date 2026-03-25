import pytest
from pathlib import Path
from engine.rules.generator import RuleGenerator

@pytest.fixture
def temp_project_dir(tmp_path):
    project_id = "test_project"
    # RuleGenerator creates projects/{project_id}/rules relative to CWD
    return project_id, tmp_path

def test_validate_all_valid(temp_project_dir, monkeypatch):
    project_id, tmp_path = temp_project_dir
    monkeypatch.chdir(tmp_path)

    generator = RuleGenerator(project_id)

    # Create valid files
    for filename in generator.FILE_NAMES.values():
        file_path = generator.rules_dir / filename
        file_path.write_text("some content")

    results = generator.validate()

    assert results["security_md"] is True
    assert results["behavior_md"] is True
    assert results["limits_md"] is True
    assert results["skills_md"] is True
    assert results["all_valid"] is True

def test_validate_some_missing(temp_project_dir, monkeypatch):
    project_id, tmp_path = temp_project_dir
    monkeypatch.chdir(tmp_path)

    generator = RuleGenerator(project_id)

    # Create only some valid files
    valid_keys = ["behavior_md", "limits_md", "skills_md"]
    for key in valid_keys:
        filename = generator.FILE_NAMES[key]
        file_path = generator.rules_dir / filename
        file_path.write_text("some content")

    results = generator.validate()

    assert results["security_md"] is False
    assert results["behavior_md"] is True
    assert results["limits_md"] is True
    assert results["skills_md"] is True
    assert results["all_valid"] is False

def test_validate_some_empty(temp_project_dir, monkeypatch):
    project_id, tmp_path = temp_project_dir
    monkeypatch.chdir(tmp_path)

    generator = RuleGenerator(project_id)

    # Create all files, but one is empty
    for key, filename in generator.FILE_NAMES.items():
        file_path = generator.rules_dir / filename
        if key == "security_md":
            file_path.write_text("")
        else:
            file_path.write_text("some content")

    results = generator.validate()

    assert results["security_md"] is False
    assert results["behavior_md"] is True
    assert results["limits_md"] is True
    assert results["skills_md"] is True
    assert results["all_valid"] is False

def test_validate_all_missing(temp_project_dir, monkeypatch):
    project_id, tmp_path = temp_project_dir
    monkeypatch.chdir(tmp_path)

    generator = RuleGenerator(project_id)
    # No files created (except the directory itself by __init__)

    results = generator.validate()

    assert results["security_md"] is False
    assert results["behavior_md"] is False
    assert results["limits_md"] is False
    assert results["skills_md"] is False
    assert results["all_valid"] is False
