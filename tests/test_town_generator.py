from collections import deque

import pytest

from engine.town_generator import TownGenerator


SCENARIOS = [
    {"width": 18, "height": 12, "seed": 1111},
    {"width": 24, "height": 16, "seed": 2222},
    {"width": 36, "height": 24, "seed": 3333},
]


def _has_walkable_path(town) -> bool:
    start = town.start
    goal = town.goal

    queue = deque([start])
    visited = {start}

    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            return True

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (nx, ny) in visited:
                continue
            if not town.is_walkable(nx, ny):
                continue
            visited.add((nx, ny))
            queue.append((nx, ny))

    return False


@pytest.mark.parametrize("scenario", SCENARIOS)
def test_town_generator_scenarios_produce_valid_town(scenario):
    generator = TownGenerator(width=scenario["width"], height=scenario["height"])
    town = generator.build_town(seed_value=scenario["seed"])

    assert town.width == scenario["width"]
    assert town.height == scenario["height"]
    assert town.start == (1, 1)
    assert town.goal == (scenario["width"] - 2, scenario["height"] - 2)
    assert town.is_walkable(*town.start)
    assert town.is_walkable(*town.goal)
    assert _has_walkable_path(town)


@pytest.mark.parametrize(
    "seed",
    [1010, 2020, 3030],
)
def test_town_generator_seed_is_reproducible(seed):
    generator = TownGenerator(width=20, height=14)

    town_a = generator.build_town(seed)
    town_b = generator.build_town(seed)

    names_a = [[tile.name for tile in row] for row in town_a.grid]
    names_b = [[tile.name for tile in row] for row in town_b.grid]

    assert names_a == names_b
    assert [(npc.x, npc.y) for npc in town_a.npcs] == [(npc.x, npc.y) for npc in town_b.npcs]
    assert [(item.x, item.y) for item in town_a.collectibles] == [(item.x, item.y) for item in town_b.collectibles]
