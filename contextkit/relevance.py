import re

from contextkit.config import get_project_root


def extract_keywords(task_desc: str) -> set[str]:
    # Very basic keyword extraction: words >= 3 chars
    words = re.findall(r'\b\w{3,}\b', task_desc.lower())
    # Exclude common stop words (simplified list)
    stopwords = {"the", "and", "this", "that", "with", "for", "from", "have", "are", "was", "not"}
    return {w for w in words if w not in stopwords}

def score_relevance(task_desc: str, index_data: dict, start_path: str = ".", use_semantic: bool = False) -> dict[str, float]:
    """
    Score files based on keyword matches (and optionally semantic similarity).
    Returns a dict mapping file_path to score (0.0 to 1.0).
    """
    keywords = extract_keywords(task_desc)
    scores = {}

    root = get_project_root(start_path)

    files_data = index_data.get("files", {})

    max_score = 0.0
    raw_scores = {}

    for path, data in files_data.items():
        score = 0.0

        # Check filename
        path_lower = path.lower()
        for kw in keywords:
            if kw in path_lower:
                score += 2.0

        # Check symbols
        symbols = data.get("symbols", [])
        for sym in symbols:
            sym_lower = sym.lower()
            for kw in keywords:
                if kw in sym_lower:
                    score += 1.0

        # Check file content loosely for keywords
        full_path = root / path
        if full_path.exists():
            try:
                content = full_path.read_text(encoding="utf-8").lower()
                for kw in keywords:
                    score += 0.1 * content.count(kw)
            except Exception:
                pass

        raw_scores[path] = score
        if score > max_score:
            max_score = score

    # Normalize scores
    if max_score > 0:
        for path in raw_scores:
            scores[path] = min(1.0, raw_scores[path] / max_score)
    else:
        scores = {p: 0.0 for p in raw_scores}

    if use_semantic:
        try:
            import numpy as np
            from sentence_transformers import SentenceTransformer

            # Simple fallback to a fast small model
            model = SentenceTransformer("all-MiniLM-L6-v2")
            task_emb = model.encode(task_desc)

            sem_scores = {}
            for path in files_data.keys():
                # embed filename and symbols
                doc = path + " " + " ".join(files_data[path].get("symbols", []))
                doc_emb = model.encode(doc)

                # cosine similarity
                cos_sim = np.dot(task_emb, doc_emb) / (np.linalg.norm(task_emb) * np.linalg.norm(doc_emb))
                sem_scores[path] = max(0.0, float(cos_sim))

            # Combine scores (simple average)
            for path in scores:
                scores[path] = (scores[path] + sem_scores.get(path, 0.0)) / 2.0

        except ImportError:
            # Semantic search not available, stick to keyword
            pass

    return scores
