import random
import sys
from pathlib import Path

import pygame

from models.entities import PlayerModel
from models.town import TownModel
from config import GameConfig
from versioning.version import GameVersion

from .constants import (
    FONT_NAME,
    FONT_SIZE,
    FPS,
    GAME_TITLE,
    HIGH_SCORE_FILE,
    SCREEN_H,
    SCREEN_W,
)
from .high_score import HighScoreStore
from .movements import AvatarMovementEngine, NpcMovementEngine
from .renderers import TownRenderer
from .town_generator import TownGenerator


class GameEngine:
    """Coordinate gameplay systems, input handling, and frame updates.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(self):
        """Create game services and initialize the first playable world state.

        Args:
            None.

        Returns:
            None.
        """
        pygame.init()
        GameConfig.initialize()

        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

        self.generator = TownGenerator()
        self.renderer = TownRenderer(self.font)

        self.current_seed = random.randint(1000, 9999)
        self.difficulty = GameConfig.initial_difficulty
        self.town: TownModel = self.generator.build_town(
            self.current_seed, self.difficulty
        )
        self.player = PlayerModel(*self.town.start)
        self.won = False
        self.score = 0
        self.finish_bonus_applied = False
        self.round_start_ticks = pygame.time.get_ticks()
        self.combo_streak = 0
        self.last_collect_ticks: int | None = None

        high_score_path = Path(__file__).resolve().parent.parent / HIGH_SCORE_FILE
        self.high_score_store = HighScoreStore(str(high_score_path))
        self.high_score = self.high_score_store.load()
        self.game_started = False
        self.version_label = GameVersion.current()

        self.wind_speed = GameConfig.initial_wind_speed
        self.wind_slider_track_rect = pygame.Rect(10, 36, 220, 8)
        self.difficulty_slider_track_rect = pygame.Rect(10, 58, 220, 8)
        self.active_slider: str | None = None
        now_ticks = pygame.time.get_ticks()
        self.avatar_movement = AvatarMovementEngine(
            sub_tile_steps=GameConfig.sub_tile_steps,
            idle_interval_ms=GameConfig.avatar_idle_interval_ms,
            contact_slowdown_ms=GameConfig.avatar_contact_slowdown_ms,
        )
        self.npc_movement = NpcMovementEngine(
            move_interval_ms=GameConfig.npc_move_interval_ms,
            move_chance=GameConfig.npc_move_chance,
            sub_tile_steps=GameConfig.sub_tile_steps,
        )
        self.apply_runtime_config(rebuild_town=False)
        self.avatar_movement.initialize(
            player=self.player, town=self.town, now_ticks=now_ticks
        )
        self.npc_movement.initialize(town=self.town, now_ticks=now_ticks)

    def apply_runtime_config(self, rebuild_town: bool) -> None:
        """Apply current config values to running systems and optional town difficulty.

        Args:
            rebuild_town: Whether difficulty change should rebuild current town.

        Returns:
            None.
        """
        self.collectible_points = GameConfig.collectible_points
        self.combo_window_seconds = GameConfig.combo_window_seconds
        self.combo_multiplier_cap = GameConfig.combo_multiplier_cap
        self.finish_time_target_seconds = GameConfig.finish_time_target_seconds
        self.finish_bonus_points = GameConfig.finish_bonus_points

        self.avatar_movement.sub_tile_steps = max(1, GameConfig.sub_tile_steps)
        self.avatar_movement.idle_interval_ms = GameConfig.avatar_idle_interval_ms
        self.avatar_movement.contact_slowdown_ms = GameConfig.avatar_contact_slowdown_ms

        self.npc_movement.sub_tile_steps = max(1, GameConfig.sub_tile_steps)
        self.npc_movement.move_interval_ms = GameConfig.npc_move_interval_ms
        self.npc_movement.move_chance = GameConfig.npc_move_chance

        self.hud_right_margin_px = GameConfig.hud_right_margin_px
        self.hud_version_row_y = GameConfig.hud_version_row_y
        self.hud_win_row_y = GameConfig.hud_win_row_y

        if self.active_slider is None:
            self.wind_speed = GameConfig.initial_wind_speed

        if (
            rebuild_town
            and self.active_slider is None
            and self.difficulty != GameConfig.initial_difficulty
        ):
            self.difficulty = GameConfig.initial_difficulty
            self.rebuild_town_for_difficulty()

    def initialize_world_engines(self) -> None:
        """Reset movement engines when the town layout or actors are recreated.

        Args:
            None.

        Returns:
            None.
        """
        now_ticks = pygame.time.get_ticks()
        self.avatar_movement.initialize(
            player=self.player, town=self.town, now_ticks=now_ticks
        )
        self.npc_movement.initialize(town=self.town, now_ticks=now_ticks)

    def initialize_avatar_engine(self) -> None:
        """Reset only avatar movement state while keeping the current town intact.

        Args:
            None.

        Returns:
            None.
        """
        now_ticks = pygame.time.get_ticks()
        self.avatar_movement.initialize(
            player=self.player, town=self.town, now_ticks=now_ticks
        )

    def restart_town(self) -> None:
        """Generate a brand-new seeded town and reset round progression.

        Args:
            None.

        Returns:
            None.
        """
        self.current_seed = random.randint(1000, 9999)
        self.town = self.generator.build_town(self.current_seed, self.difficulty)
        self.player.move_to(*self.town.start)
        self.won = False
        self.score = 0
        self.finish_bonus_applied = False
        self.round_start_ticks = pygame.time.get_ticks()
        self.combo_streak = 0
        self.last_collect_ticks = None
        self.game_started = False
        self.initialize_world_engines()

    def rebuild_town_for_difficulty(self) -> None:
        """Rebuild the current seed with updated difficulty to preserve slider intent.

        Args:
            None.

        Returns:
            None.
        """
        self.town = self.generator.build_town(self.current_seed, self.difficulty)
        self.player.move_to(*self.town.start)
        self.won = False
        self.score = 0
        self.finish_bonus_applied = False
        self.round_start_ticks = pygame.time.get_ticks()
        self.combo_streak = 0
        self.last_collect_ticks = None
        self.game_started = False
        self.initialize_world_engines()

    def start_game(self) -> None:
        """Enter active play mode and reset score/timer state for a new run.

        Args:
            None.

        Returns:
            None.
        """
        self.game_started = True
        self.player.move_to(*self.town.start)
        self.score = 0
        self.combo_streak = 0
        self.last_collect_ticks = None
        self.finish_bonus_applied = False
        self.round_start_ticks = pygame.time.get_ticks()
        self.initialize_avatar_engine()

    def return_to_welcome(self) -> None:
        """Leave active play mode and return the avatar to idle welcome behavior.

        Args:
            None.

        Returns:
            None.
        """
        self.game_started = False
        self.player.move_to(*self.town.start)
        self.score = 0
        self.combo_streak = 0
        self.last_collect_ticks = None
        self.finish_bonus_applied = False
        self.round_start_ticks = pygame.time.get_ticks()
        self.initialize_avatar_engine()

    def elapsed_seconds(self) -> float:
        """Return elapsed round time in seconds for HUD and scoring logic.

        Args:
            None.

        Returns:
            float: Elapsed gameplay time in seconds.
        """
        return (pygame.time.get_ticks() - self.round_start_ticks) / 1000.0

    def combo_time_left(self) -> float:
        """Compute remaining time before the collectible combo streak expires.

        Args:
            None.

        Returns:
            float: Remaining combo time in seconds.
        """
        if self.last_collect_ticks is None or self.combo_streak <= 0:
            return 0.0

        elapsed = (pygame.time.get_ticks() - self.last_collect_ticks) / 1000.0
        return max(0.0, self.combo_window_seconds - elapsed)

    def register_collectible_pickup(self) -> None:
        """Apply combo math and add points whenever a collectible is picked up.

        Args:
            None.

        Returns:
            None.
        """
        now_ticks = pygame.time.get_ticks()

        if self.last_collect_ticks is not None:
            elapsed = (now_ticks - self.last_collect_ticks) / 1000.0
            if elapsed <= self.combo_window_seconds:
                self.combo_streak += 1
            else:
                self.combo_streak = 1
        else:
            self.combo_streak = 1

        self.last_collect_ticks = now_ticks
        multiplier = min(self.combo_streak, self.combo_multiplier_cap)
        self.score += self.collectible_points * multiplier

    def update_combo_state(self) -> None:
        """Clear combo streak state once the combo window has elapsed.

        Args:
            None.

        Returns:
            None.
        """
        if self.combo_streak > 0 and self.combo_time_left() <= 0:
            self.combo_streak = 0
            self.last_collect_ticks = None

    def apply_finish_bonus_if_needed(self) -> None:
        """Award time bonus once and persist a new high score if achieved.

        Args:
            None.

        Returns:
            None.
        """
        if self.finish_bonus_applied:
            return

        if self.elapsed_seconds() <= self.finish_time_target_seconds:
            self.score += self.finish_bonus_points

        self.finish_bonus_applied = True
        self.high_score = self.high_score_store.save_if_higher(self.score)

    def move_player(self, dx: int, dy: int) -> None:
        """Delegate avatar movement, then resolve pickups and win conditions.

        Args:
            dx: Horizontal tile delta.
            dy: Vertical tile delta.

        Returns:
            None.
        """
        moved = self.avatar_movement.try_move(
            dx, dy, self.town.npcs, pygame.time.get_ticks()
        )
        if moved and self.town.collect_at(self.player.x, self.player.y):
            self.register_collectible_pickup()

        self.won = self.player.position == self.town.goal
        if self.won:
            self.apply_finish_bonus_if_needed()

    def handle_keydown(self, key: int) -> None:
        """Map keyboard input into game state transitions and movement actions.

        Args:
            key: Pygame key code from keyboard event.

        Returns:
            None.
        """
        if not self.game_started and key == pygame.K_SPACE:
            self.start_game()
            return

        if self.game_started and key == pygame.K_ESCAPE:
            self.return_to_welcome()
            return

        if key == pygame.K_r:
            self.restart_town()
            return

        if not self.game_started:
            return

        if key in (pygame.K_LEFT, pygame.K_a):
            self.move_player(-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.move_player(1, 0)
        elif key in (pygame.K_UP, pygame.K_w):
            self.move_player(0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.move_player(0, 1)

    def update_wind_from_mouse(self, mouse_x: int) -> None:
        """Convert wind slider cursor position into a 0-100 wind strength value.

        Args:
            mouse_x: Current mouse x coordinate.

        Returns:
            None.
        """
        left = self.wind_slider_track_rect.left
        width = self.wind_slider_track_rect.width
        clamped_x = max(left, min(left + width, mouse_x))
        ratio = (clamped_x - left) / width
        self.wind_speed = int(round(ratio * 100))

    def update_difficulty_from_mouse(self, mouse_x: int) -> None:
        """Convert difficulty slider cursor position into a 0-100 difficulty value.

        Args:
            mouse_x: Current mouse x coordinate.

        Returns:
            None.
        """
        left = self.difficulty_slider_track_rect.left
        width = self.difficulty_slider_track_rect.width
        clamped_x = max(left, min(left + width, mouse_x))
        ratio = (clamped_x - left) / width
        self.difficulty = int(round(ratio * 100))

    def run(self) -> None:
        """Run the main loop that processes input, updates systems, and renders frames.

        Args:
            None.

        Returns:
            None.
        """
        while True:
            if GameConfig.reload_if_changed():
                self.apply_runtime_config(rebuild_town=True)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

                if event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    wind_hit_box = self.wind_slider_track_rect.inflate(0, 18)
                    difficulty_hit_box = self.difficulty_slider_track_rect.inflate(
                        0, 18
                    )

                    if wind_hit_box.collidepoint(event.pos):
                        self.active_slider = "wind"
                        self.update_wind_from_mouse(event.pos[0])

                    if difficulty_hit_box.collidepoint(event.pos):
                        self.active_slider = "difficulty"
                        self.update_difficulty_from_mouse(event.pos[0])

                if event.type == pygame.MOUSEMOTION and self.active_slider == "wind":
                    self.update_wind_from_mouse(event.pos[0])

                if (
                    event.type == pygame.MOUSEMOTION
                    and self.active_slider == "difficulty"
                ):
                    self.update_difficulty_from_mouse(event.pos[0])

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.active_slider == "difficulty":
                        self.rebuild_town_for_difficulty()
                    self.active_slider = None

            if self.game_started:
                self.update_combo_state()
            else:
                self.avatar_movement.update_idle_motion(pygame.time.get_ticks())

            now_ticks = pygame.time.get_ticks()
            self.npc_movement.execute(now_ticks)
            self.avatar_movement.execute(now_ticks)

            self.renderer.draw(
                self.screen,
                self.town,
                self.player,
                self.won,
                self.wind_speed,
                self.wind_slider_track_rect,
                self.difficulty,
                self.difficulty_slider_track_rect,
                self.score,
                self.elapsed_seconds() if self.game_started else 0.0,
                self.high_score,
                self.combo_streak,
                self.combo_time_left(),
                self.combo_window_seconds,
                self.version_label,
                self.game_started,
                self.avatar_movement.render_position,
                self.npc_movement.render_positions,
                self.hud_right_margin_px,
                self.hud_version_row_y,
                self.hud_win_row_y,
            )
            pygame.display.flip()
            self.clock.tick(FPS)
