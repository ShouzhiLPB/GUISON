"""
SON Demo V3 - Triple Frequency 3D Lissajous (Perspective Projection)
Keyboard: press 3 keys to set X/Y/Z frequencies. Uses shared visualizer_3d.
"""

import pygame
import time
from ui import Theme, Button, Label, Slider, FrequencyBar, draw_grid, draw_corners
from visualizer_3d import TripleFrequency3DVisualizer, NOTE_FREQUENCIES, NOTE_COLORS

# Config
WIDTH, HEIGHT = 1280, 800
SIDEBAR_WIDTH = 320
MAIN_VIEW_WIDTH = WIDTH - SIDEBAR_WIDTH
FPS = 60



def main():
    """Keyboard-driven demo entry point using the shared 3D visualizer.
    Inputs: none; uses global window configuration and keyboard events.
    Outputs: runs demo loop until window is closed; no explicit return."""
    pygame.init()
    Theme.init_fonts()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SON Demo V3 - 3D Lissajous (Perspective)")
    clock = pygame.time.Clock()

    viz = TripleFrequency3DVisualizer(MAIN_VIEW_WIDTH, HEIGHT)

    ui = []
    y = 20
    ui.append(Label(30, y, "DEMO V3: 3D LISSAJOUS", Theme.FONT_TITLE, Theme.GOLD_PRIMARY))
    y += 50
    bar_x = FrequencyBar(30, y, 260, 20, "X Freq", max_freq=1000, color=(255, 100, 100))
    ui.append(bar_x)
    y += 60
    bar_y = FrequencyBar(30, y, 260, 20, "Y Freq", max_freq=1000, color=(100, 200, 255))
    ui.append(bar_y)
    y += 60
    bar_z = FrequencyBar(30, y, 260, 20, "Z Freq", max_freq=1000, color=(100, 255, 150))
    ui.append(bar_z)
    y += 60
    lbl_pts = Label(30, y, "Points: 0", Theme.FONT_MAIN, Theme.TEXT_GRAY)
    ui.append(lbl_pts)
    y += 30
    # Tilt angle controls
    lbl_tilt = Label(30, y, "Tilt: -23°", Theme.FONT_MAIN, Theme.TEXT_GRAY)
    ui.append(lbl_tilt)
    y += 30
    def tilt_minus(): viz.set_base_tilt_deg(viz.base_rot_deg - 5)
    def tilt_plus(): viz.set_base_tilt_deg(viz.base_rot_deg + 5)
    def tilt_reset(): viz.set_base_tilt_deg(-23.0)
    btn_tilt_minus = Button(30, y, 80, 32, "Tilt -", tilt_minus)
    btn_tilt_plus = Button(120, y, 80, 32, "Tilt +", tilt_plus)
    btn_tilt_reset = Button(210, y, 80, 32, "Reset", tilt_reset)
    ui.extend([btn_tilt_minus, btn_tilt_plus, btn_tilt_reset])
    y += 42
    def set_smooth(v): viz.lerp_steps = int(v)
    ui.append(Slider(30, y, 260, 0, 50, 30, "Smoothness", set_smooth))
    y += 60
    # Volume = glow intensity/saturation; Attenuation = trail continuity and particle spread (decay time)
    def set_volume_slider(v): viz.set_volume(v / 100.0)
    ui.append(Slider(30, y, 260, 0, 100, 100, "Volume", set_volume_slider))
    y += 60
    def set_attenuation_slider(v): viz.set_delay(v / 100.0)
    ui.append(Slider(30, y, 260, 0, 100, 0, "Atténuation", set_attenuation_slider))
    y += 60
    ui.append(Button(30, y, 260, 40, "Clear", viz.clear))
    y += 50
    ui.append(Button(30, y, 260, 40, "Exit", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))))

    running = True
    pressed = set()
    drag_started = False
    last_mouse = (0, 0)

    while running:
        mp = pygame.mouse.get_pos()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if e.pos[0] >= SIDEBAR_WIDTH:
                    drag_started = True
                    last_mouse = e.pos
            elif e.type == pygame.MOUSEMOTION and drag_started and e.buttons[0]:
                dx = e.pos[0] - last_mouse[0]
                dy = e.pos[1] - last_mouse[1]
                viz.add_rotation(dx, dy)
                last_mouse = e.pos
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                drag_started = False
            for el in ui:
                el.handle_event(e)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_SPACE:
                    viz.clear()
                else:
                    k = pygame.key.name(e.key)
                    if k.startswith('[') and k.endswith(']'):
                        k = k[1:-1]
                    if k in NOTE_FREQUENCIES:
                        pressed.add(k)
                        if len(pressed) >= 3:
                            keys = list(pressed)[-3:]
                            viz.set_frequencies(keys[0], keys[1], keys[2])
            elif e.type == pygame.KEYUP:
                k = pygame.key.name(e.key)
                if k.startswith('[') and k.endswith(']'):
                    k = k[1:-1]
                if k in pressed:
                    pressed.remove(k)

        if viz.current_freq_x > 0 and viz.current_freq_y > 0 and viz.current_freq_z > 0:
            bar_x.set_value(viz.current_freq_x)
            bar_y.set_value(viz.current_freq_y)
            bar_z.set_value(viz.current_freq_z)
        viz.update()
        lbl_pts.set_text(f"Points: {len(viz.points)}")
        lbl_tilt.set_text(f"Tilt: {viz.base_rot_deg:.0f}°")

        screen.fill(Theme.BLACK_BG, (0, 0, SIDEBAR_WIDTH, HEIGHT))
        pygame.draw.rect(screen, (25, 25, 30), (0, 0, SIDEBAR_WIDTH, HEIGHT))
        pygame.draw.line(screen, Theme.GOLD_DIM, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, HEIGHT), 2)
        for el in ui:
            el.update(mp)
            el.draw(screen)
        main_surf = screen.subsurface((SIDEBAR_WIDTH, 0, MAIN_VIEW_WIDTH, HEIGHT))
        main_surf.fill(Theme.BLACK_BG)
        draw_grid(main_surf, main_surf.get_rect())
        viz.draw(main_surf)
        draw_corners(main_surf, main_surf.get_rect().inflate(-40, -40))
        if viz.current_freq_x <= 1 or viz.current_freq_y <= 1 or viz.current_freq_z <= 1:
            h = Theme.FONT_TITLE.render("Press 3 Keys", True, (100, 100, 100))
            main_surf.blit(h, h.get_rect(center=(MAIN_VIEW_WIDTH // 2, HEIGHT // 2)))
        hint = Theme.FONT_SMALL.render("Drag to rotate (no zoom)", True, (80, 80, 80))
        main_surf.blit(hint, (12, HEIGHT - 28))
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__": main()
