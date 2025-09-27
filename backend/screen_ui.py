import tkinter as tk
from typing import Tuple, Dict
from dataclasses import dataclass
from drive_modes import SpeedMode, SPEED_MODES

class Colors:
    RED = "#FF0060"
    YELLOW = "#F6FA70"
    GREEN = "#00DFA2"
    BLUE = "#0079FF"
    GRAY = "#6b7280"
    LIGHT_GRAY = "#9ca3af"
    BLACK = "#111827"


@dataclass
class ScreenUIUpdate:
    speed_mph: float
    power_watts: float
    battery_pct: float
    speed_mode: "SpeedMode"

class DialWidget:
    """
    Minimalist dial with a clean Tesla-like aesthetic.
    - Draws a background arc, value arc, center label, and value text.
    - Smoothly animates toward target values for a responsive feel.
    """

    def __init__(
        self,
        root: tk.Misc,
        center: Tuple[int, int],
        radius: int,
        label: str,
        unit: str,
        min_value: float,
        max_value: float,
        arc_extent_deg: int = 240,
        bg: str = "white",
        fg: str = "black",
        accent: str = Colors.BLUE,
    ) -> None:
        self.root = root
        self.center_x, self.center_y = center
        self.radius = radius
        self.label = label
        self.unit = unit
        self.min_value = min_value
        self.max_value = max_value
        self.arc_extent_deg = arc_extent_deg
        self.bg = bg
        self.fg = fg
        self.accent = accent

        size = (radius * 2) + 20
        self.canvas = tk.Canvas(
            root, width=size, height=size, bg=bg, highlightthickness=0, bd=0
        )
        self.canvas.place(x=self.center_x - size // 2, y=self.center_y - size // 2)

        # Internal state for animation
        self._target_value: float = 0.0
        self._display_value: float = 0.0
        self._tick_running: bool = False

        # Precompute geometry
        self._bbox = (10, 10, size - 10, size - 10)
        # Centered dial with 240-degree sweep, opening downward (top-oriented arc)
        # Tk angles: 0=3 o'clock, 90=12 o'clock. Start at 330 (just right of bottom)
        # and sweep counterclockwise for a top arc.
        self._start_angle = 330
        # For value arc we start at the left end of the top arc (clockwise fill)
        self._value_start_angle = (self._start_angle + self.arc_extent_deg) % 360

        # Draw static elements
        self._bg_arc = self.canvas.create_arc(
            self._bbox,
            start=self._start_angle,
            extent=self.arc_extent_deg,
            style=tk.ARC,
            outline=Colors.LIGHT_GRAY,
            width=12,
        )

        # Value arc (dynamic)
        self._value_arc = self.canvas.create_arc(
            self._bbox,
            start=self._value_start_angle,
            extent=0,
            style=tk.ARC,
            outline=self.accent,
            width=12,
        )

        # Label and value
        # Position texts to avoid overlap across different radii
        self._label_id = self.canvas.create_text(
            size // 2,
            size // 2 + int(self.radius * 0.62),
            text=self.label,
            fill=Colors.GRAY,
            font=("Helvetica", 14),
        )
        self._value_id = self.canvas.create_text(
            size // 2,
            size // 2,
            text="0",
            fill=self.fg,
            font=("Helvetica", 36, "bold"),
        )
        self._unit_id = self.canvas.create_text(
            size // 2,
            size // 2 + int(self.radius * 0.30),
            text=self.unit,
            fill=Colors.GRAY,
            font=("Helvetica", 14),
        )

    def _clamp(self, value: float) -> float:
        return max(self.min_value, min(self.max_value, value))

    def _value_to_extent(self, value: float) -> float:
        if self.max_value == self.min_value:
            return 0
        ratio = (value - self.min_value) / (self.max_value - self.min_value)
        ratio = max(0.0, min(1.0, ratio))
        # Negative extent draws clockwise from start angle
        return -self.arc_extent_deg * ratio

    def set_target(self, value: float) -> None:
        self._target_value = self._clamp(value)
        if not self._tick_running:
            self._tick_running = True
            self.root.after(16, self._tick)  # ~60fps

    def _tick(self) -> None:
        # Smoothly animate toward target for a refined feel
        delta = self._target_value - self._display_value
        if abs(delta) < 0.1:
            self._display_value = self._target_value
        else:
            self._display_value += delta * 0.2

        extent = self._value_to_extent(self._display_value)
        self.canvas.itemconfig(self._value_arc, extent=extent)

        # Update number display
        if self.unit.lower() == "mph":
            value_text = f"{self._display_value:.0f}"
        elif self.unit == "%":
            value_text = f"{self._display_value:.0f}"
        else:
            value_text = f"{self._display_value:.0f}"
        self.canvas.itemconfig(self._value_id, text=value_text)

        if abs(self._target_value - self._display_value) > 0.05:
            self.root.after(32, self._tick)
        else:
            self._tick_running = False


class ModeIndicator:
    """Inline mode indicator with a pill highlight for the active mode."""

    def __init__(
        self, root: tk.Misc, x: int, y: int, bg: str = "white", fg: str = "black"
    ) -> None:
        self.selected_mode: SpeedMode = "park"
        self.root = root
        self.frame = tk.Frame(root, bg=bg)
        self.frame.place(x=x, y=y)
        self.bg = bg
        self.fg = fg
        self.accent = Colors.BLACK
        self.dim = Colors.GRAY
        self.labels: Dict[SpeedMode, str] = {
            "park": "Park",
            "neutral": "Neutral",
            "chill": "Chill",
            "standard": "Sport",
            "sport": "Sport",
            "insane": "Ludicrous",
        }
        self.active_colors: Dict[SpeedMode, str] = {
            "park": Colors.RED,
            "neutral": Colors.YELLOW,
            "chill": Colors.GREEN,
            "standard": Colors.GREEN,
            "sport": Colors.GREEN,
            "insane": Colors.GREEN,
        }
        self._label_widgets: Dict[SpeedMode, tk.Label] = {}

        for idx, mode in enumerate(SPEED_MODES):
            label = self.labels[mode]
            lbl = tk.Label(
                self.frame,
                text=label,
                bg=self.bg,
                fg=self.dim,
                font=("Helvetica", 16),
                padx=10,
            )
            lbl.grid(row=0, column=idx, padx=6)
            self._label_widgets[mode] = lbl

    def set_mode(self, mode: "SpeedMode") -> None:
        prev_mode = self.selected_mode
        self._label_widgets[mode].config(bg=self.active_colors[mode], fg=self.accent)
        self._label_widgets[prev_mode].config(bg=self.bg, fg=self.dim)
        self.selected_mode = mode


class ScreenUI:
    """
    Clean, minimalist dashboard:
    - Center dial: Speed (mph)
    - Left dial: Power (W)
    - Right dial: Battery (%)
    - Top-right: Mode indicator (N, Chill, Sport, Ludicrous)
    """

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Moonshot Couch")
        try:
            self.root.attributes("-fullscreen", True)
        except Exception:
            pass
        self.root.geometry("800x480")
        self.root.configure(bg="white")

        # Layout constants
        self.bg = "white"
        self.fg = "black"

        # Header
        self.header = tk.Label(
            root,
            text="Moonshot Couch",
            bg=self.bg,
            fg=Colors.BLACK,
            font=("Helvetica", 18, "bold"),
        )
        self.header.place(x=20, y=16)

        # Mode indicator (top-right)
        self.mode = ModeIndicator(root, x=800 - 20 - 520, y=16, bg=self.bg, fg=self.fg)

        # Dials
        self.dial_speed = DialWidget(
            root,
            center=(400, 260),
            radius=130,
            label="Speed",
            unit="mph",
            min_value=0,
            max_value=25,
            accent=Colors.BLACK,
        )

        self.dial_power = DialWidget(
            root,
            center=(160, 280),
            radius=90,
            label="Power",
            unit="W",
            min_value=0,
            max_value=1200,
            accent=Colors.GREEN,
        )

        self.dial_battery = DialWidget(
            root,
            center=(640, 280),
            radius=90,
            label="Battery",
            unit="%",
            min_value=0,
            max_value=100,
            accent=Colors.BLUE,
        )

    def update(
        self, update: ScreenUIUpdate
    ) -> None:
        # Clamp incoming values and update targets
        speed_mph = max(0.0, min(25.0, float(update.speed_mph)))
        power_watts = max(0.0, min(1200.0, float(update.power_watts)))
        battery_pct = max(0.0, min(100.0, float(update.battery_pct)))

        self.dial_speed.set_target(speed_mph)
        self.dial_power.set_target(power_watts)
        self.dial_battery.set_target(battery_pct)
        self.mode.set_mode(update.speed_mode)


if __name__ == "__main__":
    root = tk.Tk()
    ui = ScreenUI(root)

    def demo_tick(v: float = 0.0) -> None:
        ui.update(ScreenUIUpdate(
            speed_mph=v % 25,
            power_watts=(v * 50) % 1200,
            battery_pct=100 - (v % 100),
            speed_mode=SPEED_MODES[int(v) % len(SPEED_MODES)],
        ))
        root.after(100, lambda: demo_tick(v + 1))

    demo_tick()
    root.mainloop()
