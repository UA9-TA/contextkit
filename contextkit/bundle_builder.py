from pathlib import Path
from typing import Any, Dict, Set

from .token_counter import TokenCounter


class BundleBuilder:
    def __init__(self, root_dir: str, max_tokens: int = 30000):
        self.root_dir = Path(root_dir)
        self.max_tokens = max_tokens
        self.counter = TokenCounter()

    def build(self, files_to_include: Set[str], relevance_scores: Dict[str, float]) -> Dict[str, Any]:
        bundle = {}
        total_tokens = 0

        # Sort files by relevance score (descending), then tests
        def sort_key(f):
            score = relevance_scores.get(f, 0)
            is_test = 1 if 'test' in f.lower() else 0
            return (score, is_test)

        sorted_files = sorted(list(files_to_include), key=sort_key, reverse=True)

        for file_path in sorted_files:
            full_path = self.root_dir / file_path
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception:
                continue

            tokens = self.counter.count(content)

            # Simple inclusion policy for now: include whole file if budget allows
            if total_tokens + tokens <= self.max_tokens:
                bundle[file_path] = content
                total_tokens += tokens
            else:
                # If a file doesn't fit, we stop (or we could truncate, but let's keep it simple for now)
                # Actually, let's include as much as possible
                break

        return {
            "files": bundle,
            "total_tokens": total_tokens
        }
