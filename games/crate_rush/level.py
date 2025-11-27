import random
import pygame as pg
from . import settings as S

class Platform(pg.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.rect = pg.Rect(rect)
        self.image = pg.Surface(self.rect.size)
        self.image.fill(S.PLATFORM_COLOR)
        self.mask = None
        self.pos = self.rect.topleft

class Level:
    def __init__(self):
        self.platforms = pg.sprite.Group()
        self.platform_rects = [
            (0, S.HAZARD_HEIGHT, S.WIDTH, 24),
            (60, 360, 280, 18),
            (620, 360, 280, 18),
            (320, 250, 320, 18),
            (120, 160, 220, 14),
            (620, 160, 220, 14),
        ]
        for r in self.platform_rects:
            self.platforms.add(Platform(r))
        self.spawners = [(40, -20), (S.WIDTH - 40, -20)]
        self.crate_spots = [
            pg.Rect(100, 130, 24, 24),
            pg.Rect(700, 130, 24, 24),
            pg.Rect(200, 330, 24, 24),
            pg.Rect(740, 330, 24, 24),
            pg.Rect(450, 220, 24, 24),
        ]

    def random_crate_spot(self):
        return random.choice(self.crate_spots).center
