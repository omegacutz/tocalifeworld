from dataclasses import dataclass


@dataclass(frozen=True)
class TerrainTile:
    name: str
    color: tuple[int, int, int]
    walkable: bool = False


class GrassTile(TerrainTile):
    def __init__(self):
        super().__init__(name="grass", color=(126, 200, 80), walkable=False)


class RoadTile(TerrainTile):
    def __init__(self):
        super().__init__(name="road", color=(188, 176, 153), walkable=True)


class TreeTile(TerrainTile):
    def __init__(self):
        super().__init__(name="tree", color=(38, 132, 65), walkable=False)


class BuildingTile(TerrainTile):
    def __init__(self):
        super().__init__(name="building", color=(170, 110, 84), walkable=False)


class StartTile(TerrainTile):
    def __init__(self):
        super().__init__(name="start", color=(88, 214, 141), walkable=True)


class GoalTile(TerrainTile):
    def __init__(self):
        super().__init__(name="goal", color=(231, 76, 60), walkable=True)


GRASS_TILE = GrassTile()
ROAD_TILE = RoadTile()
TREE_TILE = TreeTile()
BUILDING_TILE = BuildingTile()
START_TILE = StartTile()
GOAL_TILE = GoalTile()
