from contextkit.config import get_project_root
from contextkit.token_counter import count_tokens


def build_bundle(resolved_files: set[str], seed_files: list[str], scores: dict[str, float], max_tokens: int, start_path: str = ".") -> dict[str, str]:
    root = get_project_root(start_path)
    bundle_items = {}
    current_tokens = 0

    # Priority groups
    p1_high_relevance = [] # > 0.8
    p2_tests = []
    p3_transitive = []

    for f in resolved_files:
        if scores.get(f, 0.0) > 0.8:
            p1_high_relevance.append(f)
        elif "test_" in f.split("/")[-1]:
            p2_tests.append(f)
        else:
            p3_transitive.append(f)

    # Include files by priority until budget is hit
    for group in [p1_high_relevance, p2_tests, p3_transitive]:
        for f in group:
            if current_tokens >= max_tokens:
                break

            full_path = root / f
            if full_path.exists():
                try:
                    content = full_path.read_text(encoding="utf-8")

                    # Very simple truncation logic for low relevance transitive dependencies
                    # (In a real scenario, this would parse AST to extract only signatures)
                    if group == p3_transitive and scores.get(f, 0.0) < 0.3 and f not in seed_files:
                        # naive truncation - just first 50 lines to catch imports and class/func defs
                        lines = content.splitlines()
                        if len(lines) > 50:
                            content = "\n".join(lines[:50]) + "\n... (truncated)"

                    tokens = count_tokens(content)
                    if current_tokens + tokens <= max_tokens:
                        bundle_items[f] = content
                        current_tokens += tokens
                    else:
                        # Skip if it would push us over
                        pass
                except Exception:
                    pass

    return bundle_items
