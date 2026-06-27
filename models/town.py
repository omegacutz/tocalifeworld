from dataclasses import dataclass

from .entities import NpcModel
from .terrain import TerrainTile


@dataclass
class TownModel:
    grid: list[list[TerrainTile]]
    start: tuple[int, int]
    goal: tuple[int, int]
    seed: int
    npcs: list[NpcModel]

    @property
    def width(self) -> int:
        return len(self.grid[0])

    @property
    def height(self) -> int:
        return len(self.grid)

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def tile_at(self, x: int, y: int) -> TerrainTile:
        return self.grid[y][x]

    def is_walkable(self, x: int, y: int) -> bool:
        return self.in_bounds(x, y) and self.tile_at(x, y).walkable
