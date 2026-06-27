import pytest

from models.terrain import GOAL_TILE, ROAD_TILE, TREE_TILE
from models.town import TownModel


@pytest.mark.parametrize(
    "x,y,expected",
    [
        (0, 0, True),
        (1, 0, False),
        (1, 1, True),
        (5, 5, False),
    ],
)
def test_town_model_walkability_scenarios(x, y, expected):
    grid = [
        [ROAD_TILE, TREE_TILE],
        [ROAD_TILE, GOAL_TILE],
    ]
    town = TownModel(grid=grid, start=(0, 0), goal=(1, 1), seed=1, npcs=[])

    assert town.is_walkable(x, y) is expected
