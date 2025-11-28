import pygame as pg
import math
from . import settings as S

def gradient_bg(surf, top=(24,28,48), bottom=(10,10,18)):
    h = surf.get_height()
    for y in range(h):
        t = y / max(1, h-1)
        r = int(top[0]*(1-t) + bottom[0]*t)
        g = int(top[1]*(1-t) + bottom[1]*t)
        b = int(top[2]*(1-t) + bottom[2]*t)
        pg.draw.line(surf, (r,g,b), (0,y), (surf.get_width(), y))

def draw_panel(surf, rect, bg=S.PANEL_BG, border=S.PANEL_BORDER, glow=False):
    if glow:
        for i in range(3, 0, -1):
            expanded = rect.inflate(i*4, i*4)
            alpha = 60 - i*15
            glow_surf = pg.Surface((expanded.width, expanded.height), pg.SRCALPHA)
            pg.draw.rect(glow_surf, (*S.GLOW_COLOR, alpha), glow_surf.get_rect(), border_radius=14)
            surf.blit(glow_surf, expanded.topleft)
    pg.draw.rect(surf, bg, rect, border_radius=12)
    pg.draw.rect(surf, border, rect, width=3, border_radius=12)
    inner = rect.inflate(-6, -6)
    pg.draw.rect(surf, (255,255,255,30), inner, width=1, border_radius=9)

def text(surf, font, msg, color, pos, shadow=False, center=False, glow=False):
    if glow:
        for offset in [(0,4),(4,0),(-4,0),(0,-4)]:
            g = font.render(msg, True, (color[0]//3, color[1]//3, color[2]//3))
            r = g.get_rect()
            if center:
                r.center = (pos[0]+offset[0], pos[1]+offset[1])
            else:
                r.topleft = (pos[0]+offset[0], pos[1]+offset[1])
            surf.blit(g, r)
    img = font.render(msg, True, color)
    r = img.get_rect()
    if center:
        r.center = pos
    else:
        r.topleft = pos
    surf.blit(img, r)
    return r

def button(surf, font, label, rect, hot=False):
    bg = (28, 28, 40) if not hot else (48, 60, 90)
    border = S.PANEL_BORDER if not hot else (120, 180, 255)
    draw_panel(surf, rect, bg=bg, border=border, glow=hot)
    col = S.FG_COLOR if not hot else (255, 255, 120)
    text(surf, font, label, col, (rect.centerx, rect.centery-1), center=True, glow=hot)
    return rect
