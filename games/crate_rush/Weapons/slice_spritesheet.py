"""
Sprite Sheet Slicer
====================
This script slices a sprite sheet into individual weapon sprites.

Usage:
    python slice_spritesheet.py <spritesheet_image> [--cell-width W] [--cell-height H] [--output-dir DIR]

Example:
    python slice_spritesheet.py weapons_sheet.png --cell-width 32 --cell-height 32
    python slice_spritesheet.py weapons_sheet.png --auto  # Auto-detect sprites
"""

import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow is required. Install it with: pip install Pillow")
    sys.exit(1)


def slice_by_grid(image_path, cell_width, cell_height, output_dir, padding=0):
    """Slice sprite sheet by fixed grid size."""
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    
    os.makedirs(output_dir, exist_ok=True)
    
    cols = width // cell_width
    rows = height // cell_height
    
    count = 0
    for row in range(rows):
        for col in range(cols):
            x = col * cell_width + padding
            y = row * cell_height + padding
            
            # Crop the cell
            cell = img.crop((x, y, x + cell_width - padding*2, y + cell_height - padding*2))
            
            # Check if cell has any non-transparent pixels
            if has_content(cell):
                output_path = os.path.join(output_dir, f"sprite_{row:02d}_{col:02d}.png")
                cell.save(output_path)
                count += 1
                print(f"Saved: {output_path}")
    
    print(f"\nTotal sprites extracted: {count}")
    return count


def has_content(image, threshold=10):
    """Check if image has non-transparent content."""
    pixels = list(image.getdata())
    non_transparent = sum(1 for p in pixels if len(p) == 4 and p[3] > threshold)
    return non_transparent > 5  # At least 5 non-transparent pixels


def find_sprites_auto(image_path, output_dir, min_size=8, bg_color=None):
    """Auto-detect and extract individual sprites based on bounding boxes."""
    img = Image.open(image_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a mask of non-transparent/non-background pixels
    visited = [[False] * width for _ in range(height)]
    sprites = []
    
    def is_sprite_pixel(x, y):
        if x < 0 or x >= width or y < 0 or y >= height:
            return False
        pixel = pixels[x, y]
        # Check if pixel is not transparent
        if len(pixel) == 4 and pixel[3] < 10:
            return False
        # Check if pixel is not background color
        if bg_color and pixel[:3] == bg_color:
            return False
        return True
    
    def flood_fill(start_x, start_y):
        """Find bounding box of connected sprite pixels."""
        if not is_sprite_pixel(start_x, start_y) or visited[start_y][start_x]:
            return None
        
        min_x, max_x = start_x, start_x
        min_y, max_y = start_y, start_y
        
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack.pop()
            
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            if visited[y][x]:
                continue
            if not is_sprite_pixel(x, y):
                continue
            
            visited[y][x] = True
            
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            
            # Check neighbors (4-connected for speed, use 8 for diagonal)
            stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
            # 8-connected (include diagonals)
            stack.extend([(x+1, y+1), (x-1, y-1), (x+1, y-1), (x-1, y+1)])
        
        return (min_x, min_y, max_x + 1, max_y + 1)
    
    # Scan image for sprites
    print("Scanning for sprites...")
    for y in range(height):
        for x in range(width):
            bbox = flood_fill(x, y)
            if bbox:
                bw = bbox[2] - bbox[0]
                bh = bbox[3] - bbox[1]
                if bw >= min_size and bh >= min_size:
                    sprites.append(bbox)
    
    # Sort sprites by position (top-to-bottom, left-to-right)
    sprites.sort(key=lambda b: (b[1] // 20, b[0]))
    
    # Extract and save sprites
    print(f"Found {len(sprites)} sprites")
    for i, bbox in enumerate(sprites):
        # Add 1 pixel padding
        padded_bbox = (
            max(0, bbox[0] - 1),
            max(0, bbox[1] - 1),
            min(width, bbox[2] + 1),
            min(height, bbox[3] + 1)
        )
        sprite = img.crop(padded_bbox)
        output_path = os.path.join(output_dir, f"weapon_{i:03d}.png")
        sprite.save(output_path)
        print(f"Saved: {output_path} (size: {sprite.size})")
    
    print(f"\nTotal sprites extracted: {len(sprites)}")
    return len(sprites)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Slice a sprite sheet into individual sprites")
    parser.add_argument("image", help="Path to the sprite sheet image")
    parser.add_argument("--cell-width", "-cw", type=int, help="Cell width for grid slicing")
    parser.add_argument("--cell-height", "-ch", type=int, help="Cell height for grid slicing")
    parser.add_argument("--auto", "-a", action="store_true", help="Auto-detect sprites")
    parser.add_argument("--output-dir", "-o", default="sliced_sprites", help="Output directory")
    parser.add_argument("--min-size", type=int, default=8, help="Minimum sprite size for auto mode")
    parser.add_argument("--padding", "-p", type=int, default=0, help="Padding between cells in grid mode")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.image):
        print(f"Error: Image file '{args.image}' not found")
        sys.exit(1)
    
    if args.auto:
        find_sprites_auto(args.image, args.output_dir, min_size=args.min_size)
    elif args.cell_width and args.cell_height:
        slice_by_grid(args.image, args.cell_width, args.cell_height, args.output_dir, args.padding)
    else:
        # Interactive mode
        print(f"\nSprite Sheet Slicer")
        print(f"=" * 40)
        print(f"Image: {args.image}")
        
        img = Image.open(args.image)
        print(f"Size: {img.size[0]} x {img.size[1]} pixels")
        
        print(f"\nChoose slicing method:")
        print(f"  1. Grid-based (specify cell size)")
        print(f"  2. Auto-detect (find individual sprites)")
        
        choice = input("\nEnter choice (1 or 2): ").strip()
        
        if choice == "1":
            cell_w = int(input("Cell width (e.g., 16, 32): "))
            cell_h = int(input("Cell height (e.g., 16, 32): "))
            slice_by_grid(args.image, cell_w, cell_h, args.output_dir)
        else:
            find_sprites_auto(args.image, args.output_dir, min_size=args.min_size)
    
    print(f"\nSprites saved to: {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()
