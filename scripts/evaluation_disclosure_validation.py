"""Bounded disclosure shape checks; never an NLP truth/keyword oracle."""
import re

# Whole-value placeholder vocabulary, not forbidden words in real prose.
PLACEHOLDER_PARTS = frozenset({"todo", "tbd", "tba", "fixme", "placeholder", "fabricated",
                               "unsubstantiated", "none", "unknown", "na",
                               "limitation", "limitations", "disclosure", "pending", "unresolved"})


def is_placeholder(value: str) -> bool:
    words = re.findall(r"[^\W_]+", value.casefold(), re.UNICODE)
    return value.strip().rstrip(".").casefold() == "n/a" or not words or all(word in PLACEHOLDER_PARTS for word in words)


def disclosure_error(value, *, allow_none=False):
    if not isinstance(value, str) or not value.strip():
        return "requires disclosure"
    if allow_none and value.strip().rstrip(".").casefold() == "none":
        return None
    if is_placeholder(value):
        return "has placeholder disclosure rather than substantive content"
    if len(value.strip()) < 12:
        return "requires substantive disclosure (at least 12 characters)"
    return None


def pending_todo(value: str) -> bool:
    """An unquoted leading TODO marker declares pending work, not completion."""
    return re.match(r"^TODO\b", value.strip(), re.I) is not None
