import pygame

from ..constants import HUD_HEIGHT, SCREEN_H, SCREEN_W, TEXT_COLOR


class GamePanelRenderer:
    """Render fixed panel UI elements that do not move with world tiles.

    Args:
        None.

    Returns:
        None.
    """

    def __init__(self, font: pygame.font.Font):
        """Store shared font resources used by panel labels and overlay text.

        Args:
            font: Font used for panel labels and status text.

        Returns:
            None.
        """
        self.font = font

    def draw_fixed_panel(
        self,
        surface: pygame.Surface,
        town_seed: int,
        collectibles_left: int,
        score: int,
        timer_seconds: float,
        high_score: int,
        combo_streak: int,
        combo_time_left: float,
        combo_window_seconds: float,
        version_label: str,
        won: bool,
        wind_speed: int,
        wind_slider_track_rect: pygame.Rect,
        difficulty: int,
        difficulty_slider_track_rect: pygame.Rect,
    ) -> None:
        """Draw all fixed HUD panel elements above the world viewport.

        Args:
            surface: Destination surface for drawing.
            town_seed: Current generated town seed.
            collectibles_left: Number of remaining collectibles.
            score: Current score value.
            timer_seconds: Elapsed time in seconds.
            high_score: Persisted high score value.
            combo_streak: Current combo chain count.
            combo_time_left: Remaining combo time in seconds.
            combo_window_seconds: Total combo window duration in seconds.
            version_label: Current version text.
            won: Whether player reached goal.
            wind_speed: Wind slider value from 0 to 100.
            wind_slider_track_rect: Wind slider track rectangle.
            difficulty: Difficulty slider value from 0 to 100.
            difficulty_slider_track_rect: Difficulty slider track rectangle.

        Returns:
            None.
        """
        surface.fill((245, 245, 245), pygame.Rect(0, 0, surface.get_width(), HUD_HEIGHT))

        title = self.font.render(
            f"Seed: {town_seed}  |  Reach B from A  |  Press R to regenerate",
            True,
            TEXT_COLOR,
        )
        surface.blit(title, (10, 8))

        hud_line = self.font.render(
            f"Score: {score}  |  Yellow Picks Left: {collectibles_left}  |  Time: {timer_seconds:0.1f}s  |  High Score: {high_score}",
            True,
            TEXT_COLOR,
        )
        surface.blit(hud_line, (10, 88))

        combo_line = self.font.render(
            f"Combo: x{combo_streak}  |  Combo Timer: {combo_time_left:0.1f}s / {combo_window_seconds:0.1f}s",
            True,
            TEXT_COLOR,
        )
        surface.blit(combo_line, (10, 110))

        self.draw_wind_slider(surface, wind_speed, wind_slider_track_rect)
        self.draw_difficulty_slider(surface, difficulty, difficulty_slider_track_rect)

        version_text = self.font.render(f"Version: {version_label}", True, TEXT_COLOR)
        surface.blit(version_text, (620, 88))

        if won:
            win_text = self.font.render(
                "Reached B! Finish under 120s for +100 bonus.", True, TEXT_COLOR
            )
            surface.blit(win_text, (620, 110))

    def draw_wind_slider(
        self, surface: pygame.Surface, wind_speed: int, slider_track_rect: pygame.Rect
    ) -> None:
        """Draw the wind control slider and its current numeric value.

        Args:
            surface: Destination surface for drawing.
            wind_speed: Wind value from 0 to 100.
            slider_track_rect: Slider track rectangle.

        Returns:
            None.
        """
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

    def draw_difficulty_slider(
        self, surface: pygame.Surface, difficulty: int, slider_track_rect: pygame.Rect
    ) -> None:
        """Draw the difficulty control slider and its current numeric value.

        Args:
            surface: Destination surface for drawing.
            difficulty: Difficulty value from 0 to 100.
            slider_track_rect: Slider track rectangle.

        Returns:
            None.
        """
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
        """Draw the welcome overlay shown before gameplay starts.

        Args:
            surface: Destination surface for drawing.
            high_score: Current stored high score for display.

        Returns:
            None.
        """
        overlay = pygame.Surface((SCREEN_W, SCREEN_H - HUD_HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 20, 20, 110))
        surface.blit(overlay, (0, HUD_HEIGHT))

        title_font = pygame.font.SysFont("consolas", 30)
        subtitle_font = pygame.font.SysFont("consolas", 22)

        title = title_font.render("START WITH SPACEBAR", True, (255, 255, 255))
        subtitle = subtitle_font.render(
            f"Current high score is: {high_score}", True, (255, 255, 255)
        )

        center_x = SCREEN_W // 2
        center_y = HUD_HEIGHT + (SCREEN_H - HUD_HEIGHT) // 2

        surface.blit(title, (center_x - title.get_width() // 2, center_y - 30))
        surface.blit(subtitle, (center_x - subtitle.get_width() // 2, center_y + 10))
