import re


def clean_text(text: str) -> str:
    """Remove excess whitespace and control characters."""
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()
