# 🎖️ TEAM-BASED COMBAT SYSTEM

## ✅ NEW FEATURES IMPLEMENTED

Your game now features a **COMPLETE TEAM-BASED COMBAT SYSTEM**!

---

## 🎮 HOW IT WORKS

### 1️⃣ TEAM SELECTION SCREEN

When you click "⚡ PLAY GAME" from the main menu, you'll see a **team selection screen**:

- **BLUE TEAM** 🛡️ (Left Card)
  - Defenders
  - Tactical Approach
  - Team Strategy
  - Protect Objectives
  - **Blue tactical uniforms, vests, and helmets**

- **RED TEAM** ⚔️ (Right Card)
  - Attackers
  - Aggressive Style
  - Fast Strikes
  - Capture Territory
  - **Red tactical uniforms, vests, and helmets**

### 2️⃣ CONTROLS

**Team Selection:**
- **← →** (Left/Right Arrows) - Choose team
- **ENTER** or **SPACE** - Confirm selection
- **ESC** - Back to main menu

---

## ⚔️ COMBAT MECHANICS

### FRIENDLY FIRE PROTECTION
**You CANNOT damage teammates!**

- If you're on **BLUE TEAM**, you can only damage **RED TEAM** enemies
- If you're on **RED TEAM**, you can only damage **BLUE TEAM** enemies
- Bullets pass through teammates without dealing damage

### ENEMY TEAM COLORS

Enemies are now **color-coded by team**:

**BLUE TEAM ENEMIES:**
- Blue tactical uniforms
- Blue tactical vests
- Blue helmets
- Shades of blue (varying by enemy type)

**RED TEAM ENEMIES:**
- Red/Maroon tactical uniforms
- Red tactical vests
- Red helmets
- Shades of red (varying by enemy type)

### ENEMY TYPES (Both Teams)

Each team has 3 enemy types with different colors:

1. **WALKER** - Light team colors
   - BLUE: Light blue uniform
   - RED: Light red uniform

2. **RUNNER** - Medium team colors
   - BLUE: Medium blue urban camo
   - RED: Medium red tactical gear

3. **TANK** - Dark team colors
   - BLUE: Navy blue heavy armor
   - RED: Maroon heavy armor

---

## 📊 TECHNICAL DETAILS

### What Was Changed:

1. **Team Selection Screen** (`_render_team_selection()`)
   - Beautiful card-based UI
   - Animated selection indicators
   - Team descriptions and icons
   - Smooth navigation

2. **Team Assignment**
   - Player chooses team before spawning
   - Enemies spawn with opposite team
   - Team data stored in `enemy['team']`

3. **Damage System** (`_update_bullets()`)
   - Team check before applying damage
   - `if enemy.get('team') == self.player_team: continue`
   - Friendly fire prevention

4. **Visual Team Identification**
   - Outfit colors based on team
   - Vest colors based on team
   - Helmet colors based on team
   - Clear visual distinction

---

## 🎯 GAMEPLAY STRATEGY

### AS BLUE TEAM (Defenders):
- Focus on **tactical positioning**
- Use **cover effectively**
- **Defend key areas**
- Work as a cohesive unit

### AS RED TEAM (Attackers):
- **Aggressive pushes**
- **Fast movement**
- **Quick strikes**
- Capture and control territory

---

## 💡 PRO TIPS

1. **Identify Enemies by Color**
   - Blue uniforms = Blue team
   - Red uniforms = Red team
   - Don't waste ammo shooting wrong team!

2. **Team Coordination**
   - Your bullets only damage opposite team
   - Position yourself strategically
   - Use team strengths

3. **Visual Clarity**
   - Look for uniform colors
   - Helmet color is most visible
   - Vest color confirms team

4. **Combat Awareness**
   - Know your team color
   - Focus fire on enemy team
   - Conserve ammunition

---

## 🔧 TECHNICAL IMPLEMENTATION

### Code Changes:

**1. Game State Variables:**
```python
self.player_team = None  # 'BLUE' or 'RED'
self.team_selection = 0  # 0 = BLUE, 1 = RED
self.in_team_selection = False
```

**2. Enemy Spawning:**
```python
enemy_team = 'RED' if self.player_team == 'BLUE' else 'BLUE'
enemy = {
    'team': enemy_team,
    # ... other properties
}
```

**3. Damage Check:**
```python
for enemy in self.enemies:
    if enemy.get('team') == self.player_team:
        continue  # Skip teammates!
    # Apply damage logic
```

**4. Team Colors:**
```python
if enemy_team == 'BLUE':
    outfit_color = (60, 80, 140)  # Blue
    vest_color = (40, 60, 120)
    helmet_color = (30, 50, 100)
else:  # RED
    outfit_color = (140, 60, 60)  # Red
    vest_color = (120, 40, 40)
    helmet_color = (100, 30, 30)
```

---

## 🎨 VISUAL FEATURES

### Team Selection Screen:
- **Gradient background** (dark tactical theme)
- **Large team cards** (500x550px)
- **Animated glow** when selected
- **Team icons** (shield for blue, swords for red)
- **Team descriptions**
- **Selection pulse effect**
- **Clear instructions**

### In-Game Visuals:
- **Ultra-realistic soldiers** with team colors
- **Detailed uniforms** in team colors
- **Tactical vests** color-coded
- **Helmets** with team identification
- **Consistent color scheme**

---

## 🏆 BENEFITS OF TEAM SYSTEM

1. **Strategic Depth**
   - Must identify targets correctly
   - Team-based tactics matter
   - Positioning becomes critical

2. **Visual Clarity**
   - Easy to distinguish friend from foe
   - Color-coded system is intuitive
   - Reduces friendly fire confusion

3. **Immersive Gameplay**
   - Feel like part of a team
   - Realistic military structure
   - Enhanced role-playing

4. **Replayability**
   - Play as different teams
   - Different strategies per team
   - Varied gameplay experience

---

## 📝 CONTROLS SUMMARY

**Team Selection:**
- ← → : Choose team
- ENTER/SPACE : Confirm
- ESC : Back to menu

**In-Game:**
- All previous controls work the same
- Just aim at ENEMY TEAM colors!

---

## ⚠️ IMPORTANT NOTES

1. **Choose Wisely!**
   - You must select a team before starting
   - Team choice affects enemy spawns
   - Enemies will be opposite team

2. **Color Recognition**
   - Blue = Blue Team
   - Red = Red Team
   - Simple and clear!

3. **No Friendly Fire**
   - Your bullets automatically ignore teammates
   - Focus on enemy team only
   - Saves ammunition

4. **Team Persistence**
   - Team choice lasts entire session
   - Return to menu to change teams
   - Each playthrough can be different team

---

## 🎮 QUICK START GUIDE

1. **Launch Game** → Main menu appears
2. **Press Enter** on "⚡ PLAY GAME"
3. **Team Selection Screen** appears
4. **Use ← →** to choose BLUE or RED
5. **Press ENTER** to confirm
6. **Game Starts!** Fight enemy team!

---

## ✨ WHAT'S NEW

### Before:
- ❌ No team system
- ❌ All enemies looked the same
- ❌ No target identification needed

### Now:
- ✅ Full team selection screen
- ✅ Team-coded enemy colors
- ✅ Friendly fire protection
- ✅ Strategic team gameplay
- ✅ Beautiful team UI
- ✅ Realistic tactical combat

---

**Enjoy the new team-based tactical combat!** 🔥

Choose your side and dominate the battlefield!

🔵 **BLUE TEAM** - Tactical Defenders
🔴 **RED TEAM** - Aggressive Attackers

**Which team will you lead to victory?**
