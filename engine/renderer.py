import math

import pygame

from models.entities import NpcModel, PlayerModel
from models.town import TownModel

from .constants import HUD_HEIGHT, SCREEN_H, SCREEN_W, TEXT_COLOR, TILE_SIZE


class TownRenderer:
    def __init__(self, font: pygame.font.Font):
        self.font = font

    def draw_tile(self, surface: pygame.Surface, x: int, y: int, color: tuple[int, int, int]) -> None:
        rect = pygame.Rect(x * TILE_SIZE, HUD_HEIGHT + (y * TILE_SIZE), TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, color, rect)

    def draw(
        self,
        surface: pygame.Surface,
        town: TownModel,
        player: PlayerModel,
        won: bool,
        wind_speed: int,
        wind_slider_track_rect: pygame.Rect,
        difficulty: int,
        difficulty_slider_track_rect: pygame.Rect,
        score: int,
        timer_seconds: float,
        high_score: int,
        combo_streak: int,
        combo_time_left: float,
        game_started: bool,
    ) -> None:
        surface.fill((245, 245, 245), pygame.Rect(0, 0, surface.get_width(), HUD_HEIGHT))
        time_s = pygame.time.get_ticks() / 1000.0

        for y in range(town.height):
            for x in range(town.width):
                tile = town.tile_at(x, y)
                if tile.name == "tree":
                    self.draw_swaying_tree(surface, x, y, time_s, wind_speed)
                else:
                    self.draw_tile(surface, x, y, tile.color)

        for npc in town.npcs:
            self.draw_avatar(surface, npc, time_s, is_player=False)

        for item in town.collectibles:
            cx = item.x * TILE_SIZE + TILE_SIZE // 2
            cy = HUD_HEIGHT + (item.y * TILE_SIZE + TILE_SIZE // 2)
            diamond = [(cx, cy - 6), (cx + 6, cy), (cx, cy + 6), (cx - 6, cy)]
            pygame.draw.polygon(surface, item.color, diamond)
            pygame.draw.polygon(surface, (180, 140, 25), diamond, 1)

        self.draw_avatar(surface, player, time_s, is_player=True)

        title = self.font.render(
            f"Seed: {town.seed}  |  Reach B from A  |  Press R to regenerate",
            True,
            TEXT_COLOR,
        )
        surface.blit(title, (10, 8))

        hud_line = self.font.render(
            f"Score: {score}  |  Yellow Picks Left: {len(town.collectibles)}  |  Time: {timer_seconds:0.1f}s  |  High Score: {high_score}",
            True,
            TEXT_COLOR,
        )
        surface.blit(hud_line, (10, 88))

        combo_line = self.font.render(
            f"Combo: x{combo_streak}  |  Combo Timer: {combo_time_left:0.1f}s / 10.0s",
            True,
            TEXT_COLOR,
        )
        surface.blit(combo_line, (10, 110))

        self.draw_wind_slider(surface, wind_speed, wind_slider_track_rect)
        self.draw_difficulty_slider(surface, difficulty, difficulty_slider_track_rect)

        if won:
            win_text = self.font.render("Reached B! Finish under 120s for +100 bonus.", True, TEXT_COLOR)
            surface.blit(win_text, (620, 110))

        if not game_started:
            self.draw_start_overlay(surface, high_score)

    def draw_swaying_tree(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        time_s: float,
        wind_speed: int,
    ) -> None:
        # Draw grass first so tree animation looks layered over the ground tile.
        self.draw_tile(surface, x, y, (126, 200, 80))

        tile_x = x * TILE_SIZE
        tile_y = HUD_HEIGHT + (y * TILE_SIZE)
        center_x = tile_x + TILE_SIZE // 2

        wind_level = max(0, min(100, wind_speed)) / 100.0
        phase = (x * 0.37) + (y * 0.23)
        if wind_level <= 0:
            sway_px = 0
        else:
            sway_speed = 1.2 + (5.8 * wind_level)
            sway_amplitude = 1 + (10 * wind_level)
            sway_px = int(math.sin(time_s * sway_speed + phase) * sway_amplitude)

        trunk_color = (110, 74, 48)
        canopy_color = (38, 132, 65)
        branch_color = (58, 160, 86)

        trunk_rect = pygame.Rect(
            center_x - 2,
            tile_y + TILE_SIZE // 2,
            4,
            TILE_SIZE // 2,
        )
        pygame.draw.rect(surface, trunk_color, trunk_rect)

        top_point = (center_x + sway_px, tile_y + 3)
        left_point = (center_x - 8 + sway_px, tile_y + TILE_SIZE - 4)
        right_point = (center_x + 8 + sway_px, tile_y + TILE_SIZE - 4)
        pygame.draw.polygon(surface, canopy_color, [top_point, left_point, right_point])

        pygame.draw.line(
            surface,
            branch_color,
            (center_x + sway_px - 3, tile_y + TILE_SIZE // 2),
            (center_x + sway_px + 4, tile_y + TILE_SIZE // 2 + 4),
            1,
        )

    def draw_avatar(self, surface: pygame.Surface, actor: PlayerModel | NpcModel, time_s: float, is_player: bool) -> None:
        tile_x = actor.x * TILE_SIZE
        tile_y = HUD_HEIGHT + (actor.y * TILE_SIZE)

        center_x = tile_x + TILE_SIZE // 2
        phase = (actor.x * 0.43) + (actor.y * 0.29)
        bob = int(math.sin(time_s * 5.0 + phase) * 1.2)

        skin_color = (241, 194, 125)
        shirt_color = actor.color
        limb_color = (82, 58, 45)
        shoe_color = (44, 44, 44)

        body_w = 8
        body_h = 9
        body_x = center_x - body_w // 2
        body_y = tile_y + 11 + bob

        head_radius = 4
        head_center = (center_x, tile_y + 7 + bob)

        hand_y = body_y + 3
        hand_swing = int(math.sin(time_s * 7.5 + phase) * 2)

        foot_y_top = body_y + body_h
        foot_swing = int(math.sin(time_s * 7.5 + phase + 1.1) * 2)

        pygame.draw.line(surface, limb_color, (body_x - 1, hand_y), (body_x - 3, hand_y + hand_swing), 2)
        pygame.draw.line(surface, limb_color, (body_x + body_w + 1, hand_y), (body_x + body_w + 3, hand_y - hand_swing), 2)

        pygame.draw.rect(surface, shirt_color, pygame.Rect(body_x, body_y, body_w, body_h), border_radius=2)

        pygame.draw.line(surface, limb_color, (body_x + 2, foot_y_top), (body_x + 1 + foot_swing, foot_y_top + 5), 2)
        pygame.draw.line(surface, limb_color, (body_x + body_w - 2, foot_y_top), (body_x + body_w - 1 - foot_swing, foot_y_top + 5), 2)

        pygame.draw.circle(surface, skin_color, head_center, head_radius)

        if actor.hat_color is not None:
            hat_w = 10 if is_player else 9
            hat_h = 3
            hat_rect = pygame.Rect(center_x - hat_w // 2, head_center[1] - head_radius - 2, hat_w, hat_h)
            brim_rect = pygame.Rect(center_x - (hat_w // 2 + 1), head_center[1] - head_radius, hat_w + 2, 2)
            pygame.draw.rect(surface, actor.hat_color, hat_rect, border_radius=1)
            pygame.draw.rect(surface, actor.hat_color, brim_rect, border_radius=1)

        eye_y = head_center[1] - 1
        pygame.draw.circle(surface, (35, 35, 35), (head_center[0] - 1, eye_y), 1)
        pygame.draw.circle(surface, (35, 35, 35), (head_center[0] + 1, eye_y), 1)

        pygame.draw.line(surface, shoe_color, (body_x + foot_swing, foot_y_top + 5), (body_x + 3 + foot_swing, foot_y_top + 5), 1)
        pygame.draw.line(
            surface,
            shoe_color,
            (body_x + body_w - 3 - foot_swing, foot_y_top + 5),
            (body_x + body_w - foot_swing, foot_y_top + 5),
            1,
        )

    def draw_wind_slider(self, surface: pygame.Surface, wind_speed: int, slider_track_rect: pygame.Rect) -> None:
        pygame.draw.rect(surface, (210, 210, 210), slider_track_rect, border_radius=4)

        wind_level = max(0, min(100, wind_speed)) / 100.0
        fill_rect = slider_track_rect.copy()
        fill_rect.width = max(1, int(slider_track_rect.width * wind_level))
        pygame.draw.rect(surface, (90, 170, 230), fill_rect, border_radius=4)

        knob_x = slider_track_rect.left + int(slider_track_rect.width * wind_level)
        knob_center = (knob_x, slider_track_rect.centery)
        pygame.draw.circle(surface, (35, 35, 35), knob_center, 7)

        label = self.font.render(f"Wind: {int(wind_speed)}", True, TEXT_COLOR)
        surface.blit(label, (slider_track_rect.right + 12, slider_track_rect.top - 8))

    def draw_difficulty_slider(self, surface: pygame.Surface, difficulty: int, slider_track_rect: pygame.Rect) -> None:
        pygame.draw.rect(surface, (210, 210, 210), slider_track_rect, border_radius=4)

        difficulty_level = max(0, min(100, difficulty)) / 100.0
        fill_rect = slider_track_rect.copy()
        fill_rect.width = max(1, int(slider_track_rect.width * difficulty_level))
        pygame.draw.rect(surface, (230, 140, 80), fill_rect, border_radius=4)

        knob_x = slider_track_rect.left + int(slider_track_rect.width * difficulty_level)
        knob_center = (knob_x, slider_track_rect.centery)
        pygame.draw.circle(surface, (35, 35, 35), knob_center, 7)

        label = self.font.render(f"Difficulty: {int(difficulty)}", True, TEXT_COLOR)
        surface.blit(label, (slider_track_rect.right + 12, slider_track_rect.top - 8))

    def draw_start_overlay(self, surface: pygame.Surface, high_score: int) -> None:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H - HUD_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 20, 110))
        surface.blit(overlay, (0, HUD_HEIGHT))

        title_font = pygame.font.SysFont("consolas", 30)
        subtitle_font = pygame.font.SysFont("consolas", 22)

        title = title_font.render("START WITH SPACEBAR", True, (255, 255, 255))
        subtitle = subtitle_font.render(f"Current high score is: {high_score}", True, (255, 255, 255))

        center_x = SCREEN_W // 2
        center_y = HUD_HEIGHT + (SCREEN_H - HUD_HEIGHT) // 2

        surface.blit(title, (center_x - title.get_width() // 2, center_y - 30))
        surface.blit(subtitle, (center_x - subtitle.get_width() // 2, center_y + 10))
