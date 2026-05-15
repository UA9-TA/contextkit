from contextkit.bundle_builder import BundleBuilder
from contextkit.formatter import Formatter


def test_bundle_builder(tmp_path):
    # Setup files
    (tmp_path / "a.py").write_text("def a(): pass")
    (tmp_path / "b.py").write_text("def b(): pass")

    builder = BundleBuilder(str(tmp_path), max_tokens=100)
    bundle = builder.build({"a.py", "b.py"}, relevance_scores={"a.py": 1.0, "b.py": 0.5})

    assert "a.py" in bundle["files"]
    assert "b.py" in bundle["files"]

    formatted = Formatter.format_markdown(bundle["files"])
    assert "```python\n# a.py\ndef a(): pass\n```" in formatted
    assert "```python\n# b.py\ndef b(): pass\n```" in formatted
