import re


def normalize_whitespace(text: str) -> str:
    """
    Normalize excessive whitespace and line breaks.
    """

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()