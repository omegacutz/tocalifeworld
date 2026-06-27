from dataclasses import dataclass, field

from .entities import CollectibleModel, NpcModel
from .terrain import TerrainTile


@dataclass
class TownModel:
    grid: list[list[TerrainTile]]
    start: tuple[int, int]
    goal: tuple[int, int]
    seed: int
    npcs: list[NpcModel] = field(default_factory=list)
    collectibles: list[CollectibleModel] = field(default_factory=list)

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

    def collect_at(self, x: int, y: int) -> bool:
        for index, item in enumerate(self.collectibles):
            if item.x == x and item.y == y:
                self.collectibles.pop(index)
                return True
        return False
