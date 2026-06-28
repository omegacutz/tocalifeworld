from dataclasses import dataclass


@dataclass(frozen=True)
class TerrainTile:
    """Immutable terrain descriptor used by grid cells across the town map.

    Args:
        name: Terrain identifier label.
        color: RGB color used to render the tile.
        walkable: Whether actors can stand on this tile.

    Returns:
        None.
    """

    name: str
    color: tuple[int, int, int]
    walkable: bool = False


class GrassTile(TerrainTile):
    """Concrete grass terrain type.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(self):
        """Create non-walkable grass terrain.

        Args:
            None.

        Returns:
            None.
        """
        super().__init__(name="grass", color=(126, 200, 80), walkable=False)


class RoadTile(TerrainTile):
    """Concrete road terrain type.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(self):
        """Create walkable road terrain.

        Args:
            None.

        Returns:
            None.
        """
        super().__init__(name="road", color=(188, 176, 153), walkable=True)


class TreeTile(TerrainTile):
    """Concrete tree terrain type.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(self):
        """Create non-walkable tree terrain.

        Args:
            None.

        Returns:
            None.
        """
        super().__init__(name="tree", color=(38, 132, 65), walkable=False)


class BuildingTile(TerrainTile):
    """Concrete building terrain type.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(self):
        """Create non-walkable building terrain.

        Args:
            None.

        Returns:
            None.
        """
        super().__init__(name="building", color=(170, 110, 84), walkable=False)


class StartTile(TerrainTile):
    """Concrete start-marker terrain type.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(self):
        """Create walkable start marker terrain.

        Args:
            None.

        Returns:
            None.
        """
        super().__init__(name="start", color=(88, 214, 141), walkable=True)


class GoalTile(TerrainTile):
    """Concrete goal-marker terrain type.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(self):
        """Create walkable goal marker terrain.

        Args:
            None.

        Returns:
            None.
        """
        super().__init__(name="goal", color=(231, 76, 60), walkable=True)


GRASS_TILE = GrassTile()
ROAD_TILE = RoadTile()
TREE_TILE = TreeTile()
BUILDING_TILE = BuildingTile()
START_TILE = StartTile()
GOAL_TILE = GoalTile()
