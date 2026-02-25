import numpy as np
import time
import colorsys
import math
import random
import pygame
from ui import Theme

# Shared fade configuration
FADE_TIME = 4.0

# Optional note mapping (used by demo_v3 keyboard mode)
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
    """2D point with fade-out lifetime on screen.
    Inputs: x/y pixel coordinates, RGB color tuple, birth timestamp.
    Outputs: alpha queries and alive-check based on FADE_TIME."""

    def __init__(self, x, y, color, birth):
        self.x, self.y, self.color, self.birth_time = x, y, color, birth
    def get_alpha(self, now):
        age = now - self.birth_time
        return 0.0 if age >= FADE_TIME else 1.0 - (age / FADE_TIME)
    def is_alive(self, now): return (now - self.birth_time) < FADE_TIME


class TrailPoint3D:
    """Single 3D trail point in world space.
    Inputs: x/y/z coordinates, RGB color tuple, birth timestamp.
    Outputs: alpha and alive state used for depth-sorted drawing."""

    def __init__(self, x, y, z, color, birth):
        self.x, self.y, self.z = x, y, z
        self.color = color
        self.birth_time = birth

    def get_alpha(self, now):
        age = now - self.birth_time
        return 0.0 if age >= FADE_TIME else 1.0 - (age / FADE_TIME)

    def is_alive(self, now):
        return (now - self.birth_time) < FADE_TIME


class TripleFrequency3DVisualizer:
    """3D Lissajous visualizer driven by three frequencies.
    Inputs: target surface width/height in pixels.
    Outputs: maintains internal 3D trail and renders onto a pygame surface."""

    def __init__(self, w, h):
        self.width, self.height = w, h
        # 3D trail points stored in world coordinates
        self.points = []

        # Three frequencies (x, y, z)
        self.target_freq_x = self.target_freq_y = self.target_freq_z = 0
        self.current_freq_x = self.current_freq_y = self.current_freq_z = 0
        self.phase_x = self.phase_y = self.phase_z = 0.0

        self.target_color = (100, 100, 100)
        self.current_color = (100, 100, 100)

        self.speed_factor = 0.0003
        self.smooth_factor = 0.1

        self.lerp_steps = 30
        self.last_point = self.second_last_point = None
        self.use_catmull_rom = True

        # 3D Lissajous amplitude (world space, before projection)
        # Slightly reduced radius so points do not touch the border
        self.axis_scale = 0.9
        # Perspective: X = focal * x / (z + z_offset), Y = focal * y / (z + z_offset)
        # focal ~ z_offset so projected X,Y stay roughly in [-1, 1], then view_scale maps to pixels
        self.z_offset = 2.5   # z in [-1,1] -> zc in [1.5, 3.5]
        self.focal = 2.5      # X = focal*x/zc => X in about [-1.7, 1.7]
        # Slightly reduced projection scale to leave more margin around the view
        self.view_scale = 240.0  # px = width/2 + view_scale*X => on-screen

        # Rotation only (no zoom): mouse drag, slight fixed tilt
        self.base_rot_deg = -23.0  # Reference tilt angle in degrees
        self.base_rot_x = math.radians(self.base_rot_deg)
        self.rot_x = 0.0        # Dynamic extra pitch (kept at 0, we only use base tilt)
        self.rot_y = 0.0
        self.mouse_sensitivity = 0.005  # rad per pixel

        # Additional controls: volume (0–1) / delay (0–1)
        self.volume = 1.0
        self.delay = 0.0

    def set_frequencies(self, k1, k2, k3):
        if all(k in NOTE_FREQUENCIES for k in (k1, k2, k3)):
            self.set_frequencies_direct(
                NOTE_FREQUENCIES[k1], NOTE_FREQUENCIES[k2], NOTE_FREQUENCIES[k3]
            )
            c1, c2, c3 = NOTE_COLORS[k1], NOTE_COLORS[k2], NOTE_COLORS[k3]
            r = (c1[0] + c2[0] + c3[0]) // 3
            g = (c1[1] + c2[1] + c3[1]) // 3
            b = (c1[2] + c2[2] + c3[2]) // 3
            self.target_color = (r, g, b)

    def set_frequencies_direct(self, f1, f2, f3):
        self.target_freq_x = f1
        self.target_freq_y = f2
        self.target_freq_z = f3
        h1 = (f1 % 1000) / 1000.0
        h2 = (f2 % 1000) / 1000.0
        h3 = (f3 % 1000) / 1000.0
        c1 = colorsys.hsv_to_rgb(h1, 0.8, 0.9)
        c2 = colorsys.hsv_to_rgb(h2, 0.8, 0.9)
        c3 = colorsys.hsv_to_rgb(h3, 0.8, 0.9)
        r = int((c1[0] + c2[0] + c3[0]) / 3 * 255)
        g = int((c1[1] + c2[1] + c3[1]) / 3 * 255)
        b = int((c1[2] + c2[2] + c3[2]) / 3 * 255)
        self.target_color = (r, g, b)

    def set_volume(self, v):
        """Set global brightness multiplier for trail rendering.
        Inputs: v in [0, 1] controlling opacity and glow intensity.
        Outputs: updates internal volume factor; no return value."""
        self.volume = max(0.0, min(1.0, float(v)))

    def set_delay(self, v):
        """Set jitter/attenuation parameter for trail coherence.
        Inputs: v in [0, 1] controlling smoothness versus scattered particles.
        Outputs: updates internal delay factor; no return value."""
        self.delay = max(0.0, min(1.0, float(v)))

    def set_base_tilt_deg(self, deg):
        """Set base camera tilt angle in degrees.
        Inputs: deg clamped to [-180, 180] in world space.
        Outputs: updates base_rot_deg / base_rot_x; no return value."""
        deg = max(-180.0, min(180.0, float(deg)))
        self.base_rot_deg = deg
        self.base_rot_x = math.radians(deg)

    def _rotate_point(self, x, y, z):
        """Apply camera rotation around screen-up axis then pitch.
        Inputs: world-space x, y, z coordinates.
        Outputs: rotated coordinates (xr, yr, zr) in camera-aligned space."""
        # Keep screen up axis fixed: first rotate around up vector, then apply pitch R_x
        # Screen up in world = R_x(-total_rot_x) * (0, 1, 0) = (0, cos(total_rot_x), sin(total_rot_x))
        total_rot_x = self.base_rot_x + self.rot_x
        cx, sx = math.cos(total_rot_x), math.sin(total_rot_x)
        ux, uy, uz = 0.0, cx, sx
        cos_y = math.cos(self.rot_y)
        sin_y = math.sin(self.rot_y)
        # Rodrigues formula: rotate around arbitrary unit axis u by rot_y
        dot = ux * x + uy * y + uz * z
        cross_x = uy * z - uz * y
        cross_y = uz * x - ux * z
        cross_z = ux * y - uy * x
        x1 = x * cos_y + cross_x * sin_y + ux * dot * (1 - cos_y)
        y1 = y * cos_y + cross_y * sin_y + uy * dot * (1 - cos_y)
        z1 = z * cos_y + cross_z * sin_y + uz * dot * (1 - cos_y)
        # Then apply pitch rotation R_x around screen-horizontal axis
        y2 = y1 * cx - z1 * sx
        z2 = y1 * sx + z1 * cx
        return x1, y2, z2

    def _project(self, x, y, z, clamp=True):
        zc = z + self.z_offset
        if zc <= 0.01:
            zc = 0.01
        X = self.focal * x / zc
        Y = self.focal * y / zc
        px = self.width / 2 + self.view_scale * X
        py = self.height / 2 - self.view_scale * Y
        if clamp:
            px = max(0, min(self.width - 1, px))
            py = max(0, min(self.height - 1, py))
        return px, py

    def add_rotation(self, dx, dy):
        """Update horizontal rotation from mouse drag.
        Inputs: dx, dy mouse deltas in pixels (dy currently ignored).
        Outputs: adjusts yaw rot_y; no return value."""
        self.rot_y += dx * self.mouse_sensitivity

    def update(self):
        """Advance phases, interpolate world-space points and manage trail.
        Inputs: none; uses internal target frequencies and elapsed time.
        Outputs: updates self.points, phases and colors; no return value."""
        now = time.time()

        if self.target_freq_x > 0 and self.target_freq_y > 0 and self.target_freq_z > 0:
            if self.current_freq_x == 0:
                self.current_freq_x = self.target_freq_x
                self.current_freq_y = self.target_freq_y
                self.current_freq_z = self.target_freq_z
                self.current_color = self.target_color
            else:
                self.current_freq_x += (self.target_freq_x - self.current_freq_x) * self.smooth_factor
                self.current_freq_y += (self.target_freq_y - self.current_freq_y) * self.smooth_factor
                self.current_freq_z += (self.target_freq_z - self.current_freq_z) * self.smooth_factor
            curr_r, curr_g, curr_b = [c/255.0 for c in self.current_color]
            curr_h, curr_s, curr_v = colorsys.rgb_to_hsv(curr_r, curr_g, curr_b)
            target_r, target_g, target_b = [c/255.0 for c in self.target_color]
            target_h, target_s, target_v = colorsys.rgb_to_hsv(target_r, target_g, target_b)
            diff = target_h - curr_h
            if diff > 0.5: diff -= 1.0
            elif diff < -0.5: diff += 1.0
            next_h = (curr_h + diff * self.smooth_factor) % 1.0
            next_s = curr_s + (target_s - curr_s) * self.smooth_factor
            next_v = curr_v + (target_v - curr_v) * self.smooth_factor
            next_rgb = colorsys.hsv_to_rgb(next_h, next_s, next_v)
            self.current_color = tuple(int(c * 255) for c in next_rgb)
        else:
            self.current_freq_x *= 0.95
            self.current_freq_y *= 0.95
            self.current_freq_z *= 0.95

        if self.current_freq_x >= 1 and self.current_freq_y >= 1 and self.current_freq_z >= 1:
            self.phase_x += self.current_freq_x * self.speed_factor
            self.phase_y += self.current_freq_y * self.speed_factor
            self.phase_z += self.current_freq_z * self.speed_factor

            # Generate new 3D trail point in world coordinates
            xw = self.axis_scale * np.sin(self.phase_x)
            yw = self.axis_scale * np.sin(self.phase_y)
            zw = self.axis_scale * np.sin(self.phase_z)
            color = tuple(int(c) for c in self.current_color)
            curr = TrailPoint3D(xw, yw, zw, color, now)

            # Perform Catmull-Rom / linear interpolation in 3D world space
            # Keep interpolation steps stable so point count is mostly delay-independent
            steps = max(0, int(self.lerp_steps))

            if self.use_catmull_rom and self.second_last_point and self.last_point and steps > 0:
                p3 = TrailPoint3D(
                    2 * curr.x - self.last_point.x,
                    2 * curr.y - self.last_point.y,
                    2 * curr.z - self.last_point.z,
                    color,
                    now,
                )
                for i in range(1, steps + 1):
                    t = i / (steps + 1)
                    self.points.append(self._catmull(self.second_last_point, self.last_point, curr, p3, t))
            elif self.last_point and steps > 0:
                for i in range(1, steps + 1):
                    t = i / (steps + 1)
                    self.points.append(self._lerp(self.last_point, curr, t))

            self.points.append(curr)
            self.second_last_point = self.last_point
            self.last_point = curr

        # Remove expired points and rebuild last / second_last references
        self.points = [p for p in self.points if p.is_alive(now)]
        if len(self.points) >= 2:
            self.second_last_point, self.last_point = self.points[-2], self.points[-1]
        elif len(self.points) == 1:
            self.second_last_point, self.last_point = None, self.points[0]
        else:
            self.second_last_point = self.last_point = None

    def _catmull(self, p0, p1, p2, p3, t):
        """Catmull–Rom interpolation between 3D trail points.
        Inputs: four TrailPoint3D control points and parameter t in [0, 1].
        Outputs: new TrailPoint3D with jitter and brightness falloff applied."""
        t2, t3 = t*t, t*t*t
        c0 = -0.5*t3 + t2 - 0.5*t
        c1 = 1.5*t3 - 2.5*t2 + 1.0
        c2 = -1.5*t3 + 2.0*t2 + 0.5*t
        c3 = 0.5*t3 - 0.5*t2
        x = c0*p0.x + c1*p1.x + c2*p2.x + c3*p3.x
        y = c0*p0.y + c1*p1.y + c2*p2.y + c3*p3.y
        z = c0*p0.z + c1*p1.z + c2*p2.z + c3*p3.z
        color = tuple(int(max(0, min(255, c1*p1.color[i] + c2*p2.color[i]))) for i in range(3))
        birth = (1-t)*p1.birth_time + t*p2.birth_time
        # Larger delay scatters points more around the main curve; closer points stay brighter
        if self.delay > 0.0:
            # Overall scale of spatial jitter is reduced by about 3.5x
            jitter_amp = self.axis_scale * (0.4 / 3.5) * self.delay
            dx = jitter_amp * (random.random()*2 - 1)
            dy = jitter_amp * (random.random()*2 - 1)
            dz = jitter_amp * (random.random()*2 - 1)
            x += dx
            y += dy
            z += dz
            d = math.sqrt(dx*dx + dy*dy + dz*dz) if jitter_amp > 0 else 0.0
            # Farther from the original curve, points become slightly dimmer (down to ~60%)
            falloff = 1.0 - 0.4 * min(1.0, d / jitter_amp)
            color = tuple(int(c * falloff) for c in color)
        return TrailPoint3D(x, y, z, color, birth)

    def _lerp(self, p1, p2, t):
        """Linear interpolation between two 3D trail points.
        Inputs: endpoints p1/p2 and parameter t in [0, 1].
        Outputs: new TrailPoint3D with optional jitter and brightness falloff."""
        x = p1.x*(1-t) + p2.x*t
        y = p1.y*(1-t) + p2.y*t
        z = p1.z*(1-t) + p2.z*t
        color = tuple(int(p1.color[i]*(1-t) + p2.color[i]*t) for i in range(3))
        birth = p1.birth_time*(1-t) + p2.birth_time*t
        if self.delay > 0.0:
            jitter_amp = self.axis_scale * (0.4 / 3.5) * self.delay
            dx = jitter_amp * (random.random()*2 - 1)
            dy = jitter_amp * (random.random()*2 - 1)
            dz = jitter_amp * (random.random()*2 - 1)
            x += dx
            y += dy
            z += dz
            d = math.sqrt(dx*dx + dy*dy + dz*dz) if jitter_amp > 0 else 0.0
            falloff = 1.0 - 0.4 * min(1.0, d / jitter_amp)
            color = tuple(int(c * falloff) for c in color)
        return TrailPoint3D(x, y, z, color, birth)

    def draw(self, surf):
        """Render 3D axes, trail particles and glow to a surface.
        Inputs: pygame Surface covering the main 3D viewport.
        Outputs: draws using current state; no return value."""
        now = time.time()
        items = []  # (depth, kind, color, size, x1, y1, x2?, y2?)
        vol_gain = 1.0 + 1.5 * self.volume

        projected = []
        if self.points:
            for p in self.points:
                xr, yr, zr = self._rotate_point(p.x, p.y, p.z)
                zc = zr + self.z_offset
                if zc <= 0.01:
                    zc = 0.01
                X = self.focal * xr / zc
                Y = self.focal * yr / zc
                px = self.width / 2 + self.view_scale * X
                py = self.height / 2 - self.view_scale * Y
                px = max(0, min(self.width - 1, px))
                py = max(0, min(self.height - 1, py))
                projected.append((px, py, zr, zc))

        axis_len = 1.8
        axis_color = Theme.GOLD_DIM
        axes = [
            ((-axis_len, 0, 0), (axis_len, 0, 0)),
            ((0, -axis_len, 0), (0, axis_len, 0)),
            ((0, 0, -axis_len), (0, 0, axis_len)),
        ]
        for (x0, y0, z0), (x1, y1, z1) in axes:
            xr0, yr0, zr0 = self._rotate_point(x0, y0, z0)
            xr1, yr1, zr1 = self._rotate_point(x1, y1, z1)
            zc0 = zr0 + self.z_offset
            zc1 = zr1 + self.z_offset
            if zc0 <= 0.01 or zc1 <= 0.01:
                continue
            X0 = self.focal * xr0 / zc0
            Y0 = self.focal * yr0 / zc0
            X1 = self.focal * xr1 / zc1
            Y1 = self.focal * yr1 / zc1
            px0 = self.width / 2 + self.view_scale * X0
            py0 = self.height / 2 - self.view_scale * Y0
            px1 = self.width / 2 + self.view_scale * X1
            py1 = self.height / 2 - self.view_scale * Y1
            depth = (zc0 + zc1) / 2.0
            items.append((depth, "line", axis_color, 3, px0, py0, px1, py1))

        arrow_len = 12
        margin = 4
        for (x0, y0, z0), (x1, y1, z1) in axes:
            xr0, yr0, zr0 = self._rotate_point(x0, y0, z0)
            xr1, yr1, zr1 = self._rotate_point(x1, y1, z1)
            zc1 = zr1 + self.z_offset
            if zc1 <= 0.01:
                continue
            X1 = self.focal * xr1 / zc1
            Y1 = self.focal * yr1 / zc1
            px1 = self.width / 2 + self.view_scale * X1
            py1 = self.height / 2 - self.view_scale * Y1
            tx = max(margin, min(self.width - 1 - margin, px1))
            ty = max(margin, min(self.height - 1 - margin, py1))
            cx = self.width / 2
            cy = self.height / 2
            dx = tx - cx
            dy = ty - cy
            norm = math.hypot(dx, dy)
            if norm < 1e-3:
                continue
            ux, uy = dx / norm, dy / norm
            bx = tx - ux * arrow_len
            by = ty - uy * arrow_len
            angle = math.radians(25)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            lx = bx + (ux * cos_a - uy * sin_a) * (arrow_len * 0.6)
            ly = by + (ux * sin_a + uy * cos_a) * (arrow_len * 0.6)
            rx = bx + (ux * cos_a + uy * sin_a) * (arrow_len * 0.6)
            ry = by + (-ux * sin_a + uy * cos_a) * (arrow_len * 0.6)
            depth_arrow = zc1
            items.append((depth_arrow, "line", axis_color, 3, tx, ty, lx, ly))
            items.append((depth_arrow, "line", axis_color, 3, tx, ty, rx, ry))

        center_x = self.width / 2
        center_y = self.height / 2
        pygame.draw.circle(surf, (200, 200, 200), (int(center_x), int(center_y)), 3)

        if self.points:
            last = self.points[-1]
            xr, yr, zr = self._rotate_point(last.x, last.y, last.z)
            zc = zr + self.z_offset
            if zc < 0.01:
                zc = 0.01
            X = self.focal * xr / zc
            Y = self.focal * yr / zc
            px = self.width / 2 + self.view_scale * X
            py = self.height / 2 - self.view_scale * Y
            alpha = last.get_alpha(now)
            if alpha > 0:
                glow_color = last.color
                gc = tuple(int(min(255, v * alpha * vol_gain)) for v in glow_color)
                s = pygame.Surface((50, 50), pygame.SRCALPHA)
                pygame.draw.circle(s, (*gc, 80), (25, 25), 20)
                surf.blit(s, (px - 25, py - 25))
                pygame.draw.circle(surf, (255, 255, 255), (int(px), int(py)), 4)

            if projected:
                for (pxp, pyp, zr_p, zc_p), p in zip(projected, self.points):
                    a = p.get_alpha(now)
                    if a <= 0:
                        continue
                    base_c = p.color
                    c = tuple(int(min(255, base_c[k] * a * vol_gain)) for k in range(3))
                    radius = max(1, int((1 + 1.5 * a) * 0.25))
                    for _ in range(2):
                        jx = (random.random()*2 - 1) * 1.0
                        jy = (random.random()*2 - 1) * 1.0
                        pxj = pxp + jx
                        pyj = pyp + jy
                        items.append((zc_p, "point", c, radius, pxj, pyj, 0, 0))

        items.sort(key=lambda it: it[0], reverse=True)
        for _, kind, color, size, x1, y1, x2, y2 in items:
            if kind == "line":
                pygame.draw.line(surf, color, (int(x1), int(y1)), (int(x2), int(y2)), int(size))
            elif kind == "point":
                pygame.draw.circle(surf, color, (int(x1), int(y1)), int(size))

    def clear(self):
        """Clear all trail points and reset interpolation state.
        Inputs: none.
        Outputs: empties point list and last/second_last references."""
        self.points = []
        self.last_point = None
        self.second_last_point = None
