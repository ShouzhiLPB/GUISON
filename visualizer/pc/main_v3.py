"""
SON Music Visualizer V3 - Professional Edition
"""

import pygame
import serial
import serial.tools.list_ports
import time
import threading
import numpy as np
import sys
import os

# Import visualizer components
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
from demo_v3 import DualFrequencyVisualizer, TimedPoint
from ui import Theme, Button, Label, Panel, Slider, FrequencyBar, draw_grid, draw_corners

# ============================================
# Configuration
# ============================================

WIDTH, HEIGHT = 1280, 800
SIDEBAR_WIDTH = 320
MAIN_VIEW_WIDTH = WIDTH - SIDEBAR_WIDTH
SERIAL_BAUDRATE = 115200
SERIAL_TIMEOUT = 0.1
FREQ_UPDATE_INTERVAL = 0.05

# Key Signatures
MAJOR_KEYS = [
    ("C Major", 0), ("G Major", 7), ("D Major", 2), ("A Major", 9),
    ("E Major", 4), ("B Major", 11), ("F# Major", 6), ("C# Major", 1),
    ("F Major", 5), ("Bb Major", 10), ("Eb Major", 3), ("Ab Major", 8),
    ("Db Major", 1), ("Gb Major", 6), ("Cb Major", 11)
]
MINOR_KEYS = [
    ("A Minor", 9), ("E Minor", 4), ("B Minor", 11), ("F# Minor", 6),
    ("C# Minor", 1), ("G# Minor", 8), ("D# Minor", 3), ("A# Minor", 10),
    ("D Minor", 2), ("G Minor", 7), ("C Minor", 0), ("F Minor", 5),
    ("Bb Minor", 10), ("Eb Minor", 3), ("Ab Minor", 8)
]

# ============================================
# Serial Communication
# ============================================

class SerialComm:
    def __init__(self, port=None):
        self.port = port
        self.ser = None
        self.connected = False
        self.running = False
        self.read_thread = None
        self.latest_freq1 = None
        self.latest_freq2 = None
        self.freq_lock = threading.Lock()
    
    def connect(self, port=None):
        if port is None:
            ports = serial.tools.list_ports.comports()
            for p in ports:
                if 'teensy' in p.description.lower() or 'usb serial' in p.description.lower():
                    port = p.device
                    break
            if not port and ports: port = ports[0].device
            
        if not port: return False
        
        try:
            self.ser = serial.Serial(port, SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT)
            time.sleep(2.0)
            self.ser.reset_input_buffer()
            self.port = port
            self.connected = True
            return True
        except:
            return False

    def disconnect(self):
        self.running = False
        if self.read_thread: self.read_thread.join(timeout=1.0)
        if self.ser and self.ser.is_open: self.ser.close()
        self.connected = False

    def send_key(self, note, velocity=100):
        if self.connected:
            try: self.ser.write(f"KEY:{note}:{velocity}\n".encode())
            except: pass

    def send_key_off(self, note):
        if self.connected:
            try: self.ser.write(f"KEY_OFF:{note}\n".encode())
            except: pass

    def read_loop(self):
        self.running = True
        while self.running:
            if self.ser and self.ser.in_waiting > 0:
                try:
                    line = self.ser.readline().decode(errors='ignore').strip()
                    if line.startswith("FREQ:"):
                        parts = line.split(":")
                        if len(parts) >= 3:
                            with self.freq_lock:
                                self.latest_freq1 = float(parts[1])
                                self.latest_freq2 = float(parts[2])
                except: pass
            time.sleep(0.01)

    def start_reading(self):
        if self.connected and not self.running:
            self.read_thread = threading.Thread(target=self.read_loop, daemon=True)
            self.read_thread.start()

    def get_frequencies(self):
        with self.freq_lock: return self.latest_freq1, self.latest_freq2

# ============================================
# Helper Functions
# ============================================

def get_midi_note(key_number, offset):
    scale = [0, 2, 4, 5, 7, 9, 11, 12]
    if 1 <= key_number <= 8:
        return max(0, min(127, 60 + scale[key_number-1] + offset))
    return None

KEY_TO_NUMBER = {
    pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3, pygame.K_4: 4,
    pygame.K_5: 5, pygame.K_6: 6, pygame.K_7: 7, pygame.K_8: 8,
    pygame.K_KP1: 1, pygame.K_KP2: 2, pygame.K_KP3: 3, pygame.K_KP4: 4,
    pygame.K_KP5: 5, pygame.K_KP6: 6, pygame.K_KP7: 7, pygame.K_KP8: 8,
    pygame.K_q: 1, pygame.K_w: 2, pygame.K_r: 4, pygame.K_t: 5, pygame.K_y: 6
}

# ============================================
# 🎹 Key Selection Screen (Hearthstone Style)
# ============================================

def select_key_signature(screen):
    clock = pygame.time.Clock()
    
    # Generate Buttons (Cards)
    major_buttons = []
    minor_buttons = []
    
    # Layout Config - 填满屏幕的布局
    cols = 3
    rows = 5
    
    margin_x = 40
    margin_y = 140
    gap = 15
    
    panel_width = (WIDTH - margin_x * 2 - 40) // 2
    card_w = (panel_width - (cols - 1) * gap) // cols
    card_h = 80 # 卡片高度
    
    selected_key = None # (name, midi)
    
    def on_select(name, midi):
        nonlocal selected_key
        selected_key = (name, midi)

    # --- 左侧：大调卡组 ---
    start_x = margin_x
    start_y = margin_y
    
    for i, (name, midi) in enumerate(MAJOR_KEYS):
        row, col = divmod(i, cols)
        x = start_x + col * (card_w + gap)
        y = start_y + row * (card_h + gap)
        label = name.replace(" Major", "")
        btn = Button(x, y, card_w, card_h, label, callback=lambda n=name, m=midi: on_select(n, m))
        btn.font = Theme.FONT_TITLE
        major_buttons.append(btn)

    # --- 右侧：小调卡组 ---
    start_x = WIDTH // 2 + 20
    
    for i, (name, midi) in enumerate(MINOR_KEYS):
        row, col = divmod(i, cols)
        x = start_x + col * (card_w + gap)
        y = start_y + row * (card_h + gap)
        label = name.replace(" Minor", "m")
        btn = Button(x, y, card_w, card_h, label, callback=lambda n=name, m=midi: on_select(n, m))
        btn.font = Theme.FONT_TITLE
        minor_buttons.append(btn)
        
    all_buttons = major_buttons + minor_buttons
    
    # Start Button
    def on_confirm():
        return "CONFIRM"
        
    start_btn = Button(WIDTH//2 - 150, HEIGHT - 100, 300, 70, "START SESSION", callback=on_confirm)
    start_btn.text_color = Theme.BLACK_BG
    start_btn.base_color = Theme.GOLD_DIM
    start_btn.hover_color = Theme.GOLD_PRIMARY
    start_btn.font = Theme.FONT_TITLE
    
    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: return None
                if selected_key and event.key == pygame.K_RETURN: return selected_key
            
            for btn in all_buttons:
                btn.handle_event(event)
                
            if selected_key:
                if start_btn.handle_event(event): return selected_key

        # Update Buttons Visual State
        for btn in all_buttons:
            btn.update(mouse_pos)
            is_selected = False
            if selected_key:
                s_name_base = selected_key[0].replace(" Major", "").replace(" Minor", "m")
                if btn.text == s_name_base:
                    is_selected = True
            
            if is_selected:
                btn.base_color = Theme.GOLD_PRIMARY
                btn.text_color = Theme.BLACK_BG
            else:
                btn.base_color = (30, 30, 35) # Dark card bg
                btn.text_color = Theme.GOLD_DIM

        if selected_key:
            start_btn.update(mouse_pos)

        # Draw
        screen.fill(Theme.BLACK_BG)
        draw_grid(screen, screen.get_rect())
        
        # Panel Backgrounds
        l_bg_rect = pygame.Rect(margin_x - 10, margin_y - 40, panel_width + 20, (card_h + gap) * rows + 60)
        pygame.draw.rect(screen, (15, 15, 20), l_bg_rect, border_radius=15)
        pygame.draw.rect(screen, (40, 40, 50), l_bg_rect, 1, border_radius=15)
        
        r_bg_rect = pygame.Rect(WIDTH//2 + 10, margin_y - 40, panel_width + 20, (card_h + gap) * rows + 60)
        pygame.draw.rect(screen, (15, 15, 20), r_bg_rect, border_radius=15)
        pygame.draw.rect(screen, (40, 40, 50), r_bg_rect, 1, border_radius=15)

        # Header
        title = Theme.FONT_HUGE.render("CHOOSE YOUR KEY", True, Theme.GOLD_PRIMARY)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 60)))
        
        # Panel Titles
        l_t = Theme.FONT_TITLE.render("MAJOR", True, Theme.TEXT_WHITE)
        r_t = Theme.FONT_TITLE.render("MINOR", True, Theme.TEXT_WHITE)
        screen.blit(l_t, (l_bg_rect.x + 20, l_bg_rect.y + 10))
        screen.blit(r_t, (r_bg_rect.x + 20, r_bg_rect.y + 10))

        for btn in all_buttons:
            btn.draw(screen)
            
        if selected_key:
            start_btn.draw(screen)
            info = Theme.FONT_MAIN.render(f"Ready: {selected_key[0]}", True, Theme.GOLD_LIGHT)
            screen.blit(info, info.get_rect(center=(WIDTH//2, HEIGHT - 130)))
            
        draw_corners(screen, screen.get_rect())

        pygame.display.flip()
        clock.tick(60)

# ============================================
# Main Application
# ============================================

def main():
    pygame.init()
    Theme.init_fonts()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SON V3 Professional")
    clock = pygame.time.Clock()
    
    # Key Selection
    key_sig = select_key_signature(screen)
    if not key_sig: return
    key_name, key_offset = key_sig
    
    # Setup
    viz = DualFrequencyVisualizer(MAIN_VIEW_WIDTH, HEIGHT)
    comm = SerialComm()
    comm.connect()
    comm.start_reading()
    
    # UI Layout
    sidebar_rect = pygame.Rect(0, 0, SIDEBAR_WIDTH, HEIGHT)
    main_view_rect = pygame.Rect(SIDEBAR_WIDTH, 0, MAIN_VIEW_WIDTH, HEIGHT)
    
    ui_elements = []
    
    # --- Sidebar Elements ---
    y = 20
    lbl_title = Label(30, y, "SON VISUALIZER V3", Theme.FONT_TITLE, Theme.GOLD_PRIMARY)
    y += 50
    lbl_status = Label(30, y, "Status: Connected" if comm.connected else "Status: Offline", 
                       Theme.FONT_MAIN, Theme.SUCCESS_GREEN if comm.connected else Theme.ERROR_RED)
    y += 30
    lbl_key = Label(30, y, f"Key: {key_name}", Theme.FONT_MAIN, Theme.TEXT_WHITE)
    
    ui_elements.extend([lbl_title, lbl_status, lbl_key])
    
    y += 50
    bar_x = FrequencyBar(30, y, 260, 20, "X-Axis Freq", max_freq=1000, color=(255, 100, 100))
    y += 60
    bar_y = FrequencyBar(30, y, 260, 20, "Y-Axis Freq", max_freq=1000, color=(100, 200, 255))
    ui_elements.extend([bar_x, bar_y])
    
    y += 60
    lbl_ratio = Label(30, y, "Ratio: --", Theme.FONT_MAIN, Theme.TEXT_GOLD)
    y += 30
    lbl_points = Label(30, y, "Points: 0", Theme.FONT_MAIN, Theme.TEXT_GRAY)
    ui_elements.extend([lbl_ratio, lbl_points])
    
    y += 50
    def set_smooth(val): viz.lerp_steps = int(val)
    slider_smooth = Slider(30, y, 260, 0, 50, 30, "Smoothness", set_smooth)
    ui_elements.append(slider_smooth)
    
    y += 60
    def toggle_interp():
        viz.use_catmull_rom = not viz.use_catmull_rom
        btn_interp.text = "Mode: Catmull" if viz.use_catmull_rom else "Mode: Linear"
    btn_interp = Button(30, y, 260, 40, "Mode: Catmull", toggle_interp)
    y += 50
    btn_clear = Button(30, y, 260, 40, "Clear Screen", viz.clear)
    y += 50
    btn_exit = Button(30, y, 260, 40, "Exit Application", lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)))
    ui_elements.extend([btn_interp, btn_clear, btn_exit])
    
    running = True
    pressed_keys = {}
    last_update = time.time()
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            for el in ui_elements: el.handle_event(event)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: running = False
                elif event.key == pygame.K_SPACE: viz.clear()
                elif event.key in KEY_TO_NUMBER:
                    k = KEY_TO_NUMBER[event.key]
                    note = get_midi_note(k, key_offset)
                    if note and k not in pressed_keys:
                        pressed_keys[k] = note
                        comm.send_key(note)
            elif event.type == pygame.KEYUP:
                if event.key in KEY_TO_NUMBER:
                    k = KEY_TO_NUMBER[event.key]
                    if k in pressed_keys:
                        comm.send_key_off(pressed_keys[k])
                        del pressed_keys[k]

        now = time.time()
        if now - last_update > FREQ_UPDATE_INTERVAL:
            f1, f2 = comm.get_frequencies()
            if f1 and f2:
                if abs(viz.freq1 or 0 - f1) > 0.1 or abs(viz.freq2 or 0 - f2) > 0.1:
                    viz.set_frequencies_direct(f1, f2)
                bar_x.set_value(f1)
                bar_y.set_value(f2)
                lbl_ratio.set_text(f"Ratio: {f2/f1:.3f}")
            last_update = now
            
        viz.update()
        lbl_points.set_text(f"Points: {len(viz.points)}")
        
        # Sidebar
        screen.fill(Theme.BLACK_BG, sidebar_rect)
        pygame.draw.rect(screen, (25, 25, 30), sidebar_rect)
        pygame.draw.line(screen, Theme.GOLD_DIM, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, HEIGHT), 2)
        for el in ui_elements:
            el.update(mouse_pos)
            el.draw(screen)
            
        # Main View
        main_surf = screen.subsurface(main_view_rect)
        main_surf.fill(Theme.BLACK_BG)
        draw_grid(main_surf, main_surf.get_rect())
        viz.draw(main_surf)
        draw_corners(main_surf, main_surf.get_rect().inflate(-40, -40))
        
        if not viz.freq1:
            hint = Theme.FONT_TITLE.render("Waiting for Frequency...", True, (100, 100, 100))
            main_surf.blit(hint, hint.get_rect(center=(MAIN_VIEW_WIDTH//2, HEIGHT//2)))
            
        pygame.display.flip()
        clock.tick(60)

    comm.disconnect()
    pygame.quit()

if __name__ == "__main__":
    main()
