import random
import pygame as pg
from . import settings as S
from .weapons import WEAPON_POOL

class Crate(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        size = 22
        self.image = pg.Surface((size, size), pg.SRCALPHA)
        self.draw_crate(size)
        self.rect = self.image.get_rect(center=pos)
    
    def draw_crate(self, size):
        """Draw a 3D-looking wooden crate"""
        self.image.fill((0, 0, 0, 0))
        
        # Main crate body
        crate_color = (200, 150, 80)
        dark_color = (140, 100, 50)
        light_color = (230, 180, 100)
        
        # Draw main rectangle
        pg.draw.rect(self.image, crate_color, (0, 0, size, size))
        
        # Draw wooden planks (horizontal lines)
        for i in range(0, size, 6):
            pg.draw.line(self.image, dark_color, (0, i), (size, i), 1)
        
        # Draw vertical supports
        pg.draw.line(self.image, dark_color, (size//3, 0), (size//3, size), 2)
        pg.draw.line(self.image, dark_color, (2*size//3, 0), (2*size//3, size), 2)
        
        # Add 3D effect with shadows and highlights
        pg.draw.line(self.image, dark_color, (0, size-1), (size, size-1), 2)  # Bottom shadow
        pg.draw.line(self.image, dark_color, (size-1, 0), (size-1, size), 2)   # Right shadow
        pg.draw.line(self.image, light_color, (0, 0), (size, 0), 1)            # Top highlight
        pg.draw.line(self.image, light_color, (0, 0), (0, size), 1)            # Left highlight
        
        # Draw border
        pg.draw.rect(self.image, dark_color, (0, 0, size, size), width=1)

    def apply(self, player):
        WeaponCls = random.choice(WEAPON_POOL)
        player.give_weapon(WeaponCls())


class HealDrop(pg.sprite.Sprite):
    """A healing item that falls from the sky and must be caught before hitting the ground"""
    def __init__(self, x):
        super().__init__()
        self.size = 18
        self.image = pg.Surface((self.size, self.size), pg.SRCALPHA)
        self.draw_heal()
        self.rect = self.image.get_rect(center=(x, -20))  # Start above screen
        self.vel_y = S.HEAL_DROP_SPEED
        self.heal_amount = S.HEAL_DROP_AMOUNT
        self.pulse_timer = 0.0
    
    def draw_heal(self):
        """Draw a heart/health icon"""
        self.image.fill((0, 0, 0, 0))
        size = self.size
        center = size // 2
        
        # Draw a glowing heart shape
        # Outer glow
        glow_color = (255, 100, 100, 100)
        heart_color = (255, 60, 80)
        highlight_color = (255, 150, 160)
        
        # Simple heart using circles and triangle
        heart_size = size // 2 - 2
        
        # Left bump
        pg.draw.circle(self.image, heart_color, (center - heart_size//2, center - 2), heart_size//2 + 1)
        # Right bump
        pg.draw.circle(self.image, heart_color, (center + heart_size//2, center - 2), heart_size//2 + 1)
        # Bottom triangle
        points = [
            (center - heart_size, center),
            (center + heart_size, center),
            (center, center + heart_size + 2)
        ]
        pg.draw.polygon(self.image, heart_color, points)
        
        # Highlight
        pg.draw.circle(self.image, highlight_color, (center - heart_size//2 - 1, center - 3), 2)
    
    def update(self, dt, platforms):
        """Update position - falls down, check for platform collision"""
        self.vel_y = S.HEAL_DROP_SPEED
        self.rect.y += int(self.vel_y * dt)
        self.pulse_timer += dt
        
        # Check if hit a platform or went off screen - destroy it
        for p in platforms:
            if self.rect.colliderect(p.rect):
                self.kill()
                return
        
        # Destroy if fell below screen
        if self.rect.top > S.HEIGHT:
            self.kill()
    
    def apply(self, player):
        """Heal the player"""
        player.heal(self.heal_amount)
