import pygame
import math

# ==========================================
# 🎨 Modern Black & Gold Theme Definition
# ==========================================
class Theme:
    # Colors
    BLACK_BG = (10, 10, 12)        # Very dark blue-ish black
    BLACK_PANEL = (20, 20, 25)     # Slightly lighter panel background
    BLACK_OVERLAY = (0, 0, 0, 180) # Semi-transparent overlay
    
    GOLD_PRIMARY = (255, 215, 0)   # Classic Gold
    GOLD_DIM = (184, 134, 11)      # Dark Goldenrod
    GOLD_LIGHT = (255, 240, 150)   # Pale Gold (for highlights)
    GOLD_DARK = (100, 80, 20)      # Very dark gold for backgrounds
    
    TEXT_WHITE = (240, 240, 240)
    TEXT_GRAY = (160, 160, 160)
    TEXT_GOLD = (220, 200, 120)
    
    ERROR_RED = (200, 50, 50)
    SUCCESS_GREEN = (50, 200, 50)
    
    GRID_COLOR = (30, 30, 35)

    # Fonts (Initialized later)
    FONT_MAIN = None
    FONT_TITLE = None
    FONT_SMALL = None
    FONT_HUGE = None

    @staticmethod
    def init_fonts():
        if Theme.FONT_MAIN is None:
            pygame.font.init()
            # Try to use a modern font, fallback to system default
            fonts = ['segoeui', 'arial', 'microsoftyahei', 'simhei']
            font_name = pygame.font.match_font(fonts[0])
            
            Theme.FONT_HUGE = pygame.font.Font(font_name, 64)
            Theme.FONT_TITLE = pygame.font.Font(font_name, 36)
            Theme.FONT_MAIN = pygame.font.Font(font_name, 20)
            Theme.FONT_SMALL = pygame.font.Font(font_name, 14)

# ==========================================
# 🛠️ UI Base Component
# ==========================================
class UIElement:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.hovered = False
        self.active = True
        self.visible = True

    def update(self, mouse_pos):
        if not self.visible or not self.active:
            self.hovered = False
            return
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        pass

    def handle_event(self, event):
        pass

# ==========================================
# 🔘 Modern Button
# ==========================================
class Button(UIElement):
    def __init__(self, x, y, width, height, text, callback=None, color=None):
        super().__init__(x, y, width, height)
        self.text = text
        self.callback = callback
        self.base_color = color if color else Theme.GOLD_DIM
        self.hover_color = Theme.GOLD_PRIMARY
        self.text_color = Theme.BLACK_BG
        self.corner_radius = 6
        self.animation_progress = 0.0  # 0.0 to 1.0 for hover effect
        self.font = None # Use default if None

    def update(self, mouse_pos):
        super().update(mouse_pos)
        # Smooth animation
        target = 1.0 if self.hovered else 0.0
        self.animation_progress += (target - self.animation_progress) * 0.2

    def draw(self, surface):
        if not self.visible:
            return

        font = self.font if self.font else Theme.FONT_MAIN

        # Interpolate color
        r = self.base_color[0] + (self.hover_color[0] - self.base_color[0]) * self.animation_progress
        g = self.base_color[1] + (self.hover_color[1] - self.base_color[1]) * self.animation_progress
        b = self.base_color[2] + (self.hover_color[2] - self.base_color[2]) * self.animation_progress
        current_color = (int(r), int(g), int(b))

        # Glow effect (draw larger, transparent rect behind)
        if self.animation_progress > 0.05:
            glow_surf = pygame.Surface((self.rect.width + 12, self.rect.height + 12), pygame.SRCALPHA)
            glow_alpha = int(60 * self.animation_progress)
            pygame.draw.rect(glow_surf, (*Theme.GOLD_PRIMARY, glow_alpha), 
                           (0, 0, self.rect.width + 12, self.rect.height + 12), 
                           border_radius=self.corner_radius + 4)
            surface.blit(glow_surf, (self.rect.x - 6, self.rect.y - 6))

        # Main Button Body
        pygame.draw.rect(surface, current_color, self.rect, border_radius=self.corner_radius)
        
        # Border (Gold)
        border_width = 2 if self.hovered else 1
        pygame.draw.rect(surface, Theme.GOLD_PRIMARY, self.rect, border_width, border_radius=self.corner_radius)

        # Text
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if not self.visible or not self.active:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered and self.callback:
                self.callback()
                return True
        return False

# ==========================================
# 🏷️ Label / Text Display
# ==========================================
class Label(UIElement):
    def __init__(self, x, y, text, font=None, color=None, align="left"):
        super().__init__(x, y, 0, 0) # Width/Height dynamic
        self.text = text
        self.font = font
        self.color = color if color else Theme.GOLD_PRIMARY
        self.align = align
        self.shadow_color = (0, 0, 0)
        self.shadow_offset = (2, 2)

    def set_text(self, text):
        self.text = text

    def draw(self, surface):
        if not self.visible:
            return
            
        font = self.font if self.font else Theme.FONT_MAIN

        # Shadow
        shadow_surf = font.render(self.text, True, self.shadow_color)
        
        # Main Text
        text_surf = font.render(self.text, True, self.color)
        
        width = text_surf.get_width()
        height = text_surf.get_height()
        
        # Calculate Position
        pos_x = self.rect.x
        pos_y = self.rect.y
        
        if self.align == "center":
            pos_x = self.rect.x - width // 2
        elif self.align == "right":
            pos_x = self.rect.x - width
            
        # Draw Shadow then Text
        surface.blit(shadow_surf, (pos_x + self.shadow_offset[0], pos_y + self.shadow_offset[1]))
        surface.blit(text_surf, (pos_x, pos_y))

# ==========================================
# 📦 Panel / Container
# ==========================================
class Panel(UIElement):
    def __init__(self, x, y, width, height, title=None):
        super().__init__(x, y, width, height)
        self.title = title
        self.border_color = Theme.GOLD_DIM
        self.bg_color = (20, 20, 25, 230) # Semi-transparent

    def draw(self, surface):
        if not self.visible:
            return

        # Transparent Background
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill(self.bg_color)
        surface.blit(s, (self.rect.x, self.rect.y))

        # Border
        pygame.draw.rect(surface, self.border_color, self.rect, 1, border_radius=5)

        # Title
        if self.title:
            font = Theme.FONT_MAIN
            title_surf = font.render(self.title, True, Theme.GOLD_PRIMARY)
            # Draw title background strip
            title_bg_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 32)
            pygame.draw.rect(surface, (40, 40, 50), title_bg_rect, border_top_left_radius=5, border_top_right_radius=5)
            pygame.draw.rect(surface, self.border_color, title_bg_rect, 1, border_top_left_radius=5, border_top_right_radius=5)
            
            surface.blit(title_surf, (self.rect.x + 10, self.rect.y + 5))

# ==========================================
# 🎚️ Slider (Simple)
# ==========================================
class Slider(UIElement):
    def __init__(self, x, y, width, min_val, max_val, initial_val, label, callback=None):
        super().__init__(x, y, width, 40)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.callback = callback
        self.dragging = False

    def update(self, mouse_pos):
        super().update(mouse_pos)
        if self.dragging:
            rel_x = mouse_pos[0] - self.rect.x
            ratio = max(0, min(1, rel_x / self.rect.width))
            new_val = self.min_val + ratio * (self.max_val - self.min_val)
            if new_val != self.value:
                self.value = new_val
                if self.callback:
                    self.callback(self.value)

    def handle_event(self, event):
        if not self.visible: return False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hovered:
                self.dragging = True
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            return False
        return False

    def draw(self, surface):
        if not self.visible: return

        font = Theme.FONT_SMALL

        # Label
        label_surf = font.render(f"{self.label}: {self.value:.0f}", True, Theme.TEXT_GRAY)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 18))

        # Track
        track_rect = pygame.Rect(self.rect.x, self.rect.y + 10, self.rect.width, 4)
        pygame.draw.rect(surface, (60, 60, 60), track_rect, border_radius=2)
        
        # Fill
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        fill_width = int(ratio * self.rect.width)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y + 10, fill_width, 4)
        pygame.draw.rect(surface, Theme.GOLD_PRIMARY, fill_rect, border_radius=2)

        # Knob
        knob_x = int(self.rect.x + fill_width)
        knob_y = int(self.rect.y + 12)
        color = Theme.GOLD_LIGHT if self.dragging or self.hovered else Theme.GOLD_DIM
        pygame.draw.circle(surface, color, (knob_x, knob_y), 8)

# ==========================================
# 📊 Frequency Bar (动态频率条)
# ==========================================
class FrequencyBar(UIElement):
    def __init__(self, x, y, width, height, label, max_freq=1000, color=None):
        super().__init__(x, y, width, height)
        self.label = label
        self.value = 0
        self.max_freq = max_freq
        self.target_value = 0
        self.bar_color = color if color else Theme.GOLD_PRIMARY
        
    def set_value(self, freq):
        self.target_value = freq

    def update(self, mouse_pos):
        super().update(mouse_pos)
        # 平滑动画
        self.value += (self.target_value - self.value) * 0.1

    def draw(self, surface):
        if not self.visible: return

        # Label
        font = Theme.FONT_SMALL
        val_text = f"{int(self.value)} Hz" if self.value > 10 else "---"
        label_surf = font.render(f"{self.label}: {val_text}", True, Theme.TEXT_GOLD)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 18))

        # Background Track
        pygame.draw.rect(surface, (30, 30, 35), self.rect, border_radius=4)
        
        # Fill Bar
        ratio = min(1.0, max(0.0, self.value / self.max_freq))
        fill_width = int(self.rect.width * ratio)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(surface, self.bar_color, fill_rect, border_radius=4)

        # Border
        pygame.draw.rect(surface, (60, 60, 70), self.rect, 1, border_radius=4)

# ==========================================
# 📐 Decorative Elements (装饰元素)
# ==========================================
def draw_grid(surface, rect, spacing=40, color=(30, 30, 35)):
    """绘制背景网格"""
    for x in range(rect.left, rect.right, spacing):
        pygame.draw.line(surface, color, (x, rect.top), (x, rect.bottom))
    for y in range(rect.top, rect.bottom, spacing):
        pygame.draw.line(surface, color, (rect.left, y), (rect.right, y))

def draw_corners(surface, rect, length=20, color=Theme.GOLD_PRIMARY):
    """绘制四个角落的装饰线"""
    # Top Left
    pygame.draw.line(surface, color, (rect.left, rect.top), (rect.left + length, rect.top), 2)
    pygame.draw.line(surface, color, (rect.left, rect.top), (rect.left, rect.top + length), 2)
    # Top Right
    pygame.draw.line(surface, color, (rect.right, rect.top), (rect.right - length, rect.top), 2)
    pygame.draw.line(surface, color, (rect.right, rect.top), (rect.right, rect.top + length), 2)
    # Bottom Left
    pygame.draw.line(surface, color, (rect.left, rect.bottom), (rect.left + length, rect.bottom), 2)
    pygame.draw.line(surface, color, (rect.left, rect.bottom), (rect.left, rect.bottom - length), 2)
    # Bottom Right
    pygame.draw.line(surface, color, (rect.right, rect.bottom), (rect.right - length, rect.bottom), 2)
    pygame.draw.line(surface, color, (rect.right, rect.bottom), (rect.right, rect.bottom - length), 2)
