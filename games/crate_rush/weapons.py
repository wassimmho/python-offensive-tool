import math
import random
from pathlib import Path
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

# Rocket ammo sprite (loaded lazily)
ROCKET_AMMO_IMG = None
ROCKET_AMMO_LOADED = False

def load_rocket_ammo():
    """Load rocket ammo sprite"""
    global ROCKET_AMMO_IMG, ROCKET_AMMO_LOADED
    if ROCKET_AMMO_LOADED:
        return
    try:
        ammo_path = Path(__file__).parent / 'Weapons' / 'Rocket' / 'Ammo' / 'weapon_088.png'
        img = pg.image.load(str(ammo_path)).convert_alpha()
        # Scale to a good size
        scale_factor = 2.0
        ROCKET_AMMO_IMG = pg.transform.smoothscale(img, (int(img.get_width() * scale_factor), int(img.get_height() * scale_factor)))
        print(f"Loaded rocket ammo sprite")
        ROCKET_AMMO_LOADED = True
    except Exception as e:
        print(f"Could not load rocket ammo sprite: {e}")
        ROCKET_AMMO_LOADED = True

class RocketBullet(pg.sprite.Sprite):
    """Special bullet class for rockets with sprite"""
    def __init__(self, pos, vel, damage=3, lifetime=1.6):
        super().__init__()
        load_rocket_ammo()
        self.pos = pg.Vector2(pos)
        self.vel = pg.Vector2(vel)
        self.damage = damage
        self.life = lifetime
        self.radius = 8  # For collision detection
        
        # Calculate rotation angle from velocity
        self.angle = math.degrees(math.atan2(-vel.y, vel.x))
        
        if ROCKET_AMMO_IMG:
            # Rotate the rocket sprite to face movement direction
            self.base_image = ROCKET_AMMO_IMG
            self.image = pg.transform.rotate(self.base_image, self.angle)
        else:
            # Fallback to circle if sprite not loaded
            d = self.radius * 2
            self.image = pg.Surface((d, d), pg.SRCALPHA)
            pg.draw.circle(self.image, (255, 120, 120), (self.radius, self.radius), self.radius)
        
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
    has_sprite = True  # Flag to indicate this weapon has visual sprites
    sprite_type = 'pistol'  # Identifies which sprite set to use
    
    def shoot(self, origin, direction, bullets):
        vel = direction * 900
        bullets.add(Bullet(origin, vel, 4, S.BULLET_COLOR, 1))

class SMG(Weapon):
    name = "SMG"
    cooldown = 0.08
    has_sprite = True  # Flag to indicate this weapon has visual sprites
    sprite_type = 'smg'  # Identifies which sprite set to use
    
    def shoot(self, origin, direction, bullets):
        ang = math.atan2(direction.y, direction.x)
        ang += random.uniform(-0.09, 0.09)
        vel = pg.Vector2(math.cos(ang), math.sin(ang)) * 820
        bullets.add(Bullet(origin, vel, 3, (255, 210, 80), 1, 0.9))

class Shotgun(Weapon):
    name = "Shotgun"
    cooldown = 0.6
    has_sprite = True  # Flag to indicate this weapon has visual sprites
    sprite_type = 'shotgun'  # Identifies which sprite set to use
    
    def shoot(self, origin, direction, bullets):
        base = math.atan2(direction.y, direction.x)
        for i in range(7):
            ang = base + random.uniform(-0.25, 0.25)
            vel = pg.Vector2(math.cos(ang), math.sin(ang)) * random.randint(620, 760)
            bullets.add(Bullet(origin, vel, 3, (255, 250, 180), 1, 0.5))

class Rocket(Weapon):
    name = "Rocket"
    cooldown = 0.85
    has_sprite = True  # Flag to indicate this weapon has visual sprites
    sprite_type = 'rocket'  # Identifies which sprite set to use
    
    def shoot(self, origin, direction, bullets):
        vel = direction * 520
        bullets.add(RocketBullet(origin, vel, damage=3, lifetime=1.6))

class AK47(Weapon):
    name = "AK-47"
    cooldown = 0.12
    has_sprite = True  # Flag to indicate this weapon has visual sprites
    sprite_type = 'ak47'  # Identifies which sprite set to use
    
    def shoot(self, origin, direction, bullets):
        ang = math.atan2(direction.y, direction.x)
        ang += random.uniform(-0.06, 0.06)  # Slight spread for realism
        vel = pg.Vector2(math.cos(ang), math.sin(ang)) * 950
        bullets.add(Bullet(origin, vel, 4, (255, 200, 50), 2, 1.1))

WEAPON_POOL = [Pistol, SMG, Shotgun, Rocket, AK47]

# ==================== ENEMY WEAPON VARIANTS ====================
# These shoot red/orange bullets to distinguish from player bullets

ENEMY_BULLET_COLOR = (255, 80, 80)  # Red enemy bullets

class EnemyPistol(Weapon):
    name = "Enemy Pistol"
    cooldown = 0.3
    
    def shoot(self, origin, direction, bullets):
        vel = direction * 750  # Slightly slower than player
        bullets.add(Bullet(origin, vel, 4, ENEMY_BULLET_COLOR, 1))

class EnemySMG(Weapon):
    name = "Enemy SMG"
    cooldown = 0.10  # Slower than player SMG
    
    def shoot(self, origin, direction, bullets):
        ang = math.atan2(direction.y, direction.x)
        ang += random.uniform(-0.12, 0.12)  # More spread than player
        vel = pg.Vector2(math.cos(ang), math.sin(ang)) * 680
        bullets.add(Bullet(origin, vel, 3, (255, 120, 80), 1, 0.9))

class EnemyShotgun(Weapon):
    name = "Enemy Shotgun"
    cooldown = 0.7  # Slower than player
    
    def shoot(self, origin, direction, bullets):
        base = math.atan2(direction.y, direction.x)
        for i in range(5):  # Fewer pellets than player
            ang = base + random.uniform(-0.30, 0.30)
            vel = pg.Vector2(math.cos(ang), math.sin(ang)) * random.randint(500, 650)
            bullets.add(Bullet(origin, vel, 3, (255, 150, 100), 1, 0.5))

class EnemyRocket(Weapon):
    name = "Enemy Rocket"
    cooldown = 1.0  # Slower than player
    
    def shoot(self, origin, direction, bullets):
        vel = direction * 420  # Slower rockets
        bullets.add(RocketBullet(origin, vel, damage=3, lifetime=1.6))

class EnemyAK47(Weapon):
    name = "Enemy AK-47"
    cooldown = 0.15  # Slower than player
    
    def shoot(self, origin, direction, bullets):
        ang = math.atan2(direction.y, direction.x)
        ang += random.uniform(-0.10, 0.10)  # More spread than player
        vel = pg.Vector2(math.cos(ang), math.sin(ang)) * 800
        bullets.add(Bullet(origin, vel, 4, (255, 100, 50), 2, 1.1))
