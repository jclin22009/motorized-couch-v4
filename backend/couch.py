import time
import threading

import Gamepad.Gamepad as Gamepad
import Gamepad.Controllers as Controllers
from detect_motor_controllers import get_motor_controllers

from drive_modes import SpeedMode, enhanced_curvature_drive_ik, get_speed_multiplier
from mathutils import SlewRateLimiter

from screen_ui import ScreenUI, ScreenUIUpdate

VERTICAL_JOYSTICK_AXIS = 1
HORIZONTAL_JOYSTICK_AXIS = 0
POLL_INTERVAL = 0.05  # 20Hz polling for more responsive input reading

class Couch:
    def __init__(self, ui_manager: "ScreenUI | None" = None):
        self.ui_manager = ui_manager
        self.speed = 0
        self.left_power = 0
        self.right_power = 0
        self.left_rpm = 0
        self.right_rpm = 0
        self.voltage = 0
        self.temperature = 0
        self.speed_mode: SpeedMode = "park"
        
        # Professional slew rate limiters for smooth velocity ramping
        # Used in competitive robotics and industrial control systems
        self.left_slew_limiter = SlewRateLimiter(
            positive_rate_limit=4.0,  # RPM/sec acceleration limit
            negative_rate_limit=6.0   # RPM/sec deceleration limit (faster stopping)
        )
        self.right_slew_limiter = SlewRateLimiter(
            positive_rate_limit=4.0,
            negative_rate_limit=6.0
        )

    def start(self):
        print("Starting couch")
        self.stop_event = threading.Event()

        # Use a separate thread for joystick and motor control
        self.control_thread = threading.Thread(target=self.joystick_motor_control, daemon=True)
        self.ui_thread = threading.Thread(target=self.update_ui_periodically, daemon=True)
        self.control_thread.start()
        self.ui_thread.start()
        print("Started couch")

    def stop(self):
        print("Stopping couch")
        self.stop_event.set()
        self.control_thread.join()
        print("Stopped control thread")
        self.ui_thread.join()
        print("Stopped UI thread")
        print("Stopped couch")

    def update_ui_periodically(self):
        stop_event = self.stop_event
        while not stop_event.is_set():
            battery_percentage = self.voltage # TODO: DO actual conversion
            wattage = self.left_power + self.right_power
            try:
                if self.ui_manager:
                    self.ui_manager.update(ScreenUIUpdate(
                        speed_mph=self.speed,
                        power_watts=wattage,
                        battery_pct=battery_percentage,
                        speed_mode=self.speed_mode,
                    ))
            except Exception as e:
                print(f"Error sending data to UI: {e}")
            time.sleep(0.2)

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
                # Get raw joystick inputs
                joystick_vertical = -joystick.axis('Y')
                joystick_horizontal = joystick.axis('X')
                
                # Check for quick-turn mode (for tight maneuvers at low speed)
                # You can assign this to a button - for now using a simple speed threshold
                current_speed_magnitude = abs(joystick_vertical)
                quick_turn = current_speed_magnitude < 0.1 and abs(joystick_horizontal) > 0.3
                
                # Use professional curvature drive (speed-dependent turning)
                ik_left, ik_right = enhanced_curvature_drive_ik(
                    joystick_vertical, 
                    joystick_horizontal, 
                    quick_turn
                )
                # Apply speed mode scaling
                ik_left *= get_speed_multiplier(self.speed_mode)
                ik_right *= get_speed_multiplier(self.speed_mode)
                
                # Apply professional slew rate limiting for smooth acceleration/deceleration
                # Convert to RPM (adjust this based on your motor's max RPM)
                MAX_RPM = 1000  # TODO: Replace with your actual motor max RPM
                target_left_rpm = ik_left * MAX_RPM
                target_right_rpm = ik_right * MAX_RPM
                
                # Apply slew rate limiting
                smooth_left_rpm = self.left_slew_limiter.calculate(target_left_rpm)
                smooth_right_rpm = self.right_slew_limiter.calculate(target_right_rpm)
                
                # Convert back to normalized values for the existing code
                ik_left = smooth_left_rpm / MAX_RPM if MAX_RPM > 0 else 0
                ik_right = smooth_right_rpm / MAX_RPM if MAX_RPM > 0 else 0

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

                is_driving = True

                is_neutral = joystick.isPressed("MODEA")
                is_driving = joystick.isPressed("MODEB")
                is_park = not is_driving and not is_neutral

                if is_park:
                    self.speed_mode = "park"
                    left_motor.set_rpm(0)
                    right_motor.set_rpm(0)
                elif is_neutral:
                    self.speed_mode = "neutral"
                    left_motor.set_current(0) 
                    right_motor.set_current(0)
                elif is_driving:
                    if self.speed_mode == "park" or self.speed_mode == "neutral":
                        self.speed_mode = "chill"
                    if joystick.isPressed('T1') or joystick.isPressed('T2'):
                        self.speed_mode = "chill"
                    elif joystick.isPressed('T3') or joystick.isPressed('T4'):
                        self.speed_mode = "standard"
                    elif joystick.isPressed('T5') or joystick.isPressed('T6'):
                        self.speed_mode = "sport"
                    elif joystick.isPressed('T7') or joystick.isPressed('T8'):
                        self.speed_mode = "insane"
                    # Use the slew-rate limited RPM values directly
                    left_motor.set_rpm(smooth_left_rpm)
                    right_motor.set_rpm(smooth_right_rpm)

                if joystick.isPressed('TRIGGER'):
                    # TODO: Horn
                    pass
                
                # Control loop timing
                time.sleep(POLL_INTERVAL)

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
    
