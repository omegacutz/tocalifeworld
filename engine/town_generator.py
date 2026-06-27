import random

from models.entities import CollectibleModel, NpcModel
from models.terrain import BUILDING_TILE, GOAL_TILE, GRASS_TILE, ROAD_TILE, START_TILE, TREE_TILE
from models.town import TownModel

from .constants import BUILDING_CHANCE, GRID_H, GRID_W, TREE_CHANCE


class TownGenerator:
    def __init__(self, width: int = GRID_W, height: int = GRID_H):
        self.width = width
        self.height = height

    def _neighbor_steps(self, x: int, y: int) -> list[tuple[int, int, int, int]]:
        steps = [
            (x + 2, y, x + 1, y),
            (x - 2, y, x - 1, y),
            (x, y + 2, x, y + 1),
            (x, y - 2, x, y - 1),
        ]
        random.shuffle(steps)
        return steps

    def generate_maze_roads(self, start: tuple[int, int], goal: tuple[int, int]) -> set[tuple[int, int]]:
        roads: set[tuple[int, int]] = set()
        visited: set[tuple[int, int]] = set()
        stack: list[tuple[int, int]] = [start]

        roads.add(start)
        visited.add(start)

        while stack:
            cx, cy = stack[-1]
            moved = False

            for nx, ny, wx, wy in self._neighbor_steps(cx, cy):
                if not (1 <= nx < self.width - 1 and 1 <= ny < self.height - 1):
                    continue
                if (nx, ny) in visited:
                    continue

                visited.add((nx, ny))
                roads.add((wx, wy))
                roads.add((nx, ny))
                stack.append((nx, ny))
                moved = True
                break

            if not moved:
                stack.pop()

        # Keep compatibility with existing goal coordinate by carving a connector.
        gx, gy = goal
        link_x, link_y = gx - 1, gy - 1
        x, y = link_x, link_y
        roads.add((x, y))
        while x != gx:
            x += 1 if gx > x else -1
            roads.add((x, y))
        while y != gy:
            y += 1 if gy > y else -1
            roads.add((x, y))

        return roads

    def carve_extra_openings(self, roads: set[tuple[int, int]], difficulty: int) -> set[tuple[int, int]]:
        # Lower difficulty means more openings, fewer dead ends, and easier navigation.
        difficulty = max(0, min(100, difficulty))
        openness_ratio = (100 - difficulty) / 100.0
        openings_to_add = int(self.width * self.height * 0.05 * openness_ratio)

        if openings_to_add <= 0:
            return roads

        candidates: list[tuple[int, int]] = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if (x, y) in roads:
                    continue
                road_neighbors = 0
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    if (x + dx, y + dy) in roads:
                        road_neighbors += 1
                if road_neighbors >= 2:
                    candidates.append((x, y))

        random.shuffle(candidates)
        for x, y in candidates[:openings_to_add]:
            roads.add((x, y))

        return roads

    def build_town(self, seed_value: int, difficulty: int = 50) -> TownModel:
        random.seed(seed_value)

        grid = [[GRASS_TILE for _ in range(self.width)] for _ in range(self.height)]
        start = (1, 1)
        goal = (self.width - 2, self.height - 2)

        road_set = self.generate_maze_roads(start, goal)
        road_set = self.carve_extra_openings(road_set, difficulty)

        for x, y in road_set:
            grid[y][x] = ROAD_TILE

        for x, y in road_set:
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

        npc_hat_palette = [
            (52, 73, 94),
            (120, 66, 18),
            (17, 122, 101),
            (146, 43, 33),
        ]
        npcs: list[NpcModel] = []
        for nx, ny in walkable:
            if (nx, ny) in (start, goal):
                continue
            hat_color = random.choice(npc_hat_palette) if random.random() < 0.6 else None
            npcs.append(NpcModel(x=nx, y=ny, hat_color=hat_color))
            if len(npcs) >= npc_count:
                break

        npc_positions = {(npc.x, npc.y) for npc in npcs}
        collectible_candidates = [
            (x, y)
            for x, y in walkable
            if (x, y) not in npc_positions and (x, y) not in (start, goal)
        ]
        random.shuffle(collectible_candidates)

        collectible_count = min(24, max(10, len(walkable) // 10))
        collectibles = [CollectibleModel(x, y) for x, y in collectible_candidates[:collectible_count]]

        return TownModel(
            grid=grid,
            start=start,
            goal=goal,
            seed=seed_value,
            npcs=npcs,
            collectibles=collectibles,
        )
