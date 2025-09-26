import tkinter as tk
import os
os.environ['DISPLAY'] = ':0'

class ScreenUI:
    def __init__(self, root):
        self.root = root
        root.attributes('-fullscreen', True)
        self.root.title("Screen UI")
        self.root.geometry("800x480")
        self.root.configure(bg='white')  # Set the background color of the window to white
        
        # Vertical line in the center
        self.center_line = tk.Canvas(root, width=4, height=480, bg='black', highlightthickness=0, bd=0)
        self.center_line.place(x=398, y=0)
        
        # Large text box in the top right half with the text "69"
        self.text_box = tk.Text(root, wrap=tk.WORD, font=('Helvetica', 69), bg='white', fg='black', bd=0, highlightthickness=0)
        self.text_box.place(x=0, y=30, width=398, height=100)
        self.text_box.tag_configure("center", justify='center')
        self.text_box.insert(tk.END, "69\n", "center")      

        #Add four text boxes at the top of the screen
        labels_text = ["P/N", "Chill", "Speed", "Ludicrous"]
        self.labels_container = [[] for _ in range(len(labels_text))]
        for i, text in enumerate(labels_text):
            self.labels_container[i] = tk.Text(root, wrap=tk.WORD, font=('Helvetica', 18), bg='white', fg='black', bd=0, highlightthickness=0)
            self.labels_container[i].tag_configure("center", justify='center')
            self.labels_container[i].insert(tk.END, text, "center")
            self.labels_container[i].place(x= i*96 + 4, y=10, width=96, height=20)                
        
        # Small text "MPH" under "69"
        self.mph_label = tk.Label(root, text="MPH", font=('Helvetica', 20), bg='white', fg='black')
        self.mph_label.place(x=0, y=140)  # Adjust x and y to position correctly under "69"
        root.update_idletasks()
        width = self.mph_label.winfo_width()    
        self.mph_label.place(x=200 - (width / 2), y=120)

        # Left side lines
        self.left_power_border = tk.Canvas(root, width=4, height=200, bg='lightgrey', highlightthickness=0, bd=0)
        self.left_power_border.place(x=20, y=140)
        self.left_power_green = tk.Canvas(root, width=4, height=20, bg='green', highlightthickness=0, bd=0)
        self.left_power_green.place(x=20, y=180)
        
        self.right_power_border = tk.Canvas(root, width=4, height=200, bg='lightgrey', highlightthickness=0, bd=0)
        self.right_power_border.place(x=374, y=140)
        self.right_power_green = tk.Canvas(root, width=4, height=20, bg='green', highlightthickness=0, bd=0)
        self.right_power_green.place(x=374, y=180)
        
        # Small text "Battery: 100%" at the bottom of the left half, centered
        self.battery_label = tk.Label(root, text="Battery: 100%", font=('Helvetica', 20), bg='white', fg='black')
        self.battery_label.place(x=100, y=440)  # Adjust x and y to center it in the bottom left half

        # Call the update function every 200 milliseconds (5 times per second)
        # self.update_ui()

        #Debug info
        self.debug_label = tk.Label(root, text="Debug info", font=('Helvetica', 20), bg='white', fg='black')
        self.debug_label.place(x=400, y=0)
        self.debug_info = tk.Label(root, text="Debug info", font=('Helvetica', 20), bg='white', fg='black')
        self.debug_info.place(x=400, y=40)

    def update(self, speed, battery, left_power, right_power, debug_info, drive_mode): 
        # Generate random values for demonstration
        self.text_box.delete("1.0", tk.END)
        self.text_box.insert(tk.END, str(speed) + "\n", "center")

        self.left_power_green.place(height=left_power, y = 260 - left_power) # fixes the top, changes the bottom
        self.right_power_green.place(height=right_power, y = 260 - right_power)

        self.battery_label.config(text="Battery: " + str(battery) + " %")

        drive_mode = drive_mode - 1
        if drive_mode < 0:
            drive_mode = 0

        for i in range(len(self.labels_container)):
            self.labels_container[i].config(fg='grey', font=('Helvetica', 18, 'normal'))

        self.labels_container[drive_mode].config(fg='black', font=('Helvetica', 18, 'bold'))

        self.debug_info.config(text=debug_info)

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenUI(root)
    root.mainloop()
