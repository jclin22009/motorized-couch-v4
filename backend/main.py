import tkinter as tk
from couch import Couch
from screen_ui import ScreenUI

class UIManager:
    def __init__(self, root):
        self.screen_ui = ScreenUI(root)

    def send(self, data: dict):
        self.screen_ui.update(
            speed=data["speed"],
            battery=data["battery"],
            left_power=0, # TODO: Fill in
            right_power=0, # TODO: Fill in,
            debug_info="", # TODO: Fill in
            drive_mode=data["speedMode"]
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