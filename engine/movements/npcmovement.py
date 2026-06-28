import random

from models.town import TownModel

from engine.base_engine import BaseEngine


class NpcMovementEngine(BaseEngine):
    """Control NPC decision movement and smooth render-position updates.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(self, move_interval_ms: int, move_chance: float, sub_tile_steps: int):
        """Configure NPC movement pacing, randomness, and interpolation granularity.

        Args:
            move_interval_ms: Milliseconds between NPC decision cycles.
            move_chance: Probability each NPC chooses to move on a decision cycle.
            sub_tile_steps: Render interpolation steps used per tile movement.

        Returns:
            None.
        """
        self.move_interval_ms = move_interval_ms
        self.move_chance = move_chance
        self.sub_tile_steps = max(1, sub_tile_steps)

        self.town: TownModel | None = None
        self.last_move_ticks = 0
        self.npc_render_positions: dict[int, tuple[float, float]] = {}

    def initialize(self, town: TownModel | None = None, now_ticks: int = 0) -> None:
        """Bind town reference and reset NPC movement/render state to tile positions.

        Args:
            town: Current town model containing NPC entities.
            now_ticks: Current pygame tick count for timer initialization.

        Returns:
            None.
        """
        if town is not None:
            self.town = town

        self.last_move_ticks = now_ticks
        if self.town is None:
            self.npc_render_positions = {}
            return

        self.npc_render_positions = {
            id(npc): (float(npc.x), float(npc.y)) for npc in self.town.npcs
        }

    def _approach(self, current: float, target: float, max_step: float) -> float:
        """Move a value toward a target by at most one interpolation step.

        Args:
            current: Current numeric value.
            target: Desired numeric value.
            max_step: Maximum change to apply in one update.

        Returns:
            float: Updated value after clamped movement toward target.
        """
        delta = target - current
        if abs(delta) <= max_step:
            return target
        return current + max_step if delta > 0 else current - max_step

    def _move_npcs_if_due(self, now_ticks: int) -> None:
        """Run NPC tile decisions at fixed intervals with anti-bunching behavior.

        Args:
            now_ticks: Current pygame tick count for interval checks.

        Returns:
            None.
        """
        if self.town is None:
            return

        if now_ticks - self.last_move_ticks < self.move_interval_ms:
            return

        self.last_move_ticks = now_ticks
        base_positions = [(npc.x, npc.y) for npc in self.town.npcs]

        for index, npc in enumerate(self.town.npcs):
            if random.random() > self.move_chance:
                continue

            candidates: list[tuple[int, int]] = []
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)):
                nx = npc.x + dx
                ny = npc.y + dy
                if not self.town.is_walkable(nx, ny):
                    continue
                if (nx, ny) == self.town.goal:
                    continue
                candidates.append((nx, ny))

            if not candidates:
                continue

            other_positions = [
                pos for i, pos in enumerate(base_positions) if i != index
            ]

            def local_density(tile: tuple[int, int]) -> int:
                tx, ty = tile
                count = 0
                for ox, oy in other_positions:
                    if abs(tx - ox) <= 1 and abs(ty - oy) <= 1:
                        count += 1
                return count

            random.shuffle(candidates)
            candidates.sort(key=local_density)

            best_density = local_density(candidates[0])
            best_candidates = [
                tile for tile in candidates if local_density(tile) == best_density
            ]
            chosen = random.choice(best_candidates)

            npc.move_to(*chosen)
            base_positions[index] = chosen

    def _update_render_positions(self) -> None:
        """Smoothly chase NPC tile positions for non-janky on-screen movement.

        Args:
            None.

        Returns:
            None.
        """
        if self.town is None:
            return

        step = 1.0 / self.sub_tile_steps
        active_npc_ids: set[int] = set()

        for npc in self.town.npcs:
            npc_id = id(npc)
            active_npc_ids.add(npc_id)
            current = self.npc_render_positions.get(
                npc_id, (float(npc.x), float(npc.y))
            )
            self.npc_render_positions[npc_id] = (
                self._approach(current[0], float(npc.x), step),
                self._approach(current[1], float(npc.y), step),
            )

        stale_ids = [
            npc_id
            for npc_id in self.npc_render_positions
            if npc_id not in active_npc_ids
        ]
        for npc_id in stale_ids:
            self.npc_render_positions.pop(npc_id, None)

    def execute(self, now_ticks: int = 0) -> None:
        """Run one NPC tick: decide moves when due and update interpolation state.

        Args:
            now_ticks: Current pygame tick count for movement cadence.

        Returns:
            None.
        """
        if self.town is None:
            return

        self._move_npcs_if_due(now_ticks)
        self._update_render_positions()

    @property
    def render_positions(self) -> dict[int, tuple[float, float]]:
        """Expose interpolated NPC render positions keyed by object identity.

        Args:
            None.

        Returns:
            dict[int, tuple[float, float]]: Smoothed render position per NPC object id.
        """
        return self.npc_render_positions
