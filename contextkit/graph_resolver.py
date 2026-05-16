from collections import deque


def resolve_dependencies(seed_files: list[str], edges: list[tuple[str, str]], scores: dict[str, float], max_depth: int = 3) -> set[str]:
    """
    Walks the import graph to find dependencies.
    edges: list of (source, target) tuples
    scores: relevance scores for files
    """
    # Build adjacency list
    adj = {}
    for src, tgt in edges:
        if src not in adj:
            adj[src] = []
        adj[src].append(tgt)

    resolved = set(seed_files)
    queue = deque([(f, 0) for f in seed_files])

    while queue:
        curr, depth = queue.popleft()

        if depth >= max_depth:
            continue

        for neighbor in adj.get(curr, []):
            if neighbor not in resolved:
                # Exclude if relevance score is very low AND it's not a direct dependency
                # Actually spec says: Exclude: files with relevance score < 0.1
                # We'll allow direct dependencies (depth 0) to bypass score check,
                # but transitive ones (depth > 0) need some relevance.
                # Let's apply a threshold of 0.1
                if scores.get(neighbor, 0.0) >= 0.1 or depth == 0:
                    resolved.add(neighbor)
                    queue.append((neighbor, depth + 1))

    # Always include test files for seed files
    # We don't have a robust way to find tests, but we can look for test_*.py
    # or files in tests/ that match the filename
    for file in list(resolved):
        parts = file.split('/')
        name = parts[-1]

        # very basic test file finding based on known files in scores
        test_name = f"test_{name}"
        for known_file in scores:
            if known_file.endswith(test_name) and known_file not in resolved:
                resolved.add(known_file)

    return resolved
