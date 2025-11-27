import random
import pygame as pg
from . import settings as S

class Platform(pg.sprite.Sprite):
    def __init__(self, rect, color=None):
        super().__init__()
        self.rect = pg.Rect(rect)
        self.image = pg.Surface(self.rect.size)
        self.image.fill(color or S.PLATFORM_COLOR)
        self.mask = None
        self.pos = self.rect.topleft


# Map definitions
MAPS = {
    "classic": {
        "name": "Classic Arena",
        "description": "The original battleground",
        "color": (60, 80, 100),
        "platforms": [
            (0, S.HAZARD_HEIGHT, S.WIDTH, 24),
            (60, 360, 280, 18),
            (620, 360, 280, 18),
            (320, 250, 320, 18),
            (120, 160, 220, 14),
            (620, 160, 220, 14),
        ],
        "spawners": [(40, -20), (S.WIDTH - 40, -20)],
        "crate_spots": [
            (100, 130, 24, 24),
            (700, 130, 24, 24),
            (200, 330, 24, 24),
            (740, 330, 24, 24),
            (450, 220, 24, 24),
        ]
    },
    "towers": {
        "name": "Twin Towers",
        "description": "Two tall towers with bridges",
        "color": (80, 60, 100),
        "platforms": [
            (0, S.HAZARD_HEIGHT, S.WIDTH, 24),
            # Left tower
            (50, 350, 150, 18),
            (50, 250, 150, 18),
            (50, 150, 150, 18),
            # Right tower
            (760, 350, 150, 18),
            (760, 250, 150, 18),
            (760, 150, 150, 18),
            # Bridges
            (200, 300, 560, 14),
            (300, 180, 360, 14),
        ],
        "spawners": [(100, -20), (S.WIDTH - 100, -20)],
        "crate_spots": [
            (100, 120, 24, 24),
            (830, 120, 24, 24),
            (480, 150, 24, 24),
            (480, 270, 24, 24),
            (100, 320, 24, 24),
            (830, 320, 24, 24),
        ]
    },
    "chaos": {
        "name": "Chaos Pit",
        "description": "Scattered platforms everywhere",
        "color": (100, 60, 60),
        "platforms": [
            (0, S.HAZARD_HEIGHT, S.WIDTH, 24),
            # Scattered small platforms
            (80, 380, 100, 14),
            (250, 340, 100, 14),
            (420, 380, 120, 14),
            (600, 340, 100, 14),
            (780, 380, 100, 14),
            # Middle layer
            (150, 260, 120, 14),
            (350, 220, 140, 14),
            (550, 260, 120, 14),
            # Top layer
            (50, 140, 100, 14),
            (220, 100, 100, 14),
            (400, 130, 160, 14),
            (630, 100, 100, 14),
            (800, 140, 100, 14),
        ],
        "spawners": [(50, -20), (S.WIDTH - 50, -20)],
        "crate_spots": [
            (100, 110, 24, 24),
            (250, 70, 24, 24),
            (460, 100, 24, 24),
            (670, 70, 24, 24),
            (830, 110, 24, 24),
            (400, 190, 24, 24),
        ]
    },
    "bridge": {
        "name": "The Bridge",
        "description": "Fight on a long central bridge",
        "color": (60, 100, 80),
        "platforms": [
            (0, S.HAZARD_HEIGHT, S.WIDTH, 24),
            # Main long bridge
            (100, 280, 760, 20),
            # Side platforms
            (30, 380, 140, 16),
            (790, 380, 140, 16),
            # Upper platforms
            (200, 160, 180, 14),
            (580, 160, 180, 14),
            # Top center
            (380, 80, 200, 14),
        ],
        "spawners": [(80, -20), (S.WIDTH - 80, -20)],
        "crate_spots": [
            (480, 50, 24, 24),
            (260, 130, 24, 24),
            (660, 130, 24, 24),
            (200, 250, 24, 24),
            (760, 250, 24, 24),
        ]
    },
    "arena": {
        "name": "Battle Arena",
        "description": "Open arena with corner platforms",
        "color": (100, 80, 50),
        "platforms": [
            (0, S.HAZARD_HEIGHT, S.WIDTH, 24),
            # Corner platforms
            (30, 350, 180, 18),
            (750, 350, 180, 18),
            (30, 150, 180, 18),
            (750, 150, 180, 18),
            # Center platform
            (350, 250, 260, 20),
            # Small connectors
            (210, 280, 140, 12),
            (610, 280, 140, 12),
        ],
        "spawners": [(100, -20), (S.WIDTH - 100, -20)],
        "crate_spots": [
            (100, 120, 24, 24),
            (850, 120, 24, 24),
            (100, 320, 24, 24),
            (850, 320, 24, 24),
            (470, 220, 24, 24),
        ]
    }
}

MAP_LIST = list(MAPS.keys())


class Level:
    def __init__(self, map_id: str = "classic"):
        self.platforms = pg.sprite.Group()
        self.map_id = map_id
        self.load_map(map_id)
    
    def load_map(self, map_id: str):
        """Load a specific map"""
        self.platforms.empty()
        
        if map_id not in MAPS:
            map_id = "classic"
        
        self.map_id = map_id
        map_data = MAPS[map_id]
        
        self.name = map_data["name"]
        self.description = map_data["description"]
        self.platform_color = map_data.get("color", S.PLATFORM_COLOR)
        
        self.platform_rects = map_data["platforms"]
        for r in self.platform_rects:
            self.platforms.add(Platform(r, self.platform_color))
        
        self.spawners = map_data["spawners"]
        self.crate_spots = [pg.Rect(r) for r in map_data["crate_spots"]]

    def random_crate_spot(self):
        return random.choice(self.crate_spots).center
    
    @staticmethod
    def get_map_list():
        """Get list of all available maps"""
        return [(map_id, MAPS[map_id]["name"], MAPS[map_id]["description"]) for map_id in MAP_LIST]
    
    @staticmethod
    def get_map_count():
        return len(MAP_LIST)
