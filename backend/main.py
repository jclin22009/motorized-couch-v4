import tkinter as tk
from couch import Couch
from screen_ui_v2 import ScreenUIv2


class UIManager:
    def __init__(self, root: tk.Tk) -> None:
        self.screen_ui = ScreenUIv2(root)

    def _map_mode_index(self, couch_mode: int) -> int:
        """Map Couch mode (0=park,1=neutral,2=chill,3=speed,4=ludicrous) to UIv2 index (0=N,1=Chill,2=Sport,3=Ludicrous)."""
        try:
            mode = int(couch_mode)
        except Exception:
            return 0
        if mode <= 1:
            return 0  # Park/Neutral -> N
        if mode == 2:
            return 1  # Chill
        if mode == 3:
            return 2  # Sport (aka Speed)
        return 3  # Ludicrous and any higher value

    def send(self, data: dict) -> None:
        speed_mph = float(data.get("speed", 0.0))
        power_watts = float(data.get("wattage", 0.0))
        battery_pct = float(data.get("battery", 0.0))
        mode_index = self._map_mode_index(data.get("speedMode", 0))

        self.screen_ui.update_ui(
            speed_mph=speed_mph,
            power_watts=power_watts,
            battery_pct=battery_pct,
            mode_index=mode_index,
        )


def main():
    root = tk.Tk()
    ui_manager = UIManager(root)
    couch = Couch(ui_manager)
    couch.start()
    print("Running main loop")
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    print("Main loop ended")
    couch.stop()


if __name__ == "__main__":
    main()
