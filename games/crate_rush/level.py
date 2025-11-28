import random
import pygame as pg
from pathlib import Path
from . import settings as S

# Tile size
TILE_SIZE = 32

# Load tile images
TILES = {}
def load_tiles():
    global TILES
    if TILES:
        return TILES
    
    tile_folder = Path(__file__).parent / "Tiles"
    if not tile_folder.exists():
        print("Tiles folder not found!")
        return {}
    
    for tile_file in tile_folder.glob("Tile_*.png"):
        try:
            img = pg.image.load(str(tile_file)).convert_alpha()
            tile_name = tile_file.stem  # e.g., "Tile_01"
            TILES[tile_name] = img
        except Exception as e:
            print(f"Failed to load {tile_file}: {e}")
    
    print(f"Loaded {len(TILES)} tiles")
    return TILES

class Platform(pg.sprite.Sprite):
    def __init__(self, rect, color=None, tile_type="solid"):
        super().__init__()
        self.rect = pg.Rect(rect)
        self.tile_type = tile_type
        
        # Load tiles if not already loaded
        tiles = load_tiles()
        
        if tiles and tile_type != "color":
            # Create tiled surface
            self.image = self._create_tiled_surface(tiles, tile_type)
        else:
            # Fallback to solid color
            self.image = pg.Surface(self.rect.size, pg.SRCALPHA)
            self.image.fill(color or S.PLATFORM_COLOR)
        
        self.mask = None
        self.pos = self.rect.topleft
    
    def _create_tiled_surface(self, tiles, tile_type):
        """Create a surface using tiles based on platform dimensions"""
        width = self.rect.width
        height = self.rect.height
        surface = pg.Surface((width, height), pg.SRCALPHA)
        
        # Calculate how many tiles we need (round up to cover the whole platform)
        tiles_wide = (width + TILE_SIZE - 1) // TILE_SIZE
        tiles_high = max(1, (height + TILE_SIZE - 1) // TILE_SIZE)
        
        # Determine which tile set to use based on tile_type
        # The tiles have decorative edges at the BOTTOM, so we flip them
        # Row format: left edge, middle fill, right edge
        if tile_type == "ground":
            # Ground/floor tiles (row 3: 31-39) - typically grassy top
            top_left = tiles.get("Tile_31")
            top_mid = tiles.get("Tile_32")
            top_right = tiles.get("Tile_33")
            # Below ground (row 4 or use same)
            fill_left = tiles.get("Tile_41", tiles.get("Tile_31"))
            fill_mid = tiles.get("Tile_42", tiles.get("Tile_32"))
            fill_right = tiles.get("Tile_41", tiles.get("Tile_33"))
        elif tile_type == "platform":
            # Platform tiles (row 2: 21-29)
            top_left = tiles.get("Tile_21")
            top_mid = tiles.get("Tile_22")
            top_right = tiles.get("Tile_23")
            fill_left = tiles.get("Tile_21")
            fill_mid = tiles.get("Tile_22")
            fill_right = tiles.get("Tile_23")
        elif tile_type == "stone":
            # Stone/brick tiles (row 1: 11-19)
            top_left = tiles.get("Tile_11")
            top_mid = tiles.get("Tile_12")
            top_right = tiles.get("Tile_13")
            fill_left = tiles.get("Tile_11")
            fill_mid = tiles.get("Tile_12")
            fill_right = tiles.get("Tile_13")
        else:
            # Default solid tiles (row 0: 01-09)
            top_left = tiles.get("Tile_01")
            top_mid = tiles.get("Tile_02")
            top_right = tiles.get("Tile_03")
            fill_left = tiles.get("Tile_01")
            fill_mid = tiles.get("Tile_02")
            fill_right = tiles.get("Tile_03")
        
        # Flip all tiles vertically since the decorative part is at the bottom of the tile image
        # but needs to be at the top of the platform
        def flip_tile(tile):
            if tile:
                return pg.transform.flip(tile, False, True)
            return None
        
        top_left = flip_tile(top_left)
        top_mid = flip_tile(top_mid)
        top_right = flip_tile(top_right)
        fill_left = flip_tile(fill_left)
        fill_mid = flip_tile(fill_mid)
        fill_right = flip_tile(fill_right)
        
        # Fallback if tiles not found
        if not top_mid:
            available = list(tiles.values())
            if available:
                top_mid = flip_tile(available[0])
                top_left = top_mid
                top_right = top_mid
                fill_mid = top_mid
                fill_left = top_mid
                fill_right = top_mid
            else:
                surface.fill(S.PLATFORM_COLOR)
                return surface
        
        # Draw the platform with proper tiling
        for row in range(tiles_high):
            for col in range(tiles_wide):
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                
                # Don't draw beyond the surface bounds
                if x >= width or y >= height:
                    continue
                
                # Determine if this is top row or fill row
                is_top_row = (row == 0)
                
                # Select tile based on position
                if tiles_wide == 1:
                    # Single tile wide - use middle tile
                    tile = top_mid if is_top_row else fill_mid
                elif col == 0:
                    tile = top_left if is_top_row else fill_left
                elif col == tiles_wide - 1:
                    tile = top_right if is_top_row else fill_right
                else:
                    tile = top_mid if is_top_row else fill_mid
                
                if tile:
                    # Blit the tile (clip to surface bounds)
                    surface.blit(tile, (x, y))
        
        return surface


# Map definitions with tile types
# Platform heights should be multiples of TILE_SIZE (32) for proper tiling
MAPS = {
    "classic": {
        "name": "Classic Arena",
        "description": "The original battleground",
        "tile_type": "ground",
        "platforms": [
            # (x, y, width, height, tile_type) - tile_type optional, defaults to map's tile_type
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground floor
            {"rect": (64, 352, 288, 32), "type": "platform"},   # Left platform
            {"rect": (608, 352, 288, 32), "type": "platform"},  # Right platform
            {"rect": (320, 256, 320, 32), "type": "stone"},     # Center platform
            {"rect": (128, 160, 224, 32), "type": "platform"},  # Top left
            {"rect": (608, 160, 224, 32), "type": "platform"},  # Top right
        ],
        "spawners": [(40, -20), (S.WIDTH - 40, -20)],
        "crate_spots": [
            (160, 128, 24, 24),
            (720, 128, 24, 24),
            (200, 320, 24, 24),
            (760, 320, 24, 24),
            (460, 224, 24, 24),
        ]
    },
    "towers": {
        "name": "Twin Towers",
        "description": "Two tall towers with bridges",
        "tile_type": "stone",
        "platforms": [
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground
            # Left tower
            {"rect": (32, 352, 160, 32), "type": "stone"},
            {"rect": (32, 256, 160, 32), "type": "stone"},
            {"rect": (32, 160, 160, 32), "type": "stone"},
            # Right tower
            {"rect": (768, 352, 160, 32), "type": "stone"},
            {"rect": (768, 256, 160, 32), "type": "stone"},
            {"rect": (768, 160, 160, 32), "type": "stone"},
            # Bridges
            {"rect": (192, 288, 576, 32), "type": "platform"},
            {"rect": (288, 192, 384, 32), "type": "platform"},
        ],
        "spawners": [(100, -20), (S.WIDTH - 100, -20)],
        "crate_spots": [
            (96, 128, 24, 24),
            (832, 128, 24, 24),
            (480, 160, 24, 24),
            (480, 256, 24, 24),
            (96, 320, 24, 24),
            (832, 320, 24, 24),
        ]
    },
    "chaos": {
        "name": "Chaos Pit",
        "description": "Scattered platforms everywhere",
        "tile_type": "platform",
        "platforms": [
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground
            # Scattered small platforms - bottom layer
            {"rect": (64, 384, 128, 32), "type": "platform"},
            {"rect": (256, 352, 128, 32), "type": "stone"},
            {"rect": (416, 384, 128, 32), "type": "platform"},
            {"rect": (608, 352, 128, 32), "type": "stone"},
            {"rect": (768, 384, 128, 32), "type": "platform"},
            # Middle layer
            {"rect": (160, 256, 128, 32), "type": "stone"},
            {"rect": (352, 224, 160, 32), "type": "platform"},
            {"rect": (576, 256, 128, 32), "type": "stone"},
            # Top layer
            {"rect": (32, 128, 128, 32), "type": "platform"},
            {"rect": (224, 96, 128, 32), "type": "stone"},
            {"rect": (384, 128, 192, 32), "type": "platform"},
            {"rect": (608, 96, 128, 32), "type": "stone"},
            {"rect": (800, 128, 128, 32), "type": "platform"},
        ],
        "spawners": [(50, -20), (S.WIDTH - 50, -20)],
        "crate_spots": [
            (96, 96, 24, 24),
            (272, 64, 24, 24),
            (464, 96, 24, 24),
            (656, 64, 24, 24),
            (848, 96, 24, 24),
            (416, 192, 24, 24),
        ]
    },
    "bridge": {
        "name": "The Bridge",
        "description": "Fight on a long central bridge",
        "tile_type": "stone",
        "platforms": [
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground
            # Main long bridge
            {"rect": (96, 288, 768, 32), "type": "stone"},
            # Side platforms
            {"rect": (32, 384, 160, 32), "type": "platform"},
            {"rect": (768, 384, 160, 32), "type": "platform"},
            # Upper platforms
            {"rect": (192, 160, 192, 32), "type": "platform"},
            {"rect": (576, 160, 192, 32), "type": "platform"},
            # Top center
            {"rect": (384, 64, 192, 32), "type": "stone"},
        ],
        "spawners": [(80, -20), (S.WIDTH - 80, -20)],
        "crate_spots": [
            (470, 32, 24, 24),
            (272, 128, 24, 24),
            (656, 128, 24, 24),
            (192, 256, 24, 24),
            (768, 256, 24, 24),
        ]
    },
    "arena": {
        "name": "Battle Arena",
        "description": "Open arena with corner platforms",
        "tile_type": "platform",
        "platforms": [
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground
            # Corner platforms
            {"rect": (32, 352, 192, 32), "type": "stone"},
            {"rect": (736, 352, 192, 32), "type": "stone"},
            {"rect": (32, 160, 192, 32), "type": "stone"},
            {"rect": (736, 160, 192, 32), "type": "stone"},
            # Center platform
            {"rect": (352, 256, 256, 32), "type": "platform"},
            # Connectors
            {"rect": (224, 288, 128, 32), "type": "platform"},
            {"rect": (608, 288, 128, 32), "type": "platform"},
        ],
        "spawners": [(100, -20), (S.WIDTH - 100, -20)],
        "crate_spots": [
            (112, 128, 24, 24),
            (816, 128, 24, 24),
            (112, 320, 24, 24),
            (816, 320, 24, 24),
            (464, 224, 24, 24),
        ]
    },
    "pyramid": {
        "name": "The Pyramid",
        "description": "Climb the ancient steps",
        "tile_type": "stone",
        "platforms": [
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground
            # Pyramid steps - bottom to top
            {"rect": (128, 416, 704, 32), "type": "stone"},
            {"rect": (224, 352, 512, 32), "type": "stone"},
            {"rect": (320, 288, 320, 32), "type": "stone"},
            {"rect": (416, 224, 128, 32), "type": "platform"},
            # Side platforms
            {"rect": (32, 320, 96, 32), "type": "platform"},
            {"rect": (832, 320, 96, 32), "type": "platform"},
            # Top platform
            {"rect": (384, 128, 192, 32), "type": "stone"},
        ],
        "spawners": [(60, -20), (S.WIDTH - 60, -20)],
        "crate_spots": [
            (470, 96, 24, 24),
            (470, 192, 24, 24),
            (320, 256, 24, 24),
            (640, 256, 24, 24),
            (64, 288, 24, 24),
            (864, 288, 24, 24),
        ]
    },
    "platforms": {
        "name": "Sky Platforms",
        "description": "Jump between floating islands",
        "tile_type": "platform",
        "platforms": [
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground
            # Floating platforms at various heights
            {"rect": (64, 416, 128, 32), "type": "platform"},
            {"rect": (256, 352, 128, 32), "type": "stone"},
            {"rect": (448, 288, 128, 32), "type": "platform"},
            {"rect": (640, 352, 128, 32), "type": "stone"},
            {"rect": (768, 416, 128, 32), "type": "platform"},
            # Upper layer
            {"rect": (160, 224, 128, 32), "type": "stone"},
            {"rect": (384, 160, 192, 32), "type": "platform"},
            {"rect": (672, 224, 128, 32), "type": "stone"},
            # Very top
            {"rect": (288, 64, 96, 32), "type": "platform"},
            {"rect": (576, 64, 96, 32), "type": "platform"},
        ],
        "spawners": [(100, -20), (S.WIDTH - 100, -20)],
        "crate_spots": [
            (112, 384, 24, 24),
            (304, 320, 24, 24),
            (496, 256, 24, 24),
            (688, 320, 24, 24),
            (816, 384, 24, 24),
            (470, 128, 24, 24),
        ]
    },
    "fortress": {
        "name": "The Fortress",
        "description": "Battle in castle walls",
        "tile_type": "stone",
        "platforms": [
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground
            # Left wall
            {"rect": (64, 384, 96, 32), "type": "stone"},
            {"rect": (64, 288, 96, 32), "type": "stone"},
            {"rect": (64, 192, 96, 32), "type": "stone"},
            {"rect": (64, 96, 96, 32), "type": "stone"},
            # Right wall
            {"rect": (800, 384, 96, 32), "type": "stone"},
            {"rect": (800, 288, 96, 32), "type": "stone"},
            {"rect": (800, 192, 96, 32), "type": "stone"},
            {"rect": (800, 96, 96, 32), "type": "stone"},
            # Inner platforms
            {"rect": (224, 352, 192, 32), "type": "platform"},
            {"rect": (544, 352, 192, 32), "type": "platform"},
            {"rect": (352, 256, 256, 32), "type": "stone"},
            {"rect": (256, 160, 160, 32), "type": "platform"},
            {"rect": (544, 160, 160, 32), "type": "platform"},
            # Top bridge
            {"rect": (160, 64, 640, 32), "type": "stone"},
        ],
        "spawners": [(120, -20), (S.WIDTH - 120, -20)],
        "crate_spots": [
            (100, 64, 24, 24),
            (836, 64, 24, 24),
            (470, 224, 24, 24),
            (304, 320, 24, 24),
            (624, 320, 24, 24),
            (470, 32, 24, 24),
        ]
    },
    "duel": {
        "name": "Duel Arena",
        "description": "Face-to-face combat zone",
        "tile_type": "platform",
        "platforms": [
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground
            # Two main platforms for dueling
            {"rect": (64, 320, 256, 32), "type": "stone"},
            {"rect": (640, 320, 256, 32), "type": "stone"},
            # Center connecting platform
            {"rect": (384, 384, 192, 32), "type": "platform"},
            # Upper platforms
            {"rect": (128, 192, 192, 32), "type": "platform"},
            {"rect": (640, 192, 192, 32), "type": "platform"},
            # Top center
            {"rect": (352, 96, 256, 32), "type": "stone"},
            # Small jump platforms
            {"rect": (320, 256, 64, 32), "type": "platform"},
            {"rect": (576, 256, 64, 32), "type": "platform"},
        ],
        "spawners": [(150, -20), (S.WIDTH - 150, -20)],
        "crate_spots": [
            (176, 288, 24, 24),
            (752, 288, 24, 24),
            (470, 64, 24, 24),
            (208, 160, 24, 24),
            (720, 160, 24, 24),
            (470, 352, 24, 24),
        ]
    },
    "maze": {
        "name": "Platform Maze",
        "description": "Navigate the labyrinth",
        "tile_type": "stone",
        "platforms": [
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground
            # Complex maze-like structure
            # Bottom row
            {"rect": (128, 416, 192, 32), "type": "stone"},
            {"rect": (448, 416, 64, 32), "type": "platform"},
            {"rect": (640, 416, 192, 32), "type": "stone"},
            # Second row
            {"rect": (32, 352, 128, 32), "type": "platform"},
            {"rect": (288, 352, 128, 32), "type": "stone"},
            {"rect": (544, 352, 128, 32), "type": "stone"},
            {"rect": (800, 352, 128, 32), "type": "platform"},
            # Third row
            {"rect": (160, 288, 160, 32), "type": "stone"},
            {"rect": (416, 288, 128, 32), "type": "platform"},
            {"rect": (640, 288, 160, 32), "type": "stone"},
            # Fourth row
            {"rect": (64, 224, 128, 32), "type": "platform"},
            {"rect": (288, 224, 128, 32), "type": "stone"},
            {"rect": (544, 224, 128, 32), "type": "stone"},
            {"rect": (768, 224, 128, 32), "type": "platform"},
            # Top row
            {"rect": (192, 160, 192, 32), "type": "stone"},
            {"rect": (576, 160, 192, 32), "type": "stone"},
            # Very top
            {"rect": (384, 96, 192, 32), "type": "platform"},
        ],
        "spawners": [(60, -20), (S.WIDTH - 60, -20)],
        "crate_spots": [
            (470, 64, 24, 24),
            (272, 128, 24, 24),
            (656, 128, 24, 24),
            (112, 192, 24, 24),
            (816, 192, 24, 24),
            (470, 256, 24, 24),
        ]
    },
    "volcano": {
        "name": "Volcano Rim",
        "description": "Fight on the crater edge",
        "tile_type": "stone",
        "platforms": [
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground
            # Volcano rim - V shape
            {"rect": (32, 256, 160, 32), "type": "stone"},
            {"rect": (160, 320, 128, 32), "type": "stone"},
            {"rect": (256, 384, 128, 32), "type": "platform"},
            {"rect": (576, 384, 128, 32), "type": "platform"},
            {"rect": (672, 320, 128, 32), "type": "stone"},
            {"rect": (768, 256, 160, 32), "type": "stone"},
            # Upper platforms
            {"rect": (128, 160, 160, 32), "type": "platform"},
            {"rect": (672, 160, 160, 32), "type": "platform"},
            # Center floating platforms
            {"rect": (384, 288, 192, 32), "type": "stone"},
            {"rect": (416, 160, 128, 32), "type": "platform"},
            # Top
            {"rect": (352, 64, 256, 32), "type": "stone"},
        ],
        "spawners": [(80, -20), (S.WIDTH - 80, -20)],
        "crate_spots": [
            (96, 224, 24, 24),
            (832, 224, 24, 24),
            (470, 256, 24, 24),
            (470, 128, 24, 24),
            (192, 128, 24, 24),
            (736, 128, 24, 24),
        ]
    },
    "spiral": {
        "name": "Spiral Tower",
        "description": "Ascend the winding path",
        "tile_type": "platform",
        "platforms": [
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground
            # Spiral ascending pattern
            {"rect": (64, 416, 256, 32), "type": "platform"},
            {"rect": (448, 384, 256, 32), "type": "stone"},
            {"rect": (192, 320, 256, 32), "type": "platform"},
            {"rect": (512, 256, 256, 32), "type": "stone"},
            {"rect": (128, 192, 256, 32), "type": "platform"},
            {"rect": (448, 128, 256, 32), "type": "stone"},
            {"rect": (256, 64, 256, 32), "type": "platform"},
            # Small connecting platforms
            {"rect": (320, 384, 64, 32), "type": "stone"},
            {"rect": (704, 320, 64, 32), "type": "platform"},
            {"rect": (448, 256, 64, 32), "type": "stone"},
            {"rect": (768, 192, 64, 32), "type": "platform"},
            {"rect": (384, 128, 64, 32), "type": "stone"},
        ],
        "spawners": [(100, -20), (S.WIDTH - 100, -20)],
        "crate_spots": [
            (176, 384, 24, 24),
            (560, 352, 24, 24),
            (304, 288, 24, 24),
            (624, 224, 24, 24),
            (240, 160, 24, 24),
            (560, 96, 24, 24),
            (368, 32, 24, 24),
        ]
    },
    "bunkers": {
        "name": "War Bunkers",
        "description": "Take cover and fight",
        "tile_type": "stone",
        "platforms": [
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground
            # Left bunker
            {"rect": (32, 352, 224, 32), "type": "stone"},
            {"rect": (32, 256, 64, 32), "type": "stone"},
            {"rect": (192, 256, 64, 32), "type": "stone"},
            {"rect": (32, 160, 224, 32), "type": "stone"},
            # Right bunker
            {"rect": (704, 352, 224, 32), "type": "stone"},
            {"rect": (704, 256, 64, 32), "type": "stone"},
            {"rect": (864, 256, 64, 32), "type": "stone"},
            {"rect": (704, 160, 224, 32), "type": "stone"},
            # Center platforms
            {"rect": (320, 384, 320, 32), "type": "platform"},
            {"rect": (384, 288, 192, 32), "type": "stone"},
            {"rect": (352, 192, 256, 32), "type": "platform"},
            # Top connections
            {"rect": (256, 96, 128, 32), "type": "platform"},
            {"rect": (576, 96, 128, 32), "type": "platform"},
        ],
        "spawners": [(120, -20), (S.WIDTH - 120, -20)],
        "crate_spots": [
            (128, 320, 24, 24),
            (800, 320, 24, 24),
            (470, 352, 24, 24),
            (470, 256, 24, 24),
            (304, 64, 24, 24),
            (624, 64, 24, 24),
        ]
    },
    "crossroads": {
        "name": "Crossroads",
        "description": "Paths cross in all directions",
        "tile_type": "platform",
        "platforms": [
            {"rect": (0, S.HEIGHT - 32, S.WIDTH, 32), "type": "ground"},  # Ground
            # Horizontal main platform
            {"rect": (128, 256, 704, 32), "type": "stone"},
            # Vertical platforms (stepped)
            {"rect": (416, 352, 128, 32), "type": "platform"},
            {"rect": (416, 160, 128, 32), "type": "platform"},
            {"rect": (416, 64, 128, 32), "type": "stone"},
            # Corner platforms
            {"rect": (32, 384, 160, 32), "type": "platform"},
            {"rect": (768, 384, 160, 32), "type": "platform"},
            {"rect": (32, 128, 160, 32), "type": "platform"},
            {"rect": (768, 128, 160, 32), "type": "platform"},
            # Diagonal connectors
            {"rect": (192, 192, 128, 32), "type": "stone"},
            {"rect": (640, 192, 128, 32), "type": "stone"},
            {"rect": (192, 320, 128, 32), "type": "stone"},
            {"rect": (640, 320, 128, 32), "type": "stone"},
        ],
        "spawners": [(80, -20), (S.WIDTH - 80, -20)],
        "crate_spots": [
            (470, 32, 24, 24),
            (470, 128, 24, 24),
            (96, 352, 24, 24),
            (832, 352, 24, 24),
            (96, 96, 24, 24),
            (832, 96, 24, 24),
            (470, 224, 24, 24),
        ]
    }
}

MAP_LIST = list(MAPS.keys())

# Original design resolution for scaling
DESIGN_WIDTH = 960
DESIGN_HEIGHT = 540


class Level:
    def __init__(self, map_id: str = "classic"):
        self.platforms = pg.sprite.Group()
        self.map_id = map_id
        self.load_map(map_id)
    
    def load_map(self, map_id: str, screen_width=None, screen_height=None):
        """Load a specific map with proper scaling"""
        self.platforms.empty()
        
        if map_id not in MAPS:
            map_id = "classic"
        
        self.map_id = map_id
        map_data = MAPS[map_id]
        
        self.name = map_data["name"]
        self.description = map_data["description"]
        default_tile_type = map_data.get("tile_type", "solid")
        
        # Use provided screen size or settings
        width = screen_width or S.WIDTH
        height = screen_height or S.HEIGHT
        
        # Calculate scale factors from design resolution
        scale_x = width / DESIGN_WIDTH
        scale_y = height / DESIGN_HEIGHT
        
        # Load platforms with tile types and scale them
        for p in map_data["platforms"]:
            if isinstance(p, dict):
                rect = list(p["rect"])
                tile_type = p.get("type", default_tile_type)
            else:
                # Legacy format (tuple)
                rect = list(p)
                tile_type = default_tile_type
            
            # Scale the rectangle
            # Handle S.WIDTH and S.HEIGHT in original values
            orig_x, orig_y, orig_w, orig_h = rect
            
            # Check if x or width uses S.WIDTH (for full-width platforms)
            if orig_w >= DESIGN_WIDTH - 10:  # Nearly full width
                scaled_x = 0
                scaled_w = width
            else:
                scaled_x = int(orig_x * scale_x)
                scaled_w = int(orig_w * scale_x)
            
            # Check if y is at bottom (ground floor)
            if orig_y >= DESIGN_HEIGHT - 64:  # Near bottom
                scaled_y = height - 32
            else:
                scaled_y = int(orig_y * scale_y)
            
            scaled_h = int(orig_h * scale_y)
            # Ensure minimum height of one tile
            scaled_h = max(scaled_h, 32)
            
            scaled_rect = (scaled_x, scaled_y, scaled_w, scaled_h)
            self.platforms.add(Platform(scaled_rect, tile_type=tile_type))
        
        # Scale spawners
        self.spawners = []
        for sp in map_data["spawners"]:
            # Handle S.WIDTH references in spawner positions
            if sp[0] > DESIGN_WIDTH / 2:
                # Right side spawner - scale from right edge
                scaled_x = width - int((DESIGN_WIDTH - sp[0]) * scale_x)
            else:
                scaled_x = int(sp[0] * scale_x)
            self.spawners.append((scaled_x, sp[1]))
        
        # Scale crate spots
        self.crate_spots = []
        for r in map_data["crate_spots"]:
            scaled_x = int(r[0] * scale_x)
            scaled_y = int(r[1] * scale_y)
            scaled_w = int(r[2] * scale_x)
            scaled_h = int(r[3] * scale_y)
            self.crate_spots.append(pg.Rect(scaled_x, scaled_y, scaled_w, scaled_h))

    def random_crate_spot(self):
        return random.choice(self.crate_spots).center
    
    @staticmethod
    def get_map_list():
        """Get list of all available maps"""
        return [(map_id, MAPS[map_id]["name"], MAPS[map_id]["description"]) for map_id in MAP_LIST]
    
    @staticmethod
    def get_map_count():
        return len(MAP_LIST)
