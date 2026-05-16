import tiktoken


def count_tokens(text: str, model_name: str = "gpt-4o") -> int:
    """
    Count the number of tokens in a given text using tiktoken.
    Falls back to cl100k_base if model is not specifically supported.
    """
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))

def count_bundle_tokens(bundle_items: dict[str, str], format_type: str = "markdown") -> int:
    from contextkit.formatter import format_bundle
    formatted_text = format_bundle(bundle_items, format_type)
    return count_tokens(formatted_text)
