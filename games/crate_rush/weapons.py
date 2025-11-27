import math
import random
import pygame as pg
from . import settings as S

class Bullet(pg.sprite.Sprite):
    def __init__(self, pos, vel, radius=4, color=S.BULLET_COLOR, damage=1, lifetime=1.2):
        super().__init__()
        self.pos = pg.Vector2(pos)
        self.vel = pg.Vector2(vel)
        self.radius = radius
        self.color = color
        self.damage = damage
        self.life = lifetime
        d = radius * 2
        self.image = pg.Surface((d, d), pg.SRCALPHA)
        pg.draw.circle(self.image, self.color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt, platforms):
        self.life -= dt
        if self.life <= 0:
            self.kill()
            return
        self.pos += self.vel * dt
        self.rect.center = self.pos
        if not (-50 <= self.pos.x <= S.WIDTH + 50 and -80 <= self.pos.y <= S.HEIGHT + 80):
            self.kill()

class Weapon:
    name = ""
    cooldown = 0.2
    def shoot(self, origin, direction, bullets):
        pass

class Pistol(Weapon):
    name = "Pistol"
    cooldown = 0.3
    def shoot(self, origin, direction, bullets):
        vel = direction * 900
        bullets.add(Bullet(origin, vel, 4, S.BULLET_COLOR, 1))

class SMG(Weapon):
    name = "SMG"
    cooldown = 0.08
    def shoot(self, origin, direction, bullets):
        ang = math.atan2(direction.y, direction.x)
        ang += random.uniform(-0.09, 0.09)
        vel = pg.Vector2(math.cos(ang), math.sin(ang)) * 820
        bullets.add(Bullet(origin, vel, 3, (255, 210, 80), 1, 0.9))

class Shotgun(Weapon):
    name = "Shotgun"
    cooldown = 0.6
    def shoot(self, origin, direction, bullets):
        base = math.atan2(direction.y, direction.x)
        for i in range(7):
            ang = base + random.uniform(-0.25, 0.25)
            vel = pg.Vector2(math.cos(ang), math.sin(ang)) * random.randint(620, 760)
            bullets.add(Bullet(origin, vel, 3, (255, 250, 180), 1, 0.5))

class Rocket(Weapon):
    name = "Rocket"
    cooldown = 0.85
    def shoot(self, origin, direction, bullets):
        vel = direction * 520
        bullets.add(Bullet(origin, vel, 6, (255, 120, 120), 3, 1.6))

class AK47(Weapon):
    name = "AK-47"
    cooldown = 0.12
    has_sprite = True  # Flag to indicate this weapon has visual sprites
    
    def shoot(self, origin, direction, bullets):
        ang = math.atan2(direction.y, direction.x)
        ang += random.uniform(-0.06, 0.06)  # Slight spread for realism
        vel = pg.Vector2(math.cos(ang), math.sin(ang)) * 950
        bullets.add(Bullet(origin, vel, 4, (255, 200, 50), 2, 1.1))

WEAPON_POOL = [Pistol, SMG, Shotgun, Rocket, AK47]
