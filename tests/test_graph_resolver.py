from contextkit.graph_resolver import GraphResolver


def test_graph_resolver():
    index_data = {
        "files": {
            "a.py": {},
            "b.py": {},
            "c.py": {},
            "tests/test_a.py": {}
        },
        "edges": [
            ("a.py", "b.py"),
            ("b.py", "c.py")
        ]
    }

    resolver = GraphResolver(index_data)

    # Resolving a.py should bring in b.py, c.py and test_a.py
    resolved = resolver.resolve(["a.py"], max_depth=3)

    assert "a.py" in resolved
    assert "b.py" in resolved
    assert "c.py" in resolved
    assert "tests/test_a.py" in resolved
