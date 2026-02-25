"""
SON Demo V3 - Triple Frequency 3D Lissajous (Perspective Projection)
With Teensy serial communication for real-time frequency input.
Format: f1;f2;f3 (e.g., 261.63;329.63;392.00)
"""

import threading
import time

import pygame
import serial

from ui import Button, FrequencyBar, Label, Slider, Theme, draw_corners, draw_grid
from visualizer_3d import TripleFrequency3DVisualizer

# Config
WIDTH, HEIGHT = 1280, 800
SIDEBAR_WIDTH = 320
MAIN_VIEW_WIDTH = WIDTH - SIDEBAR_WIDTH
FPS = 60

# Serial config
SERIAL_PORT = "/dev/ttyACM0"
SERIAL_BAUDRATE = 1000000
SERIAL_TIMEOUT = 0.1


class TeensyReader:
    """Thread-safe serial reader for Teensy frequency data.
    Reads lines in format: f1;f2;f3 (e.g., 261.63;329.63;392.00)
    """

    def __init__(
        self, port=SERIAL_PORT, baudrate=SERIAL_BAUDRATE, timeout=SERIAL_TIMEOUT
    ):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.frequencies = (0.0, 0.0, 0.0)
        self.connected = False
        self.last_error = None
        self.new_data = False  # Flag to indicate new data received

    def start(self):
        """Start the serial reading thread."""
        self.running = True
        self.thread = threading.Thread(target=self._read_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the serial reading thread and close the port."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if self.serial:
            try:
                self.serial.close()
            except Exception:
                pass
            self.serial = None
        self.connected = False

    def _connect(self):
        """Attempt to connect to the serial port."""
        try:
            if self.serial:
                self.serial.close()
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(0.5)  # Brief wait for connection to stabilize
            self.connected = True
            self.last_error = None
            print(f"[Teensy] Connected on {self.port}")
            return True
        except serial.SerialException as e:
            self.connected = False
            self.last_error = str(e)
            return False

    def _read_loop(self):
        """Main reading loop running in separate thread."""
        reconnect_delay = 2.0
        last_reconnect_attempt = 0

        while self.running:
            # Try to connect if not connected
            if not self.connected:
                current_time = time.time()
                if current_time - last_reconnect_attempt >= reconnect_delay:
                    last_reconnect_attempt = current_time
                    if not self._connect():
                        time.sleep(0.1)
                        continue

            # Read data
            try:
                if self.serial and self.serial.in_waiting > 0:
                    line = self.serial.readline().decode("utf-8").rstrip()
                    if line:
                        self._parse_frequencies(line)
                else:
                    time.sleep(0.005)  # Small delay to avoid busy-waiting
            except serial.SerialException as e:
                self.connected = False
                self.last_error = str(e)
                print(f"[Teensy] Serial error: {e}")
            except UnicodeDecodeError:
                # Ignore decode errors and continue
                pass

    def _parse_frequencies(self, line):
        """Parse a line in format: f1;f2;f3"""
        try:
            parts = line.split(";")
            if len(parts) >= 3:
                f1 = float(parts[0])
                f2 = float(parts[1])
                f3 = float(parts[2])
                with self.lock:
                    self.frequencies = (f1, f2, f3)
                    self.new_data = True
                print(f"[Teensy] Frequencies: {f1:.2f}, {f2:.2f}, {f3:.2f}")
        except ValueError:
            # Invalid format, ignore
            pass

    def get_frequencies(self):
        """Get the latest frequencies (thread-safe). Returns (f1, f2, f3, has_new_data)."""
        with self.lock:
            has_new = self.new_data
            self.new_data = False
            return (
                self.frequencies[0],
                self.frequencies[1],
                self.frequencies[2],
                has_new,
            )

    def is_connected(self):
        """Check if connected to Teensy."""
        return self.connected


def main():
    """Main entry point with Teensy serial integration.
    Reads frequencies from Teensy and visualizes them as 3D Lissajous curves."""
    pygame.init()
    Theme.init_fonts()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SON Visualizer - 3D Lissajous (Teensy)")
    clock = pygame.time.Clock()

    viz = TripleFrequency3DVisualizer(MAIN_VIEW_WIDTH, HEIGHT)

    # Initialize Teensy reader
    teensy = TeensyReader()
    teensy.start()

    ui = []
    y = 20
    ui.append(Label(30, y, "SON VISUALIZER", Theme.FONT_TITLE, Theme.GOLD_PRIMARY))
    y += 50

    # Connection status label
    lbl_status = Label(
        30, y, "Teensy: Connecting...", Theme.FONT_SMALL, Theme.TEXT_GRAY
    )
    ui.append(lbl_status)
    y += 30

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

    def tilt_minus():
        viz.set_base_tilt_deg(viz.base_rot_deg - 5)

    def tilt_plus():
        viz.set_base_tilt_deg(viz.base_rot_deg + 5)

    def tilt_reset():
        viz.set_base_tilt_deg(-23.0)

    btn_tilt_minus = Button(30, y, 80, 32, "Tilt -", tilt_minus)
    btn_tilt_plus = Button(120, y, 80, 32, "Tilt +", tilt_plus)
    btn_tilt_reset = Button(210, y, 80, 32, "Reset", tilt_reset)
    ui.extend([btn_tilt_minus, btn_tilt_plus, btn_tilt_reset])
    y += 42

    def set_smooth(v):
        viz.lerp_steps = int(v)

    ui.append(Slider(30, y, 260, 0, 50, 30, "Smoothness", set_smooth))
    y += 60

    def set_speed(v):
        viz.speed_factor = v / 10000.0  # Range: 0.0001 to 0.01

    ui.append(Slider(30, y, 260, 1, 100, 20, "Speed", set_speed))
    y += 60

    def set_volume_slider(v):
        viz.set_volume(v / 100.0)

    ui.append(Slider(30, y, 260, 0, 100, 100, "Volume", set_volume_slider))
    y += 60

    def set_attenuation_slider(v):
        viz.set_delay(v / 100.0)

    ui.append(Slider(30, y, 260, 0, 100, 0, "Atténuation", set_attenuation_slider))
    y += 60
    ui.append(Button(30, y, 260, 40, "Clear", viz.clear))
    y += 50
    ui.append(
        Button(
            30,
            y,
            260,
            40,
            "Exit",
            lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)),
        )
    )

    running = True
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

        # Get frequencies from Teensy
        f1, f2, f3, has_new = teensy.get_frequencies()
        if has_new and f1 > 0 and f2 > 0 and f3 > 0:
            viz.set_frequencies_direct(f1, f2, f3)
            bar_x.set_value(f1)
            bar_y.set_value(f2)
            bar_z.set_value(f3)

        # Update status label
        if teensy.is_connected():
            lbl_status.set_text("Teensy: Connected")
            lbl_status.color = Theme.SUCCESS_GREEN
        else:
            lbl_status.set_text("Teensy: Disconnected")
            lbl_status.color = Theme.ERROR_RED

        viz.update()
        lbl_pts.set_text(f"Points: {len(viz.points)}")
        lbl_tilt.set_text(f"Tilt: {viz.base_rot_deg:.0f}°")

        screen.fill(Theme.BLACK_BG, (0, 0, SIDEBAR_WIDTH, HEIGHT))
        pygame.draw.rect(screen, (25, 25, 30), (0, 0, SIDEBAR_WIDTH, HEIGHT))
        pygame.draw.line(
            screen, Theme.GOLD_DIM, (SIDEBAR_WIDTH, 0), (SIDEBAR_WIDTH, HEIGHT), 2
        )
        for el in ui:
            el.update(mp)
            el.draw(screen)
        main_surf = screen.subsurface((SIDEBAR_WIDTH, 0, MAIN_VIEW_WIDTH, HEIGHT))
        main_surf.fill(Theme.BLACK_BG)
        draw_grid(main_surf, main_surf.get_rect())
        viz.draw(main_surf)
        draw_corners(main_surf, main_surf.get_rect().inflate(-40, -40))

        # Show status message if no frequencies yet
        if (
            viz.current_freq_x <= 1
            or viz.current_freq_y <= 1
            or viz.current_freq_z <= 1
        ):
            if teensy.is_connected():
                msg = "Waiting for Teensy data..."
            else:
                msg = "Teensy not connected"
            if Theme.FONT_TITLE:
                h = Theme.FONT_TITLE.render(msg, True, (100, 100, 100))
                main_surf.blit(
                    h, h.get_rect(center=(MAIN_VIEW_WIDTH // 2, HEIGHT // 2))
                )

        if Theme.FONT_SMALL:
            hint = Theme.FONT_SMALL.render(
                "SPACE: Clear | ESC: Exit | Drag to rotate", True, (80, 80, 80)
            )
            main_surf.blit(hint, (12, HEIGHT - 28))

        pygame.display.flip()
        clock.tick(FPS)

    # Cleanup
    teensy.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
