import random
import pygame as pg
from . import settings as S

class Particle(pg.sprite.Sprite):
    def __init__(self, pos, color=(255, 200, 80), speed=180, radius=3, life=0.6):
        super().__init__()
        self.pos = pg.Vector2(pos)
        ang = random.uniform(0, 6.283)
        mag = random.uniform(speed*0.4, speed)
        self.vel = pg.Vector2(mag, 0).rotate_rad(ang)
        self.life = life
        self.max_life = life
        self.radius = radius
        self.base_color = color
        d = radius*2
        self.image = pg.Surface((d, d), pg.SRCALPHA)
        pg.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.kill()
            return
        self.pos += self.vel * dt
        self.rect.center = self.pos
        a = max(0, min(255, int(255 * (self.life / self.max_life))))
        d = self.radius*2
        self.image = pg.Surface((d, d), pg.SRCALPHA)
        col = (*self.base_color[:3], a)
        pg.draw.circle(self.image, col, (self.radius, self.radius), self.radius)

class Burst:
    def __init__(self, group, pos, color, count=12, speed=220, radius=3, life=0.6):
        for _ in range(count):
            group.add(Particle(pos, color, speed, radius, life))
