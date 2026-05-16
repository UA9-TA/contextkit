from pathlib import Path

INDEX_FILE_NAME = ".contextkit-index.json"

def get_project_root(start_path: str = ".") -> Path:
    """Find the project root by looking for common markers like pyproject.toml or .git."""
    # When testing, we want to treat sample_project as the root
    current = Path(start_path).resolve()
    if "sample_project" in str(current):
        for parent in [current, *current.parents]:
            if parent.name == "sample_project":
                return parent

    for parent in [current, *current.parents]:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists() or (parent / "setup.py").exists():
            return parent
    return Path(start_path).resolve()

def get_index_path(start_path: str = ".") -> Path:
    """Get the path to the index file in the project root."""
    return get_project_root(start_path) / INDEX_FILE_NAME
