import math

import pygame

from models.avatar import DEFAULT_AVATAR_STYLE
from models.entities import PlayerModel
from models.npc import NpcModel
from models.tree import DEFAULT_TREE_STYLE
from models.town import TownModel
from .game_panel_renderer import GamePanelRenderer

from ..constants import HUD_HEIGHT, TILE_SIZE


class TownRenderer:
    """Draw the world, HUD, overlays, and animated actors each frame.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(self, font: pygame.font.Font):
        """Receive shared font resources used for HUD and overlay text.

        Args:
            font: Font used for HUD labels and overlays.

        Returns:
            None.
        """
        self.font = font
        self.panel_renderer = GamePanelRenderer(font)

    def draw_tile(
        self, surface: pygame.Surface, x: int, y: int, color: tuple[int, int, int]
    ) -> None:
        """Render a single tile in world coordinates below the HUD band.

        Args:
            surface: Destination surface for drawing.
            x: Tile x coordinate.
            y: Tile y coordinate.
            color: RGB color for tile fill.

        Returns:
            None.
        """
        rect = pygame.Rect(
            x * TILE_SIZE, HUD_HEIGHT + (y * TILE_SIZE), TILE_SIZE, TILE_SIZE
        )
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
        combo_window_seconds: float,
        version_label: str,
        game_started: bool,
        player_render_position: tuple[float, float],
        npc_render_positions: dict[int, tuple[float, float]],
        hud_right_margin_px: int,
        hud_version_row_y: int,
        hud_win_row_y: int,
    ) -> None:
        """Render one complete frame including map, actors, collectibles, and UI.

        Args:
            surface: Destination surface for frame rendering.
            town: Current town model.
            player: Player model.
            won: Whether player currently reached goal.
            wind_speed: Wind slider value for tree sway.
            wind_slider_track_rect: Wind slider track rectangle.
            difficulty: Difficulty slider value.
            difficulty_slider_track_rect: Difficulty slider track rectangle.
            score: Current score value.
            timer_seconds: Elapsed gameplay timer in seconds.
            high_score: Persisted high score.
            combo_streak: Current combo streak count.
            combo_time_left: Remaining combo time in seconds.
            combo_window_seconds: Full combo window duration.
            version_label: Game version label text.
            game_started: Whether gameplay has started.
            player_render_position: Interpolated player render position.
            npc_render_positions: Interpolated NPC render positions by id.
            hud_right_margin_px: Right margin for right-aligned HUD status labels.
            hud_version_row_y: Vertical row for the version label.
            hud_win_row_y: Vertical row for the win/status label.

        Returns:
            None.
        """
        time_s = pygame.time.get_ticks() / 1000.0

        for y in range(town.height):
            for x in range(town.width):
                tile = town.tile_at(x, y)
                if tile.name == "tree":
                    self.draw_swaying_tree(surface, x, y, time_s, wind_speed)
                else:
                    self.draw_tile(surface, x, y, tile.color)

        for npc in town.npcs:
            npc_render_position = npc_render_positions.get(
                id(npc), (float(npc.x), float(npc.y))
            )
            self.draw_avatar(
                surface,
                npc,
                time_s,
                is_player=False,
                render_position=npc_render_position,
            )

        for item in town.collectibles:
            cx = item.x * TILE_SIZE + TILE_SIZE // 2
            cy = HUD_HEIGHT + (item.y * TILE_SIZE + TILE_SIZE // 2)
            diamond = [(cx, cy - 6), (cx + 6, cy), (cx, cy + 6), (cx - 6, cy)]
            pygame.draw.polygon(surface, item.color, diamond)
            pygame.draw.polygon(surface, (180, 140, 25), diamond, 1)

        self.draw_avatar(
            surface,
            player,
            time_s,
            is_player=True,
            render_position=player_render_position,
        )

        self.panel_renderer.draw_fixed_panel(
            surface=surface,
            town_seed=town.seed,
            collectibles_left=len(town.collectibles),
            score=score,
            timer_seconds=timer_seconds,
            high_score=high_score,
            combo_streak=combo_streak,
            combo_time_left=combo_time_left,
            combo_window_seconds=combo_window_seconds,
            version_label=version_label,
            won=won,
            wind_speed=wind_speed,
            wind_slider_track_rect=wind_slider_track_rect,
            difficulty=difficulty,
            difficulty_slider_track_rect=difficulty_slider_track_rect,
            hud_right_margin_px=hud_right_margin_px,
            hud_version_row_y=hud_version_row_y,
            hud_win_row_y=hud_win_row_y,
        )

        if not game_started:
            self.panel_renderer.draw_start_overlay(surface, high_score)

    def draw_swaying_tree(
        self,
        surface: pygame.Surface,
        x: int,
        y: int,
        time_s: float,
        wind_speed: int,
    ) -> None:
        """Draw an animated tree tile whose canopy sway depends on wind strength.

        Args:
            surface: Destination surface for drawing.
            x: Tile x coordinate.
            y: Tile y coordinate.
            time_s: Current animation time in seconds.
            wind_speed: Wind level from 0 to 100.

        Returns:
            None.
        """
        style = DEFAULT_TREE_STYLE

        # Draw grass first so tree animation looks layered over the ground tile.
        self.draw_tile(surface, x, y, style.base_ground_color)

        tile_x = x * TILE_SIZE
        tile_y = HUD_HEIGHT + (y * TILE_SIZE)
        center_x = tile_x + TILE_SIZE // 2

        wind_level = max(0, min(100, wind_speed)) / 100.0
        phase = (x * style.phase_x_factor) + (y * style.phase_y_factor)
        if wind_level <= 0:
            sway_px = 0
        else:
            sway_speed = style.sway_speed_base + (style.sway_speed_scale * wind_level)
            sway_amplitude = style.sway_amplitude_base + (
                style.sway_amplitude_scale * wind_level
            )
            sway_px = int(math.sin(time_s * sway_speed + phase) * sway_amplitude)

        trunk_color = style.trunk_color
        canopy_color = style.canopy_color
        branch_color = style.branch_color

        trunk_rect = pygame.Rect(
            center_x - (style.trunk_width_px // 2),
            tile_y + int(TILE_SIZE * style.trunk_top_ratio),
            style.trunk_width_px,
            TILE_SIZE - int(TILE_SIZE * style.trunk_top_ratio),
        )
        pygame.draw.rect(surface, trunk_color, trunk_rect)

        top_point = (center_x + sway_px, tile_y + style.canopy_top_offset_px)
        left_point = (
            center_x - style.canopy_half_width_px + sway_px,
            tile_y + TILE_SIZE - style.canopy_bottom_offset_px,
        )
        right_point = (
            center_x + style.canopy_half_width_px + sway_px,
            tile_y + TILE_SIZE - style.canopy_bottom_offset_px,
        )
        pygame.draw.polygon(surface, canopy_color, [top_point, left_point, right_point])

        pygame.draw.line(
            surface,
            branch_color,
            (
                center_x + sway_px + style.branch_start_dx_px,
                tile_y + int(TILE_SIZE * style.branch_start_y_ratio),
            ),
            (
                center_x + sway_px + style.branch_end_dx_px,
                tile_y
                + int(TILE_SIZE * style.branch_start_y_ratio)
                + style.branch_end_y_offset_px,
            ),
            1,
        )

    def draw_avatar(
        self,
        surface: pygame.Surface,
        actor: PlayerModel | NpcModel,
        time_s: float,
        is_player: bool,
        render_position: tuple[float, float] | None = None,
    ) -> None:
        """Draw a character sprite with bobbing limbs at interpolated tile-space position.

        Args:
            surface: Destination surface for drawing.
            actor: Player or NPC model to render.
            time_s: Current animation time in seconds.
            is_player: True when actor is player (affects styling details).
            render_position: Optional interpolated tile-space position.

        Returns:
            None.
        """
        if render_position is None:
            render_x, render_y = float(actor.x), float(actor.y)
        else:
            render_x, render_y = render_position

        tile_x = int(round(render_x * TILE_SIZE))
        tile_y = HUD_HEIGHT + int(round(render_y * TILE_SIZE))

        center_x = tile_x + TILE_SIZE // 2
        phase = (actor.x * 0.43) + (actor.y * 0.29)
        bob = int(math.sin(time_s * 5.0 + phase) * 1.2)

        style = DEFAULT_AVATAR_STYLE
        skin_color = style.skin_color
        shirt_color = actor.color
        limb_color = style.limb_color
        shoe_color = style.shoe_color

        body_w = style.body_w
        body_h = style.body_h
        body_x = center_x - body_w // 2
        body_y = tile_y + 11 + bob

        head_radius = style.head_radius
        head_center = (center_x, tile_y + 7 + bob)

        hand_y = body_y + 3
        hand_swing = int(math.sin(time_s * 7.5 + phase) * 2)

        foot_y_top = body_y + body_h
        foot_swing = int(math.sin(time_s * 7.5 + phase + 1.1) * 2)

        pygame.draw.line(
            surface,
            limb_color,
            (body_x - 1, hand_y),
            (body_x - 3, hand_y + hand_swing),
            2,
        )
        pygame.draw.line(
            surface,
            limb_color,
            (body_x + body_w + 1, hand_y),
            (body_x + body_w + 3, hand_y - hand_swing),
            2,
        )

        pygame.draw.rect(
            surface,
            shirt_color,
            pygame.Rect(body_x, body_y, body_w, body_h),
            border_radius=2,
        )

        pygame.draw.line(
            surface,
            limb_color,
            (body_x + 2, foot_y_top),
            (body_x + 1 + foot_swing, foot_y_top + 5),
            2,
        )
        pygame.draw.line(
            surface,
            limb_color,
            (body_x + body_w - 2, foot_y_top),
            (body_x + body_w - 1 - foot_swing, foot_y_top + 5),
            2,
        )

        pygame.draw.circle(surface, skin_color, head_center, head_radius)

        if actor.hat_color is not None:
            hat_w = style.player_hat_width if is_player else style.npc_hat_width
            hat_h = 3
            hat_rect = pygame.Rect(
                center_x - hat_w // 2, head_center[1] - head_radius - 2, hat_w, hat_h
            )
            brim_rect = pygame.Rect(
                center_x - (hat_w // 2 + 1), head_center[1] - head_radius, hat_w + 2, 2
            )
            pygame.draw.rect(surface, actor.hat_color, hat_rect, border_radius=1)
            pygame.draw.rect(surface, actor.hat_color, brim_rect, border_radius=1)

        eye_y = head_center[1] - 1
        pygame.draw.circle(surface, (35, 35, 35), (head_center[0] - 1, eye_y), 1)
        pygame.draw.circle(surface, (35, 35, 35), (head_center[0] + 1, eye_y), 1)

        pygame.draw.line(
            surface,
            shoe_color,
            (body_x + foot_swing, foot_y_top + 5),
            (body_x + 3 + foot_swing, foot_y_top + 5),
            1,
        )
        pygame.draw.line(
            surface,
            shoe_color,
            (body_x + body_w - 3 - foot_swing, foot_y_top + 5),
            (body_x + body_w - foot_swing, foot_y_top + 5),
            1,
        )
