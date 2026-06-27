import random
import sys

import pygame

from models.entities import PlayerModel
from models.town import TownModel

from .constants import FONT_NAME, FONT_SIZE, FPS, GAME_TITLE, SCREEN_H, SCREEN_W
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
        self.town: TownModel = self.generator.build_town(self.current_seed)
        self.player = PlayerModel(*self.town.start)
        self.won = False

    def restart_town(self) -> None:
        self.current_seed = random.randint(1000, 9999)
        self.town = self.generator.build_town(self.current_seed)
        self.player.move_to(*self.town.start)
        self.won = False

    def try_move_player(self, dx: int, dy: int) -> None:
        nx = self.player.x + dx
        ny = self.player.y + dy

        if self.town.is_walkable(nx, ny):
            self.player.move_to(nx, ny)

        self.won = self.player.position == self.town.goal

    def handle_keydown(self, key: int) -> None:
        if key == pygame.K_r:
            self.restart_town()
            return

        if key in (pygame.K_LEFT, pygame.K_a):
            self.try_move_player(-1, 0)
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.try_move_player(1, 0)
        elif key in (pygame.K_UP, pygame.K_w):
            self.try_move_player(0, -1)
        elif key in (pygame.K_DOWN, pygame.K_s):
            self.try_move_player(0, 1)

    def run(self) -> None:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)

                if event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)

            self.renderer.draw(self.screen, self.town, self.player, self.won)
            pygame.display.flip()
            self.clock.tick(FPS)
