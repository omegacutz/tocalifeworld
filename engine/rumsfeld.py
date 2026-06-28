from collections.abc import Iterable


def _normalize_lines(items: Iterable[str]) -> list[str]:
    """Strip each line and drop empty values.

    Args:
        items: Sequence of text entries to normalize.

    Returns:
        list[str]: Cleaned, non-empty lines in original order.
    """
    normalized: list[str] = []
    for item in items:
        value = item.strip()
        if value:
            normalized.append(value)
    return normalized


def rumsfeld_pass(
    known_knowns: Iterable[str],
    known_unknowns: Iterable[str],
    unknown_unknowns: Iterable[str],
) -> dict[str, list[str]]:
    """Build a normalized Rumsfeld summary payload.

    Args:
        known_knowns: Facts confirmed as true.
        known_unknowns: Questions that are clearly identified.
        unknown_unknowns: Plausible blind spots or unmodeled risks.

    Returns:
        dict[str, list[str]]: Normalized lists keyed by Rumsfeld category names.
    """
    return {
        "known_knowns": _normalize_lines(known_knowns),
        "known_unknowns": _normalize_lines(known_unknowns),
        "unknown_unknowns": _normalize_lines(unknown_unknowns),
    }
