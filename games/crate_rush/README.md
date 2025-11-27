Crate Rush (Super Crate Box–style)

Overview
- Fast, arcade platformer: collect crates to change weapons.
- Endless enemy spawns ramp difficulty; one hit resets your run.

Controls
- Move: A/D or Left/Right
- Jump: Space (W/Up also works)
- Shoot: J or F or Left Mouse

Run (Windows PowerShell)
```
# From the repo root or anywhere:
cd "c:\Users\hp\OneDrive\Documents\python-offensive-tool\games"

# Create venv inside the game folder if needed
if (!(Test-Path .\crate_rush\.venv)) { python -m venv .\crate_rush\.venv }

# Install dependencies using the venv's python
& ".\crate_rush\.venv\Scripts\python.exe" -m pip install -r .\crate_rush\requirements.txt

# Launch the game (must run from the parent 'games' dir)
& ".\crate_rush\.venv\Scripts\python.exe" -m crate_rush.main
```

Notes
- Window size: 960x540 @ 60 FPS.
- Weapons: Pistol, SMG, Shotgun, Rocket. New one on each crate.
- Score = crates collected this run. Highscore now saves to `save.json`.
- UI: Title screen (Enter to start), Pause (P/Esc), Game Over (R to retry).
