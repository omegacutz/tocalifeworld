import pygame

from models.entities import PlayerModel
from models.town import TownModel

from .constants import TEXT_COLOR, TILE_SIZE


class TownRenderer:
    def __init__(self, font: pygame.font.Font):
        self.font = font

    def draw_tile(self, surface: pygame.Surface, x: int, y: int, color: tuple[int, int, int]) -> None:
        rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(surface, color, rect)

    def draw(self, surface: pygame.Surface, town: TownModel, player: PlayerModel, won: bool) -> None:
        for y in range(town.height):
            for x in range(town.width):
                tile = town.tile_at(x, y)
                self.draw_tile(surface, x, y, tile.color)

        for npc in town.npcs:
            center = (npc.x * TILE_SIZE + TILE_SIZE // 2, npc.y * TILE_SIZE + TILE_SIZE // 2)
            pygame.draw.circle(surface, npc.color, center, TILE_SIZE // 4)

        player_rect = pygame.Rect(
            player.x * TILE_SIZE + 6,
            player.y * TILE_SIZE + 6,
            TILE_SIZE - 12,
            TILE_SIZE - 12,
        )
        pygame.draw.rect(surface, player.color, player_rect)

        title = self.font.render(
            f"Seed: {town.seed}  |  Reach B from A  |  Press R to regenerate",
            True,
            TEXT_COLOR,
        )
        surface.blit(title, (10, 8))

        if won:
            win_text = self.font.render("You made it to B. Great job!", True, TEXT_COLOR)
            surface.blit(win_text, (10, 32))
