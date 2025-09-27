import tkinter as tk
from couch import Couch
from screen_ui import ScreenUI
import os
os.environ['DISPLAY'] = ':0'


def main():
    root = tk.Tk()
    ui = ScreenUI(root)
    couch = Couch(ui)
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
