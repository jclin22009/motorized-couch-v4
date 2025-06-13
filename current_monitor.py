import asyncio
import odrive
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque
import time
import numpy as np
import pygame
from odrive.enums import AxisState, ControlMode
import math

# Import conversion functions from main.py
def rad_per_sec_to_mph(rad_per_sec, wheel_circumference_inches=25.12):
    """Convert angular velocity (rad/s) to linear speed (mph)"""
    radius_inches = wheel_circumference_inches / (2 * math.pi)
    linear_velocity_inches_per_sec = rad_per_sec * radius_inches
    mph = linear_velocity_inches_per_sec * 3600 / 63360
    return mph

def mph_to_rad_per_sec(mph, wheel_circumference_inches=25.12):
    """Convert linear speed (mph) to angular velocity (rad/s)"""
    linear_velocity_inches_per_sec = mph * 63360 / 3600
    radius_inches = wheel_circumference_inches / (2 * math.pi)
    rad_per_sec = linear_velocity_inches_per_sec / radius_inches
    return rad_per_sec

class CurrentMonitor:
    def __init__(self, max_points=500):
        self.max_points = max_points
        self.times = deque(maxlen=max_points)
        self.currents = deque(maxlen=max_points)
        self.current_limits = deque(maxlen=max_points)
        
        # Set up the plot
        self.fig, self.ax = plt.subplots(figsize=(12, 8))
        self.line_current, = self.ax.plot([], [], 'b-', label='Motor Current', linewidth=2)
        self.line_limit, = self.ax.plot([], [], 'r--', label='Current Limit', linewidth=2)
        
        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('Current (Amps)')
        self.ax.set_title('ODrive Motor Current vs Time (Live Control)')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        self.start_time = time.time()
        self.odrv0 = None
        self.current_limit_value = 25.0  # Default
        
        # Motor control variables
        self.current_torque = 0.0
        self.max_torque = 0.5
        self.torque_ramp_rate = 2.0
        self.max_safe_velocity = mph_to_rad_per_sec(15.0)
        
    async def find_device(self):
        """Connect to ODrive and configure for torque control"""
        print("Connecting to ODrive...")
        self.odrv0 = await odrive.find_async()
        await self.odrv0.axis0.clear_errors()
        
        # Configure for torque control (same as main.py)
        await self.odrv0.axis0.controller.config.control_mode.write(ControlMode.TORQUE_CONTROL)
        
        # Set torque constant
        motor_kv = 110  # Same as main.py
        torque_constant = 8.23 / motor_kv
        await self.odrv0.axis0.motor.config.torque_constant.write(torque_constant)
        
        # Set velocity limit
        max_speed_rad_s = mph_to_rad_per_sec(15.0)
        await self.odrv0.axis0.controller.config.vel_limit.write(max_speed_rad_s)
        
        await self.odrv0.axis0.requested_state.write(AxisState.CLOSED_LOOP_CONTROL)
        await self.odrv0.axis0.clear_errors()
        
        # Get the current limit
        self.current_limit_value = await self.odrv0.axis0.motor.config.current_lim.read()
        print(f"✓ Connected to ODrive")
        print(f"✓ Motor current limit: {self.current_limit_value:.1f} A")
        print(f"✓ Torque constant: {torque_constant:.4f}")
        print(f"✓ Velocity limit: 15.0 mph ({max_speed_rad_s:.1f} rad/s)")
        
        return self.current_limit_value
    
    async def get_motor_current(self):
        """Get current motor current draw"""
        if self.odrv0 is None:
            return 0.0
        
        try:
            # Try different possible current reading locations
            current = await self.odrv0.axis0.motor.current_control.Iq_measured.read()
            return abs(current)  # Return absolute value
        except AttributeError:
            try:
                # Alternative location
                current = await self.odrv0.axis0.motor.current_control.Iq_setpoint.read()
                return abs(current)
            except AttributeError:
                try:
                    # Another possible location - get DC current
                    current_a = await self.odrv0.axis0.motor.current_control.Id_measured.read()
                    current_b = await self.odrv0.axis0.motor.current_control.Iq_measured.read()
                    return abs(math.sqrt(current_a**2 + current_b**2))
                except AttributeError:
                    return 0.0
    
    async def set_torque(self, torque):
        """Set motor torque"""
        if self.odrv0:
            await self.odrv0.axis0.controller.input_torque.write(torque)
    
    async def get_velocity(self):
        """Get current velocity"""
        if self.odrv0:
            return await self.odrv0.axis0.encoder.vel_estimate.read()
        return 0.0
    
    async def update_data(self):
        """Update the data arrays with new readings"""
        current_time = time.time() - self.start_time
        motor_current = await self.get_motor_current()
        
        self.times.append(current_time)
        self.currents.append(motor_current)
        
        return current_time, motor_current
    
    def animate(self, frame):
        """Animation function for matplotlib"""
        if len(self.times) > 1:
            self.line_current.set_data(list(self.times), list(self.currents))
            
            # Update current limit line
            if len(self.times) > 0:
                self.current_limits.clear()
                self.current_limits.extend([self.current_limit_value] * len(self.times))
                self.line_limit.set_data(list(self.times), list(self.current_limits))
            
            # Auto-scale the plot
            if len(self.times) > 0:
                self.ax.set_xlim(max(0, min(self.times)), max(self.times))
                max_current = max(max(self.currents) if self.currents else 0, self.current_limit_value * 1.1)
                self.ax.set_ylim(0, max_current * 1.1)
        
        return self.line_current, self.line_limit

async def main():
    # Initialize pygame for joystick
    pygame.init()
    pygame.joystick.init()
    
    # Check for joystick
    if pygame.joystick.get_count() == 0:
        print("No joystick found! Please connect a joystick.")
        return
    
    joystick = pygame.joystick.Joystick(0)
    print(f"Using joystick: {joystick.get_name()}")
    
    # Initialize current monitor
    monitor = CurrentMonitor()
    
    # Connect to ODrive
    try:
        current_limit = await monitor.find_device()
        monitor.current_limits = deque([current_limit] * monitor.max_points, maxlen=monitor.max_points)
    except Exception as e:
        print(f"Error connecting to ODrive: {e}")
        print("Make sure ODrive is connected and accessible")
        pygame.quit()
        return
    
    print("\n=== Current Monitor + Joystick Control Started ===")
    print("🎮 Use joystick to control motor torque")
    print("📊 Watch the current graph in real-time")
    print("⚠️  Current limit is set to", current_limit, "A")
    print("🛑 Press Ctrl+C or close plot window to stop")
    print("Wheel circumference: 25.12 inches")
    
    # Set up non-blocking plot
    plt.ion()  # Turn on interactive mode
    plt.show()
    
    dt = 0.05  # 20Hz update rate
    
    try:
        while True:
            # Handle joystick input
            pygame.event.pump()
            axis_value = joystick.get_axis(1)  # Usually vertical axis
            target_torque = axis_value * -monitor.max_torque
            
            # Ramp torque for smoother control
            torque_diff = target_torque - monitor.current_torque
            max_change = monitor.torque_ramp_rate * dt
            
            if abs(torque_diff) > max_change:
                monitor.current_torque += max_change if torque_diff > 0 else -max_change
            else:
                monitor.current_torque = target_torque
            
            # Safety check: monitor velocity
            current_velocity_rad_s = await monitor.get_velocity()
            current_mph = rad_per_sec_to_mph(current_velocity_rad_s)
            
            if abs(current_velocity_rad_s) > monitor.max_safe_velocity:
                print(f"SAFETY: Speed too high ({current_mph:.2f} mph), cutting torque!")
                monitor.current_torque = 0.0
            
            # Set torque
            await monitor.set_torque(monitor.current_torque)
            
            # Update current monitoring data
            current_time, motor_current = await monitor.update_data()
            
            # Update plot
            monitor.animate(None)
            plt.pause(0.01)  # Small pause to allow plot to update
            
            # Print status when actively controlling
            if abs(axis_value) > 0.1:
                print(f"Torque: {monitor.current_torque:.3f} Nm, Speed: {current_mph:.2f} mph, Current: {motor_current:.2f}A")
                
                # Warn if hitting current limit
                if motor_current > current_limit * 0.95:
                    print(f"⚠️  WARNING: Current near limit! ({motor_current:.2f}A / {current_limit:.1f}A)")
            
            # Check if plot window is still open
            if not plt.get_fignums():
                break
                
            await asyncio.sleep(dt)
            
    except KeyboardInterrupt:
        print("\nStopping current monitor...")
    except Exception as e:
        print(f"Error during monitoring: {e}")
    finally:
        # Clean shutdown
        await monitor.set_torque(0.0)
        plt.ioff()
        plt.close('all')
        pygame.quit()
        print("Current monitor stopped.")

if __name__ == "__main__":
    asyncio.run(main()) 