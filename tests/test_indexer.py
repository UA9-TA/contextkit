from contextkit.indexer import Indexer


def test_indexer_builds_index(tmp_path):
    # Setup mock project
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "main.py").write_text("import os\ndef hello(): pass")

    indexer = Indexer(str(tmp_path))
    index_data = indexer.index()

    assert "files" in index_data
    assert "app/main.py" in index_data["files"]
    assert "hello" in index_data["files"]["app/main.py"]["symbols"]
    assert "os" in index_data["files"]["app/main.py"]["imports"]

def test_indexer_skips_hidden_files(tmp_path):
    (tmp_path / ".hidden.py").write_text("def hidden(): pass")
    (tmp_path / "visible.py").write_text("def visible(): pass")

    indexer = Indexer(str(tmp_path))
    index_data = indexer.index()

    assert ".hidden.py" not in index_data["files"]
    assert "visible.py" in index_data["files"]
