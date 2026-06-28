import pytest

from engine.rumsfeld import rumsfeld_pass

RUMSFELD_SCENARIOS = [
    {
        "name": "normal_lists",
        "known_knowns": ["Town has start", "Town has goal"],
        "known_unknowns": ["How many NPCs feel fun"],
        "unknown_unknowns": ["Generation edge case"],
        "expected_sizes": (2, 1, 1),
    },
    {
        "name": "trims_blank_entries",
        "known_knowns": ["  Map exists  ", ""],
        "known_unknowns": ["  ", "Need balancing"],
        "unknown_unknowns": ["   "],
        "expected_sizes": (1, 1, 0),
    },
]


@pytest.mark.parametrize(
    "scenario", RUMSFELD_SCENARIOS, ids=[s["name"] for s in RUMSFELD_SCENARIOS]
)
def test_rumsfeld_pass_datum_scenarios(scenario):
    result = rumsfeld_pass(
        known_knowns=scenario["known_knowns"],
        known_unknowns=scenario["known_unknowns"],
        unknown_unknowns=scenario["unknown_unknowns"],
    )

    assert set(result.keys()) == {"known_knowns", "known_unknowns", "unknown_unknowns"}

    kk, ku, uu = scenario["expected_sizes"]
    assert len(result["known_knowns"]) == kk
    assert len(result["known_unknowns"]) == ku
    assert len(result["unknown_unknowns"]) == uu


@pytest.mark.parametrize(
    "facts,questions,risks",
    [
        (["A"], ["B"], ["C"]),
        (["A", "A"], ["B", "B"], ["C", "C"]),
    ],
)
def test_rumsfeld_pass_preserves_input_order(facts, questions, risks):
    result = rumsfeld_pass(facts, questions, risks)

    assert result["known_knowns"] == [item.strip() for item in facts]
    assert result["known_unknowns"] == [item.strip() for item in questions]
    assert result["unknown_unknowns"] == [item.strip() for item in risks]
