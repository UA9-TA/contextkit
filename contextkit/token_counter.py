import tiktoken


class TokenCounter:
    def __init__(self, model_name: str = "cl100k_base"):
        try:
            self.encoding = tiktoken.get_encoding(model_name)
        except Exception:
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def count(self, text: str) -> int:
        if not text:
            return 0
        return len(self.encoding.encode(text))
