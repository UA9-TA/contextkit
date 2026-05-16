from pathlib import Path

import pytest
from typer.testing import CliRunner

from contextkit.cli import app
from contextkit.config import INDEX_FILE_NAME

runner = CliRunner()

@pytest.fixture
def sample_project_dir(monkeypatch):
    """Run tests in the sample project directory."""
    project_root = Path(__file__).parent.parent
    sample_dir = project_root / "tests/fixtures/sample_project"

    # Use monkeypatch to change working directory
    monkeypatch.chdir(sample_dir)

    # Ensure index is removed before and after test
    index_file = sample_dir / INDEX_FILE_NAME
    if index_file.exists():
        index_file.unlink()

    yield sample_dir

    if index_file.exists():
        index_file.unlink()

def test_index_command(sample_project_dir):
    result = runner.invoke(app, ["index", "--update"])
    assert result.exit_code == 0
    assert "Building index..." in result.stdout
    assert "Index built with" in result.stdout

    # Check that index file was created
    index_file = sample_project_dir / INDEX_FILE_NAME
    assert index_file.exists()

def test_build_command(sample_project_dir, mocker):
    # Mock pyperclip
    mocker.patch("pyperclip.copy")

    # First index
    runner.invoke(app, ["index", "--update"])

    result = runner.invoke(app, ["build", "fix JWT validation bug", "--copy"])
    assert result.exit_code == 0

    # Output should show reduction
    assert "fewer tokens" in result.stdout

    # Validators and dependencies should be included
    assert "validators.py" in result.stdout
    assert "models.py" in result.stdout
    assert "exceptions.py" in result.stdout
    assert "test_validators.py" in result.stdout

    # Processor should NOT be included
    assert "processor.py" not in result.stdout

    # Clipboard should be called
    import pyperclip
    pyperclip.copy.assert_called_once()
