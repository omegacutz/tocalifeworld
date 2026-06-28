from dataclasses import dataclass, field

from .entities import CollectibleModel
from .npc import NpcModel
from .terrain import TerrainTile


@dataclass
class TownModel:
    """Container for generated map tiles and all runtime world entities.

    Args:
        grid: 2D terrain grid for the map.
        start: Start tile coordinate.
        goal: Goal tile coordinate.
        seed: Seed used to generate this town.
        npcs: NPC actors currently in the town.
        collectibles: Collectible items currently in the town.

    Returns:
        None.
    """

    grid: list[list[TerrainTile]]
    start: tuple[int, int]
    goal: tuple[int, int]
    seed: int
    npcs: list[NpcModel] = field(default_factory=list)
    collectibles: list[CollectibleModel] = field(default_factory=list)

    @property
    def width(self) -> int:
        """Return grid width in tiles.

        Args:
            None.

        Returns:
            int: Number of columns in the map grid.
        """
        return len(self.grid[0])

    @property
    def height(self) -> int:
        """Return grid height in tiles.

        Args:
            None.

        Returns:
            int: Number of rows in the map grid.
        """
        return len(self.grid)

    def in_bounds(self, x: int, y: int) -> bool:
        """Check whether a tile coordinate is inside map boundaries.

        Args:
            x: Tile x coordinate.
            y: Tile y coordinate.

        Returns:
            bool: True when the coordinate is inside the map; otherwise False.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def tile_at(self, x: int, y: int) -> TerrainTile:
        """Fetch terrain tile data at a given tile coordinate.

        Args:
            x: Tile x coordinate.
            y: Tile y coordinate.

        Returns:
            TerrainTile: Terrain descriptor at the requested coordinate.
        """
        return self.grid[y][x]

    def is_walkable(self, x: int, y: int) -> bool:
        """Return whether a tile can be occupied by moving actors.

        Args:
            x: Tile x coordinate.
            y: Tile y coordinate.

        Returns:
            bool: True when tile is in bounds and walkable.
        """
        return self.in_bounds(x, y) and self.tile_at(x, y).walkable

    def collect_at(self, x: int, y: int) -> bool:
        """Remove and confirm collectible pickup at a tile when present.

        Args:
            x: Tile x coordinate.
            y: Tile y coordinate.

        Returns:
            bool: True when a collectible was removed; otherwise False.
        """
        for index, item in enumerate(self.collectibles):
            if item.x == x and item.y == y:
                self.collectibles.pop(index)
                return True
        return False
