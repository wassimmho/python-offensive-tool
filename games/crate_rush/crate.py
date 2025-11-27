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
