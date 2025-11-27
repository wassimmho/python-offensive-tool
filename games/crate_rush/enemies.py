import random
import pygame as pg
from . import settings as S
from .player import PhysicsSprite

class Enemy(PhysicsSprite):
    def __init__(self, x, y, speed=140):
        super().__init__()
        self.pos.update(x, y)
        self.speed = speed
        self.image = pg.Surface(self.size, pg.SRCALPHA)
        self.draw_enemy()
        self.rect.topleft = self.pos
        self.dir = random.choice([-1, 1])
        self.health = 2
    
    def draw_enemy(self):
        """Draw a proper enemy character sprite"""
        self.image.fill((0, 0, 0, 0))  # Clear with transparency
        w, h = int(self.size.x), int(self.size.y)
        
        # Body (torso) - more menacing colors
        body_rect = pg.Rect(w//4, h//3, w//2, h//2)
        pg.draw.rect(self.image, (220, 80, 90), body_rect, border_radius=4)
        pg.draw.rect(self.image, (180, 50, 60), body_rect, width=2, border_radius=4)
        
        # Head - skull-like
        head_size = w // 2.5
        head_center = (w // 2, h // 5)
        pg.draw.circle(self.image, (200, 200, 200), head_center, int(head_size))
        pg.draw.circle(self.image, (150, 150, 150), head_center, int(head_size), width=2)
        
        # Evil eyes (red)
        eye_y = h // 6
        pg.draw.circle(self.image, (255, 50, 50), (w//2 - 4, eye_y), 3)
        pg.draw.circle(self.image, (255, 50, 50), (w//2 + 4, eye_y), 3)
        pg.draw.circle(self.image, (150, 0, 0), (w//2 - 4, eye_y), 3, width=1)
        pg.draw.circle(self.image, (150, 0, 0), (w//2 + 4, eye_y), 3, width=1)
        
        # Legs
        leg_top = h // 3 + h // 2
        leg_width = 5
        pg.draw.rect(self.image, (150, 60, 70), (w//3 - 2, leg_top, leg_width, h - leg_top), border_radius=2)
        pg.draw.rect(self.image, (150, 60, 70), (w - w//3 - 3, leg_top, leg_width, h - leg_top), border_radius=2)
        
        # Arms (claws)
        arm_y = h // 3 + 5
        arm_height = h // 3
        pg.draw.rect(self.image, (180, 180, 180), (2, arm_y, 4, arm_height), border_radius=2)
        pg.draw.rect(self.image, (180, 180, 180), (w - 6, arm_y, 4, arm_height), border_radius=2)
        # Claw tips
        pg.draw.circle(self.image, (255, 50, 50), (4, arm_y + arm_height), 3)
        pg.draw.circle(self.image, (255, 50, 50), (w - 4, arm_y + arm_height), 3)

    def damage(self, amount):
        self.health -= amount
        return self.health <= 0

    def update(self, dt, platforms):
        self.vel.x = self.dir * self.speed
        on_ground = self.physics_step(dt, platforms)
        if on_ground:
            ahead = self.rect.move(self.dir * 10, 1)
            support = False
            for p in platforms:
                if p.rect.colliderect(ahead.move(0, 10)) and p.rect.top <= self.rect.bottom <= p.rect.bottom + 2:
                    support = True
                    break
            if not support:
                self.dir *= -1
        for p in platforms:
            if self.rect.colliderect(p.rect) and (self.rect.left <= p.rect.left or self.rect.right >= p.rect.right):
                self.dir *= -1
        if self.pos.y > S.HAZARD_HEIGHT + 60:
            self.kill()

class Spawner:
    def __init__(self, pos):
        self.pos = pg.Vector2(pos)

    def spawn(self, difficulty):
        speed = 120 + difficulty * 18
        return Enemy(self.pos.x, self.pos.y, speed)
