from pathlib import Path
from typing import Any, Dict, List, Set


class GraphResolver:
    def __init__(self, index_data: Dict[str, Any]):
        self.index_data = index_data
        self.adj_list = {}
        for file in index_data["files"]:
            self.adj_list[file] = []
        for src, dst in index_data.get("edges", []):
            if src in self.adj_list:
                self.adj_list[src].append(dst)

    def resolve(self, seed_files: List[str], max_depth: int = 3, min_relevance: float = 0.1, relevance_scores: Dict[str, float] = None) -> Set[str]:
        if relevance_scores is None:
            relevance_scores = {}

        included_files = set(seed_files)
        queue = [(f, 0) for f in seed_files]

        while queue:
            current_file, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            for neighbor in self.adj_list.get(current_file, []):
                if neighbor not in included_files:
                    # check relevance
                    score = relevance_scores.get(neighbor, 0)
                    if score >= min_relevance or neighbor.startswith('tests/') or '/test_' in neighbor or neighbor.endswith('_test.py') or len(relevance_scores) == 0:
                         included_files.add(neighbor)
                         queue.append((neighbor, depth + 1))

        # Also ensure test files corresponding to seed files are included
        for f in seed_files:
            # simple heuristic: test_filename.py or filename_test.py
            filename = Path(f).name
            test_names = [f"test_{filename}", filename.replace(".py", "_test.py")]

            for test_name in test_names:
                for candidate in self.index_data["files"]:
                    if candidate.endswith(test_name) and candidate not in included_files:
                        included_files.add(candidate)

        return included_files
