import random

from models.entities import NpcModel
from models.terrain import BUILDING_TILE, GOAL_TILE, GRASS_TILE, ROAD_TILE, START_TILE, TREE_TILE
from models.town import TownModel

from .constants import BUILDING_CHANCE, GRID_H, GRID_W, TREE_CHANCE


class TownGenerator:
    def __init__(self, width: int = GRID_W, height: int = GRID_H):
        self.width = width
        self.height = height

    def generate_path(self, start: tuple[int, int], goal: tuple[int, int]) -> list[tuple[int, int]]:
        path = [start]
        x, y = start
        gx, gy = goal

        while (x, y) != (gx, gy):
            dx = gx - x
            dy = gy - y

            if dx != 0 and dy != 0:
                move_horizontal = random.random() < 0.5
            else:
                move_horizontal = dx != 0

            if move_horizontal:
                x += 1 if dx > 0 else -1
            else:
                y += 1 if dy > 0 else -1

            path.append((x, y))

        return path

    def build_town(self, seed_value: int) -> TownModel:
        random.seed(seed_value)

        grid = [[GRASS_TILE for _ in range(self.width)] for _ in range(self.height)]
        start = (1, 1)
        goal = (self.width - 2, self.height - 2)

        path = self.generate_path(start, goal)
        road_set = set(path)

        for x, y in path:
            grid[y][x] = ROAD_TILE

        for x, y in path:
            side_options = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            random.shuffle(side_options)

            for bx, by in side_options:
                if not (0 <= bx < self.width and 0 <= by < self.height):
                    continue
                if (bx, by) in road_set:
                    continue
                if grid[by][bx] is not GRASS_TILE:
                    continue
                if random.random() < BUILDING_CHANCE:
                    grid[by][bx] = BUILDING_TILE
                    break

        for y in range(self.height):
            for x in range(self.width):
                if grid[y][x] is GRASS_TILE and random.random() < TREE_CHANCE:
                    grid[y][x] = TREE_TILE

        sx, sy = start
        gx, gy = goal
        grid[sy][sx] = START_TILE
        grid[gy][gx] = GOAL_TILE

        walkable = [(x, y) for y in range(self.height) for x in range(self.width) if grid[y][x].walkable]
        random.shuffle(walkable)
        npc_count = min(16, max(6, len(walkable) // 12))

        npcs: list[NpcModel] = []
        for nx, ny in walkable:
            if (nx, ny) in (start, goal):
                continue
            npcs.append(NpcModel(nx, ny))
            if len(npcs) >= npc_count:
                break

        return TownModel(grid=grid, start=start, goal=goal, seed=seed_value, npcs=npcs)
