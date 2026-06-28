import random

from models.npc import NpcModel


class NpcPlacementEngine:
    """Create NPC placements for a generated town from walkable tile candidates.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(self):
        """Initialize reusable NPC style palette.

        Args:
            None.

        Returns:
            None.
        """
        self.npc_hat_palette = [
            (52, 73, 94),
            (120, 66, 18),
            (17, 122, 101),
            (146, 43, 33),
        ]

    def build_npcs(
        self,
        walkable_tiles: list[tuple[int, int]],
        start: tuple[int, int],
        goal: tuple[int, int],
    ) -> list[NpcModel]:
        """Build a bounded list of NPCs from candidate walkable coordinates.

        Args:
            walkable_tiles: Candidate walkable tile coordinates.
            start: Start tile coordinate to avoid.
            goal: Goal tile coordinate to avoid.

        Returns:
            list[NpcModel]: Generated NPC entities with randomized hat style.
        """
        candidates = walkable_tiles.copy()
        random.shuffle(candidates)
        npc_count = min(16, max(6, len(candidates) // 12))

        npcs: list[NpcModel] = []
        for nx, ny in candidates:
            if (nx, ny) in (start, goal):
                continue
            hat_color = (
                random.choice(self.npc_hat_palette) if random.random() < 0.6 else None
            )
            npcs.append(NpcModel(x=nx, y=ny, hat_color=hat_color))
            if len(npcs) >= npc_count:
                break

        return npcs
