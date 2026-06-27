import random
import sys
from pathlib import Path

import pygame

from models.entities import PlayerModel
from models.town import TownModel

from .constants import (
    COLLECTIBLE_POINTS,
    COMBO_MULTIPLIER_CAP,
    COMBO_WINDOW_SECONDS,
    FINISH_BONUS_POINTS,
    FINISH_TIME_TARGET_SECONDS,
    FONT_NAME,
    FONT_SIZE,
    FPS,
    GAME_TITLE,
    HIGH_SCORE_FILE,
    NPC_MOVE_CHANCE,
    NPC_MOVE_INTERVAL_MS,
    SCREEN_H,
    SCREEN_W,
)
from .high_score import HighScoreStore
from .renderer import TownRenderer
from .town_generator import TownGenerator


class GameEngine:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

        self.generator = TownGenerator()
        self.renderer = TownRenderer(self.font)

        self.current_seed = random.randint(1000, 9999)
        self.difficulty = 55
        self.town: TownModel = self.generator.build_town(self.current_seed, self.difficulty)
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

        self.wind_speed = 35
        self.wind_slider_track_rect = pygame.Rect(10, 36, 220, 8)
        self.difficulty_slider_track_rect = pygame.Rect(10, 58, 220, 8)
        self.active_slider: str | None = None
        self.next_move_allowed_ticks = 0
        self.last_npc_move_ticks = pygame.time.get_ticks()
        self.last_idle_move_ticks = pygame.time.get_ticks()

    def restart_town(self) -> None:
        self.current_seed = random.randint(1000, 9999)
        self.town = self.generator.build_town(self.current_seed, self.difficulty)
        self.player.move_to(*self.town.start)
        self.won = False
        self.score = 0
        self.finish_bonus_applied = False
        self.round_start_ticks = pygame.time.get_ticks()
        self.combo_streak = 0
        self.last_collect_ticks = None
        self.last_npc_move_ticks = pygame.time.get_ticks()
        self.last_idle_move_ticks = pygame.time.get_ticks()
        self.game_started = False

    def rebuild_town_for_difficulty(self) -> None:
        self.town = self.generator.build_town(self.current_seed, self.difficulty)
        self.player.move_to(*self.town.start)
        self.won = False
        self.score = 0
        self.finish_bonus_applied = False
        self.round_start_ticks = pygame.time.get_ticks()
        self.combo_streak = 0
        self.last_collect_ticks = None
        self.last_npc_move_ticks = pygame.time.get_ticks()
        self.last_idle_move_ticks = pygame.time.get_ticks()
        self.game_started = False

    def start_game(self) -> None:
        self.game_started = True
        self.player.move_to(*self.town.start)
        self.score = 0
        self.combo_streak = 0
        self.last_collect_ticks = None
        self.finish_bonus_applied = False
        self.round_start_ticks = pygame.time.get_ticks()
        self.next_move_allowed_ticks = self.round_start_ticks

    def return_to_welcome(self) -> None:
        self.game_started = False
        self.player.move_to(*self.town.start)
        self.score = 0
        self.combo_streak = 0
        self.last_collect_ticks = None
        self.finish_bonus_applied = False
        self.round_start_ticks = pygame.time.get_ticks()
        self.next_move_allowed_ticks = self.round_start_ticks

    def elapsed_seconds(self) -> float:
        return (pygame.time.get_ticks() - self.round_start_ticks) / 1000.0

    def combo_time_left(self) -> float:
        if self.last_collect_ticks is None or self.combo_streak <= 0:
            return 0.0

        elapsed = (pygame.time.get_ticks() - self.last_collect_ticks) / 1000.0
        return max(0.0, COMBO_WINDOW_SECONDS - elapsed)

    def register_collectible_pickup(self) -> None:
        now_ticks = pygame.time.get_ticks()

        if self.last_collect_ticks is not None:
            elapsed = (now_ticks - self.last_collect_ticks) / 1000.0
            if elapsed <= COMBO_WINDOW_SECONDS:
                self.combo_streak += 1
            else:
                self.combo_streak = 1
        else:
            self.combo_streak = 1

        self.last_collect_ticks = now_ticks
        multiplier = min(self.combo_streak, COMBO_MULTIPLIER_CAP)
        self.score += COLLECTIBLE_POINTS * multiplier

    def update_combo_state(self) -> None:
        if self.combo_streak > 0 and self.combo_time_left() <= 0:
            self.combo_streak = 0
            self.last_collect_ticks = None

    def apply_finish_bonus_if_needed(self) -> None:
        if self.finish_bonus_applied:
            return

        if self.elapsed_seconds() <= FINISH_TIME_TARGET_SECONDS:
            self.score += FINISH_BONUS_POINTS

        self.finish_bonus_applied = True
        self.high_score = self.high_score_store.save_if_higher(self.score)

    def try_move_player(self, dx: int, dy: int) -> None:
        now_ticks = pygame.time.get_ticks()
        if now_ticks < self.next_move_allowed_ticks:
            return

        nx = self.player.x + dx
        ny = self.player.y + dy

        if self.town.is_walkable(nx, ny):
            self.player.move_to(nx, ny)
            if self.town.collect_at(nx, ny):
                self.register_collectible_pickup()

        self.won = self.player.position == self.town.goal
        if self.won:
            self.apply_finish_bonus_if_needed()

        # Soft interaction: if on the same tile as an NPC, movement stays allowed but becomes slightly slower.
        if any((npc.x, npc.y) == self.player.position for npc in self.town.npcs):
            self.next_move_allowed_ticks = now_ticks + 120
        else:
            self.next_move_allowed_ticks = now_ticks

    def handle_keydown(self, key: int) -> None:
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
            self.try_move_player(-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.try_move_player(1, 0)
        elif key in (pygame.K_UP, pygame.K_w):
            self.try_move_player(0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.try_move_player(0, 1)

    def update_wind_from_mouse(self, mouse_x: int) -> None:
        left = self.wind_slider_track_rect.left
        width = self.wind_slider_track_rect.width
        clamped_x = max(left, min(left + width, mouse_x))
        ratio = (clamped_x - left) / width
        self.wind_speed = int(round(ratio * 100))

    def update_difficulty_from_mouse(self, mouse_x: int) -> None:
        left = self.difficulty_slider_track_rect.left
        width = self.difficulty_slider_track_rect.width
        clamped_x = max(left, min(left + width, mouse_x))
        ratio = (clamped_x - left) / width
        self.difficulty = int(round(ratio * 100))

    def move_npcs(self) -> None:
        now_ticks = pygame.time.get_ticks()
        if now_ticks - self.last_npc_move_ticks < NPC_MOVE_INTERVAL_MS:
            return

        self.last_npc_move_ticks = now_ticks
        base_positions = [(npc.x, npc.y) for npc in self.town.npcs]

        for index, npc in enumerate(self.town.npcs):
            if random.random() > NPC_MOVE_CHANCE:
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

            other_positions = [pos for i, pos in enumerate(base_positions) if i != index]

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
            best_candidates = [tile for tile in candidates if local_density(tile) == best_density]
            chosen = random.choice(best_candidates)

            npc.move_to(*chosen)
            base_positions[index] = chosen

    def update_idle_player_motion(self) -> None:
        if self.game_started:
            return

        now_ticks = pygame.time.get_ticks()
        if now_ticks - self.last_idle_move_ticks < 280:
            return

        self.last_idle_move_ticks = now_ticks
        choices = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
        dx, dy = random.choice(choices)
        nx = self.player.x + dx
        ny = self.player.y + dy

        if self.town.is_walkable(nx, ny) and (nx, ny) != self.town.goal:
            self.player.move_to(nx, ny)

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

                if event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    wind_hit_box = self.wind_slider_track_rect.inflate(0, 18)
                    difficulty_hit_box = self.difficulty_slider_track_rect.inflate(0, 18)

                    if wind_hit_box.collidepoint(event.pos):
                        self.active_slider = "wind"
                        self.update_wind_from_mouse(event.pos[0])

                    if difficulty_hit_box.collidepoint(event.pos):
                        self.active_slider = "difficulty"
                        self.update_difficulty_from_mouse(event.pos[0])

                if event.type == pygame.MOUSEMOTION and self.active_slider == "wind":
                    self.update_wind_from_mouse(event.pos[0])

                if event.type == pygame.MOUSEMOTION and self.active_slider == "difficulty":
                    self.update_difficulty_from_mouse(event.pos[0])

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.active_slider == "difficulty":
                        self.rebuild_town_for_difficulty()
                    self.active_slider = None

            if self.game_started:
                self.update_combo_state()
            else:
                self.update_idle_player_motion()

            self.move_npcs()

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
                self.game_started,
            )
            pygame.display.flip()
            self.clock.tick(FPS)
