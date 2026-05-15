from contextkit.relevance import RelevanceScorer


def test_relevance_scorer():
    index_data = {
        "files": {
            "auth/validators.py": {
                "symbols": ["validate_token"],
            },
            "payment/processor.py": {
                "symbols": ["process_payment"],
            }
        }
    }

    scorer = RelevanceScorer(".", index_data)
    scores = scorer.score("fix the JWT token validation bug")

    # auth/validators.py should score higher because "token" and "validation" are matched in symbols/filename
    assert scores["auth/validators.py"] > scores["payment/processor.py"]
