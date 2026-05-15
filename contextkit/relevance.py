import re
from pathlib import Path
from typing import Any, Dict


class RelevanceScorer:
    def __init__(self, root_dir: str, index_data: Dict[str, Any]):
        self.root_dir = Path(root_dir)
        self.index_data = index_data

    def score(self, task_description: str, use_semantic: bool = False) -> Dict[str, float]:
        scores = {}

        # Simple keyword extraction (remove stop words, keep alphanumeric)
        keywords = [word.lower() for word in re.findall(r'\b\w+\b', task_description)]
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'this', 'that', 'fix', 'bug', 'add', 'refactor'}
        keywords = [k for k in keywords if k not in stop_words and len(k) > 2]

        if not keywords:
            for file_path in self.index_data["files"]:
                scores[file_path] = 0.5 # Default score if no keywords
            return scores

        max_score = 0
        for file_path, file_data in self.index_data["files"].items():
            score = 0

            # Match in filename
            file_name = file_path.split('/')[-1].lower()
            for kw in keywords:
                if kw in file_name:
                    score += 5

            # Match in symbols
            for symbol in file_data.get("symbols", []):
                symbol_lower = symbol.lower()
                for kw in keywords:
                    if kw in symbol_lower:
                        score += 2

            # Match in content
            try:
                with open(self.root_dir / file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    for kw in keywords:
                        score += content.count(kw)
            except Exception:
                pass

            scores[file_path] = score
            if score > max_score:
                max_score = score

        # Normalize
        if max_score > 0:
            for file_path in scores:
                scores[file_path] = scores[file_path] / max_score

        # Semantic scoring
        if use_semantic:
            try:
                from sentence_transformers import SentenceTransformer
                from sklearn.metrics.pairwise import cosine_similarity

                model = SentenceTransformer('all-MiniLM-L6-v2')
                task_embedding = model.encode([task_description])

                for file_path, file_data in self.index_data["files"].items():
                    # Create document representation
                    doc = " ".join([file_path] + file_data.get("symbols", []))
                    doc_embedding = model.encode([doc])
                    sim = cosine_similarity(task_embedding, doc_embedding)[0][0]

                    # Combine scores (50/50 split)
                    scores[file_path] = 0.5 * scores[file_path] + 0.5 * float(sim)
            except ImportError:
                print("Warning: sentence-transformers not installed. Skipping semantic scoring.")

        return scores
