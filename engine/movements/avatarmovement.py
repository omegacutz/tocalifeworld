import random

from models.entities import PlayerModel
from models.npc import NpcModel
from models.town import TownModel

from engine.base_engine import BaseEngine


class AvatarMovementEngine(BaseEngine):
    """Own avatar movement rules and smooth render interpolation state.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(
        self,
        sub_tile_steps: int,
        idle_interval_ms: int = 280,
        contact_slowdown_ms: int = 120,
    ):
        """Configure movement cadence and initialize avatar runtime state holders.

        Args:
            sub_tile_steps: Interpolation steps used to travel one tile.
            idle_interval_ms: Delay between idle moves on welcome screen.
            contact_slowdown_ms: Delay applied after bumping into NPC overlap.

        Returns:
            None.
        """
        self.sub_tile_steps = max(1, sub_tile_steps)
        self.idle_interval_ms = idle_interval_ms
        self.contact_slowdown_ms = contact_slowdown_ms

        self.player: PlayerModel | None = None
        self.town: TownModel | None = None
        self.next_move_allowed_ticks = 0
        self.last_idle_move_ticks = 0

        self.player_render_x = 0.0
        self.player_render_y = 0.0

    def initialize(
        self,
        player: PlayerModel | None = None,
        town: TownModel | None = None,
        now_ticks: int = 0,
    ) -> None:
        """Bind world references and reset timers/render position to actor tile state.

        Args:
            player: Active player model to control.
            town: Current town model for walkability checks.
            now_ticks: Current pygame tick count used for timer reset.

        Returns:
            None.
        """
        if player is not None:
            self.player = player
        if town is not None:
            self.town = town

        if self.player is None:
            return

        self.next_move_allowed_ticks = now_ticks
        self.last_idle_move_ticks = now_ticks
        self.player_render_x = float(self.player.x)
        self.player_render_y = float(self.player.y)

    def _approach(self, current: float, target: float, max_step: float) -> float:
        """Move a value toward its target by a capped step each frame.

        Args:
            current: Current numeric value.
            target: Desired numeric value.
            max_step: Maximum delta allowed for this update.

        Returns:
            float: Updated value moved toward target.
        """
        delta = target - current
        if abs(delta) <= max_step:
            return target
        return current + max_step if delta > 0 else current - max_step

    def execute(self, now_ticks: int = 0) -> None:
        """Advance avatar render coordinates toward logical tile coordinates.

        Args:
            now_ticks: Current pygame tick count (reserved for interface parity).

        Returns:
            None.
        """
        if self.player is None:
            return

        step = 1.0 / self.sub_tile_steps
        self.player_render_x = self._approach(
            self.player_render_x, float(self.player.x), step
        )
        self.player_render_y = self._approach(
            self.player_render_y, float(self.player.y), step
        )

    @property
    def render_position(self) -> tuple[float, float]:
        """Expose the interpolated avatar render position in tile-space units.

        Args:
            None.

        Returns:
            tuple[float, float]: Current smoothed `(x, y)` render position.
        """
        return self.player_render_x, self.player_render_y

    def try_move(self, dx: int, dy: int, npcs: list[NpcModel], now_ticks: int) -> bool:
        """Attempt one tile move while applying collision slowdown near NPC overlap.

        Args:
            dx: Horizontal tile delta.
            dy: Vertical tile delta.
            npcs: Active NPC list used for overlap slowdown checks.
            now_ticks: Current pygame tick count for move gating.

        Returns:
            bool: True when movement occurred; otherwise False.
        """
        if self.player is None or self.town is None:
            return False

        if now_ticks < self.next_move_allowed_ticks:
            return False

        moved = False
        nx = self.player.x + dx
        ny = self.player.y + dy
        if self.town.is_walkable(nx, ny):
            self.player.move_to(nx, ny)
            moved = True

        if any((npc.x, npc.y) == self.player.position for npc in npcs):
            self.next_move_allowed_ticks = now_ticks + self.contact_slowdown_ms
        else:
            self.next_move_allowed_ticks = now_ticks

        return moved

    def update_idle_motion(self, now_ticks: int) -> None:
        """Move avatar gently while idle on welcome screen to keep scene alive.

        Args:
            now_ticks: Current pygame tick count for interval checks.

        Returns:
            None.
        """
        if self.player is None or self.town is None:
            return

        if now_ticks - self.last_idle_move_ticks < self.idle_interval_ms:
            return

        self.last_idle_move_ticks = now_ticks
        choices = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
        dx, dy = random.choice(choices)
        nx = self.player.x + dx
        ny = self.player.y + dy

        if self.town.is_walkable(nx, ny) and (nx, ny) != self.town.goal:
            self.player.move_to(nx, ny)
