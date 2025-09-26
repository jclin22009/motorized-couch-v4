import asyncio
import time
import threading
from typing import TYPE_CHECKING

import Gamepad.Gamepad as Gamepad
import Gamepad.Controllers as Controllers
from detect_motor_controllers import get_motor_controllers

from drive_modes import arcade_drive_ik, get_speed_multiplier
import pygame

if TYPE_CHECKING:
    from app import UIManager

VERTICAL_JOYSTICK_AXIS = 1
HORIZONTAL_JOYSTICK_AXIS = 0
POLL_INTERVAL = 0.1

class Couch:
    def __init__(self, ui_manager: "UIManager"):
        self.ui_manager = ui_manager
        self.speed = 0
        self.left_power = 0
        self.right_power = 0
        self.left_rpm = 0
        self.right_rpm = 0
        self.voltage = 0
        self.temperature = 0
        self.couch_mode = 0 # 0 = park, 1 = neutral, 2 = chill, 3 = speed, 4 = ludicrous 

    def start(self):
        self.stop_event = threading.Event()

        # Use a separate thread for joystick and motor control
        self.control_thread = threading.Thread(target=self.joystick_motor_control)
        self.control_thread.daemon = True  # This will allow the thread to exit when the main program exits
        self.control_thread.start()

        self.update_ui_task = asyncio.create_task(self.update_ui_periodically())

    def stop(self):
        self.stop_event.set()
        self.update_ui_task.cancel()
        self.control_thread.join()

    async def update_ui_periodically(self):
        try:
            while True:
                battery_percentage = self.voltage # TODO: DO actual conversion
                range_ = self.voltage # TODO: DO actual conversion
                wattage = self.left_power + self.right_power # TODO: Is this correct?
                gear = 0 # TODO: Get actual gear
                await self.ui_manager.send({
                    "speed": self.speed,           # mph
                    "battery": battery_percentage, # %
                    "wattage": wattage,             # W
                    "range": range_,          # mi
                    "voltage": self.voltage,  # V
                    "speedMode": self.couch_mode,        # index
                    "gear": gear,             # index
                })
                await asyncio.sleep(0.2)
        except asyncio.CancelledError:
            pass

    def joystick_motor_control(self):
        stop_event = self.stop_event
        # Waits for the joystick to be connected
        while not Gamepad.available() and not stop_event.is_set():
            print("Please connect your gamepad")
            time.sleep(1)
        joystick = Controllers.Joystick()  # Initializes the joystick as a generic gamepad
        print("Gamepad connected")

        #pygame.mixer.init()

        joystick.startBackgroundUpdates()

        # Waits for the motor controllers to be connected
        left_motor, right_motor = get_motor_controllers()

        # Main loop
        try:
            while joystick.isConnected() and not stop_event.is_set():
                joystick_vertical = -joystick.axis('Y')
                joystick_horizontal = joystick.axis('X')
                ik_left, ik_right = arcade_drive_ik(joystick_vertical, joystick_horizontal)
                ik_left *= get_speed_multiplier(self.couch_mode)
                ik_right *= get_speed_multiplier(self.couch_mode)

                try:
                    measurements_left = left_motor.get_measurements()
                    measurements_right = right_motor.get_measurements()

                    if measurements_left and measurements_right:
                        self.left_rpm = measurements_left.rpm
                        self.right_rpm = measurements_right.rpm
                        self.left_power = measurements_left.avg_motor_current * 10
                        self.right_power = measurements_right.avg_motor_current * 10
                        self.voltage = measurements_left.v_in
                        self.temperature = measurements_left.temp_fet if measurements_left.temp_fet > measurements_right.temp_fet else measurements_right.temp_fet
                    else:
                        self.left_rpm = 0
                        self.right_rpm = 0
                except Exception as e:
                    print(f"Error getting motor measurements: {e}")
                    self.left_rpm = 0
                    self.right_rpm = 0

                rpm_to_mph = 8 * 3.14 * 60 / 5280 / 12

                self.speed = (((self.left_rpm + self.right_rpm) / 2) / 15) * rpm_to_mph #Convert ERPM to RPM

                if joystick.isPressed('T1'):
                    self.couch_mode = 0
                    left_motor.set_rpm(0)
                    right_motor.set_rpm(0)
                    print("Motors set to brake state (park)")
                elif joystick.isPressed('T2'):
                    self.couch_mode = 1
                    left_motor.set_current(0) 
                    right_motor.set_current(0)
                    print("Motors set to loose state (neutral)")
                elif joystick.isPressed('T3'):
                    self.couch_mode = 2
                    print("Motors set to brake state (chill)")
                elif joystick.isPressed('T5'):
                    self.couch_mode = 3
                    print("Motors set to brake state (speed)")
                elif joystick.isPressed('T7'):
                    self.couch_mode = 4
                    print("Motors set to brake state (ludicrous)")

                if joystick.isPressed('TRIGGER'):
                    try:
                        pygame.mixer.music.load("horn2.wav")
                        pygame.mixer.music.play()
                        print("Playing sound")
                    except Exception as e:
                        print(f"Failed to play sound: {e}")

                if self.couch_mode > 1:
                    left_motor.set_rpm(ik_left)
                    right_motor.set_rpm(ik_right)

        finally:
            del left_motor
            del right_motor
            joystick.disconnect()


if __name__ == "__main__":
    main = Couch()
    main.start()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        main.stop()
    
