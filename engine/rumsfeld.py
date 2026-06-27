from collections.abc import Iterable


def _normalize_lines(items: Iterable[str]) -> list[str]:
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
    return {
        "known_knowns": _normalize_lines(known_knowns),
        "known_unknowns": _normalize_lines(known_unknowns),
        "unknown_unknowns": _normalize_lines(unknown_unknowns),
    }
