# How to Play - Simple Guide

## Quick Start (Step by Step)

### Step 1: Start the Game
```bash
python start_localhost.py
```

### Step 2: Choose Option
- Choose **3** (Start Both Server + Client)

### Step 3: Wait for Windows
- A **server window** will open (leave this running)
- A **client window** will open (this is your game)

### Step 4: Connect to Server
- In the client window, you'll see a connection dialog
- Type: `localhost`
- Press **Enter**

### Step 5: Play the Game!
- You should see a 3D space scene with asteroids
- Your ship is the green triangle

## Game Controls

### Movement
- **W** - Move forward
- **A** - Move left  
- **S** - Move backward
- **D** - Move right

### Combat
- **Mouse** - Look around (move mouse to rotate ship)
- **Left Click** - Shoot lasers

### Menu
- **Escape** - Open menu/Exit

## What You Should See

1. **Black space background** with stars
2. **Gray asteroids** floating around
3. **Your ship** (green triangle)
4. **Other players** (blue triangles) if connected
5. **Health/Ammo bars** in top-left corner

## Troubleshooting

### If you can't move:
- Make sure the game window is **focused** (click on it)
- Try pressing **W** to move forward
- Check if you see your ship (green triangle)

### If you can't shoot:
- Make sure you're **left-clicking** in the game window
- You should see yellow laser beams

### If the game seems stuck:
- Press **Escape** to open the menu
- Try reconnecting by choosing the connection option again

## Common Issues

**Problem**: Game opens but nothing happens
**Solution**: Make sure you typed `localhost` correctly when connecting

**Problem**: Can't see my ship
**Solution**: Move your mouse around to look around, your ship should be visible

**Problem**: Can't move
**Solution**: Click on the game window first, then try WASD keys

## Need Help?
Run this diagnostic: `python diagnose_game.py`
