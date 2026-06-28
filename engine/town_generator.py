import random

from models.entities import CollectibleModel
from models.terrain import (
    BUILDING_TILE,
    GOAL_TILE,
    GRASS_TILE,
    ROAD_TILE,
    START_TILE,
    TREE_TILE,
)
from models.town import TownModel

from .constants import BUILDING_CHANCE, GRID_H, GRID_W, TREE_CHANCE
from .npc import NpcPlacementEngine


class TownGenerator:
    """Create seeded procedural towns with roads, actors, and collectibles.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(self, width: int = GRID_W, height: int = GRID_H):
        """Set the map dimensions used by subsequent town generations.

        Args:
            width: Map width in tiles.
            height: Map height in tiles.

        Returns:
            None.
        """
        self.width = width
        self.height = height
        self.npc_placement_engine = NpcPlacementEngine()

    def _neighbor_steps(self, x: int, y: int) -> list[tuple[int, int, int, int]]:
        """Return randomized two-step maze neighbors and their linking wall cells.

        Args:
            x: Current cell x coordinate.
            y: Current cell y coordinate.

        Returns:
            list[tuple[int, int, int, int]]: Candidate next cell and wall-link tuples.
        """
        steps = [
            (x + 2, y, x + 1, y),
            (x - 2, y, x - 1, y),
            (x, y + 2, x, y + 1),
            (x, y - 2, x, y - 1),
        ]
        random.shuffle(steps)
        return steps

    def generate_maze_roads(
        self, start: tuple[int, int], goal: tuple[int, int]
    ) -> set[tuple[int, int]]:
        """Carve a DFS maze road network and ensure connectivity to the goal tile.

        Args:
            start: Starting tile coordinate.
            goal: Goal tile coordinate.

        Returns:
            set[tuple[int, int]]: Walkable road tile coordinates.
        """
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

    def carve_extra_openings(
        self, roads: set[tuple[int, int]], difficulty: int
    ) -> set[tuple[int, int]]:
        """Add optional shortcuts to roads so lower difficulties are easier to navigate.

        Args:
            roads: Existing road tile coordinates.
            difficulty: Difficulty level from 0 to 100.

        Returns:
            set[tuple[int, int]]: Updated road tile coordinates.
        """
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
        """Build a full town model deterministically from seed and difficulty inputs.

        Args:
            seed_value: Seed for deterministic generation.
            difficulty: Difficulty level from 0 to 100.

        Returns:
            TownModel: Generated town with tiles, NPCs, and collectibles.
        """
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

        walkable = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if grid[y][x].walkable
        ]
        npcs = self.npc_placement_engine.build_npcs(walkable, start, goal)

        npc_positions = {(npc.x, npc.y) for npc in npcs}
        collectible_candidates = [
            (x, y)
            for x, y in walkable
            if (x, y) not in npc_positions and (x, y) not in (start, goal)
        ]
        random.shuffle(collectible_candidates)

        collectible_count = min(24, max(10, len(walkable) // 10))
        collectibles = [
            CollectibleModel(x, y)
            for x, y in collectible_candidates[:collectible_count]
        ]

        return TownModel(
            grid=grid,
            start=start,
            goal=goal,
            seed=seed_value,
            npcs=npcs,
            collectibles=collectibles,
        )
