"""
SON Demo V3 - Dual Frequency (Professional Edition)
"""

import pygame
import numpy as np
import time
import colorsys
from ui import Theme, Button, Label, Panel, Slider, FrequencyBar, draw_grid, draw_corners

# Config
WIDTH, HEIGHT = 1280, 800
SIDEBAR_WIDTH = 320
MAIN_VIEW_WIDTH = WIDTH - SIDEBAR_WIDTH
FPS = 60
FADE_TIME = 4.0

NOTE_FREQUENCIES = {
    '1': 261.63, '2': 293.66, '3': 329.63, '4': 349.23,
    '5': 392.00, '6': 440.00, '7': 493.88, '8': 523.25,
    'q': 277.18, 'w': 311.13, 'r': 369.99, 't': 415.30, 'y': 466.16
}
NOTE_COLORS = {
    '1': (255, 100, 100), '2': (255, 150, 50), '3': (255, 255, 100),
    '4': (100, 255, 100), '5': (100, 200, 255), '6': (150, 100, 255),
    '7': (255, 100, 200), '8': (255, 200, 200),
    'q': (200, 80, 80), 'w': (200, 120, 40),
    'r': (80, 200, 200), 't': (80, 150, 200), 'y': (120, 80, 200)
}

class TimedPoint:
    def __init__(self, x, y, color, birth):
        self.x, self.y, self.color, self.birth_time = x, y, color, birth
    def get_alpha(self, now):
        age = now - self.birth_time
        return 0.0 if age >= FADE_TIME else 1.0 - (age / FADE_TIME)
    def is_alive(self, now): return (now - self.birth_time) < FADE_TIME

class DualFrequencyVisualizer:
    def __init__(self, w, h):
        self.width, self.height = w, h
        self.points = []
        self.t = 0
        self.speed = 0.006
        self.freq1 = self.freq2 = None
        self.color1 = self.color2 = None
        self.lerp_steps = 30
        self.last_point = self.second_last_point = None
        self.use_catmull_rom = True
        
    def set_frequencies(self, k1, k2):
        if k1 in NOTE_FREQUENCIES and k2 in NOTE_FREQUENCIES:
            self.freq1, self.freq2 = NOTE_FREQUENCIES[k1], NOTE_FREQUENCIES[k2]
            self.color1, self.color2 = NOTE_COLORS[k1], NOTE_COLORS[k2]
            self.clear()
            
    def set_frequencies_direct(self, f1, f2):
        self.freq1, self.freq2 = f1, f2
        h1, h2 = (f1%1000)/1000.0, (f2%1000)/1000.0
        self.color1 = tuple(int(c*255) for c in colorsys.hsv_to_rgb(h1, 0.8, 0.9))
        self.color2 = tuple(int(c*255) for c in colorsys.hsv_to_rgb(h2, 0.8, 0.9))
        self.clear()

    def update(self):
        if not self.freq1 or not self.freq2: return
        self.t += self.speed
        now = time.time()
        
        w1, w2 = 2*np.pi*self.freq1/100, 2*np.pi*self.freq2/100
        xp, yp = np.sin(w1*self.t), np.sin(w2*self.t)
        
        scale = 300
        sx, sy = int(self.width/2 + xp*scale), int(self.height/2 + yp*scale)
        color = tuple(int((self.color1[i]+self.color2[i])/2) for i in range(3))
        
        curr = (sx, sy, color, now)
        
        if self.use_catmull_rom and self.second_last_point and self.last_point:
            p3 = (2*sx - self.last_point[0], 2*sy - self.last_point[1], color, now)
            for i in range(1, self.lerp_steps + 1):
                t = i / (self.lerp_steps + 1)
                self.points.append(self.catmull(self.second_last_point, self.last_point, curr, p3, t))
        elif self.last_point:
            for i in range(1, self.lerp_steps + 1):
                t = i / (self.lerp_steps + 1)
                self.points.append(self.lerp(self.last_point, curr, t))
                
        self.points.append(TimedPoint(*curr))
        self.second_last_point = self.last_point
        self.last_point = curr
        self.points = [p for p in self.points if p.is_alive(now)]

    def catmull(self, p0, p1, p2, p3, t):
        t2, t3 = t*t, t*t*t
        c0, c1 = -0.5*t3 + t2 - 0.5*t, 1.5*t3 - 2.5*t2 + 1.0
        c2, c3 = -1.5*t3 + 2.0*t2 + 0.5*t, 0.5*t3 - 0.5*t2
        x = int(c0*p0[0] + c1*p1[0] + c2*p2[0] + c3*p3[0])
        y = int(c0*p0[1] + c1*p1[1] + c2*p2[1] + c3*p3[1])
        color = tuple(int(max(0, min(255, c1*p1[2][i] + c2*p2[2][i]))) for i in range(3))
        return TimedPoint(x, y, color, (1-t)*p1[3] + t*p2[3])

    def lerp(self, p1, p2, t):
        x = int(p1[0]*(1-t) + p2[0]*t)
        y = int(p1[1]*(1-t) + p2[1]*t)
        color = tuple(int(p1[2][i]*(1-t) + p2[2][i]*t) for i in range(3))
        return TimedPoint(x, y, color, p1[3]*(1-t) + p2[3]*t)

    def draw(self, surf):
        if not self.points: return
        now = time.time()
        for i in range(len(self.points)-1):
            p1, p2 = self.points[i], self.points[i+1]
            a = p1.get_alpha(now)
            if a > 0:
                c = tuple(int(v*a) for v in p1.color)
                pygame.draw.line(surf, c, (p1.x, p1.y), (p2.x, p2.y), max(1, int(4*a)))
        
        last = self.points[-1]
        a = last.get_alpha(now)
        if a > 0:
            gc = tuple(int(v*a) for v in last.color)
            s = pygame.Surface((50,50), pygame.SRCALPHA)
            pygame.draw.circle(s, (*gc, 80), (25,25), 20)
            surf.blit(s, (last.x-25, last.y-25))
            pygame.draw.circle(surf, (255,255,255), (last.x, last.y), 4)

    def clear(self): self.points = []; self.last_point = None

def main():
    pygame.init()
    Theme.init_fonts()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SON Demo V3 - Professional")
    clock = pygame.time.Clock()
    
    viz = DualFrequencyVisualizer(MAIN_VIEW_WIDTH, HEIGHT)
    
    # UI
    ui = []
    y = 20
    ui.append(Label(30, y, "DEMO V3: DUAL FREQ", Theme.FONT_TITLE, Theme.GOLD_PRIMARY))
    
    y += 50
    bar_x = FrequencyBar(30, y, 260, 20, "X-Axis Freq", max_freq=1000, color=(255,100,100))
    ui.append(bar_x)
    y += 60
    bar_y = FrequencyBar(30, y, 260, 20, "Y-Axis Freq", max_freq=1000, color=(100,200,255))
    ui.append(bar_y)
    
    y += 60
    lbl_ratio = Label(30, y, "Ratio: --", Theme.FONT_MAIN, Theme.TEXT_GOLD)
    ui.append(lbl_ratio)
    y += 30
    lbl_pts = Label(30, y, "Points: 0", Theme.FONT_MAIN, Theme.TEXT_GRAY)
    ui.append(lbl_pts)
    
    y += 50
    def set_smooth(v): viz.lerp_steps = int(v)
    ui.append(Slider(30, y, 260, 0, 50, 30, "Smoothness", set_smooth))
    
    y += 60
    btn_mode = Button(30, y, 260, 40, "Mode: Catmull", lambda: setattr(viz, 'use_catmull_rom', not viz.use_catmull_rom))
    ui.append(btn_mode)
    y += 50
    ui.append(Button(30, y, 260, 40, "Clear", viz.clear))
    y += 50
    ui.append(Button(30, y, 260, 40, "Exit", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))))
    
    running = True
    pressed = set()
    
    while running:
        mp = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: running = False
            for el in ui: el.handle_event(e)
            
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: running = False
                elif e.key == pygame.K_SPACE: viz.clear()
                else:
                    k = pygame.key.name(e.key)
                    # Numpad fixes
                    if k.startswith('[') and k.endswith(']'): k = k[1:-1]
                    if k in NOTE_FREQUENCIES:
                        pressed.add(k)
                        if len(pressed) >= 2:
                            keys = list(pressed)[-2:]
                            viz.set_frequencies(keys[0], keys[1])
            elif e.type == pygame.KEYUP:
                k = pygame.key.name(e.key)
                if k.startswith('[') and k.endswith(']'): k = k[1:-1]
                if k in pressed: pressed.remove(k)
                    
        if viz.freq1 and viz.freq2:
            bar_x.set_value(viz.freq1)
            bar_y.set_value(viz.freq2)
            lbl_ratio.set_text(f"Ratio: {viz.freq2/viz.freq1:.3f}")
            
        viz.update()
        lbl_pts.set_text(f"Points: {len(viz.points)}")
        btn_mode.text = "Mode: Catmull" if viz.use_catmull_rom else "Mode: Linear"
        
        # Sidebar
        screen.fill(Theme.BLACK_BG, (0,0,SIDEBAR_WIDTH,HEIGHT))
        pygame.draw.rect(screen, (25,25,30), (0,0,SIDEBAR_WIDTH,HEIGHT))
        pygame.draw.line(screen, Theme.GOLD_DIM, (SIDEBAR_WIDTH,0), (SIDEBAR_WIDTH,HEIGHT), 2)
        for el in ui: el.update(mp); el.draw(screen)
        
        # Main
        main_surf = screen.subsurface((SIDEBAR_WIDTH, 0, MAIN_VIEW_WIDTH, HEIGHT))
        main_surf.fill(Theme.BLACK_BG)
        draw_grid(main_surf, main_surf.get_rect())
        viz.draw(main_surf)
        draw_corners(main_surf, main_surf.get_rect().inflate(-40,-40))
        
        if not viz.freq1:
            h = Theme.FONT_TITLE.render("Press 2 Keys", True, (100,100,100))
            main_surf.blit(h, h.get_rect(center=(MAIN_VIEW_WIDTH//2, HEIGHT//2)))
        
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()

if __name__ == "__main__": main()
