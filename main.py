import asyncio
import odrive
import pygame
import math
from odrive.enums import AxisState, ControlMode

async def find_device():
    odrv0 = await odrive.find_async()
    await odrv0.axis0.clear_errors()

    
    # Configure for torque control
    await odrv0.axis0.controller.config.control_mode.write(ControlMode.TORQUE_CONTROL)
    
    # Set torque constant - using the correct path found from debugging
    motor_kv = 110  # Our motor ratings and lawton
    torque_constant = 8.23 / motor_kv # from odrive documentation
    
    print(f"Setting torque_constant = {torque_constant}")
    await odrv0.axis0.motor.config.torque_constant.write(torque_constant)
    print("✓ Torque constant set successfully")
    
    # Optional: Disable velocity limiter for full torque control
    # WARNING: This removes a safety feature! Enable only if you understand the risks
    # await odrv0.axis0.controller.enable_torque_mode_vel_limit.write(False)
    
    # Set velocity limit for torque mode (safety feature) - 25 mph max
    max_speed_rad_s = mph_to_rad_per_sec(25.0)
    await odrv0.axis0.controller.config.vel_limit.write(max_speed_rad_s)  # rad/s
    print(f"✓ Velocity limit set to 25.0 mph ({max_speed_rad_s:.1f} rad/s)")
    
    await odrv0.axis0.requested_state.write(AxisState.CLOSED_LOOP_CONTROL)
    await odrv0.axis0.clear_errors()
    return odrv0

async def set_torque(torque, device):
    """
    torque: in Nm (Newton-meters)
    """
    await device.axis0.controller.input_torque.write(torque)

async def get_velocity(device):
    """
    Get current velocity for monitoring
    """
    return await device.axis0.encoder.vel_estimate.read()

async def get_current(device):
    """
    Get current draw for monitoring
    """
    return await device.axis0.motor.current_control.Iq_measured.read()

def rad_per_sec_to_mph(rad_per_sec, wheel_circumference_inches=25.12):
    """
    Convert angular velocity (rad/s) to linear speed (mph)
    
    Args:
        rad_per_sec: Angular velocity in radians per second
        wheel_circumference_inches: Wheel circumference in inches (default: 25.12)
    
    Returns:
        Speed in miles per hour (mph)
    """
    # Convert angular velocity to linear velocity (inches per second)
    # Linear velocity = angular_velocity * radius
    # radius = circumference / (2 * pi)
    radius_inches = wheel_circumference_inches / (2 * math.pi)
    linear_velocity_inches_per_sec = rad_per_sec * radius_inches
    
    # Convert inches per second to miles per hour
    # 1 mile = 63,360 inches
    # 1 hour = 3600 seconds
    mph = linear_velocity_inches_per_sec * 3600 / 63360
    
    return mph

def mph_to_rad_per_sec(mph, wheel_circumference_inches=25.12):
    """
    Convert linear speed (mph) to angular velocity (rad/s)
    
    Args:
        mph: Speed in miles per hour
        wheel_circumference_inches: Wheel circumference in inches (default: 25.12)
    
    Returns:
        Angular velocity in radians per second
    """
    # Convert mph to inches per second
    # 1 mile = 63,360 inches, 1 hour = 3600 seconds
    linear_velocity_inches_per_sec = mph * 63360 / 3600
    
    # Convert linear velocity to angular velocity
    # radius = circumference / (2 * pi)
    # angular_velocity = linear_velocity / radius
    radius_inches = wheel_circumference_inches / (2 * math.pi)
    rad_per_sec = linear_velocity_inches_per_sec / radius_inches
    
    return rad_per_sec

async def main():
    pygame.init()
    pygame.joystick.init()
    
    odrv0 = await find_device()
    if odrv0 is None:
        print("Failed to configure ODrive properly")
        return
        
    joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
    
    if not joystick:
        print("No joystick found!")
        return
    
    print(f"Using joystick: {joystick.get_name()}")
    print("TORQUE CONTROL MODE - Be careful!")
    print("Wheel circumference: 25.12 inches")
    
    # Torque control parameters - MUCH LESS AGGRESSIVE
    max_torque = 2.0  # Maximum torque in Nm - increased from 0.5 to 2.0!
    torque_ramp_rate = 10.0  # Nm/s - increased from 2.0 to 10.0 for faster response!
    current_torque = 0.0
    dt = 0.05  # 20Hz update rate
    
    # Safety parameters - increased speed limit
    max_safe_mph = 25.0  # Increased from 15 to 25 mph
    max_safe_velocity = mph_to_rad_per_sec(max_safe_mph)
    print(f"Maximum safe speed: {max_safe_mph} mph ({max_safe_velocity:.1f} rad/s)")
    
    try:
        while True:
            pygame.event.pump()
            axis_value = joystick.get_axis(1)  # Usually vertical axis
            target_torque = axis_value * -max_torque
            
            # Check if we're hitting max torque limit
            if abs(axis_value) > 0.95:  # 95% of full joystick range
                print(f"LIMIT HIT: MAXIMUM TORQUE LIMIT - Joystick at {abs(axis_value)*100:.1f}%, torque capped at {max_torque} Nm")
            
            # Ramp torque for smoother control
            torque_diff = target_torque - current_torque
            max_change = torque_ramp_rate * dt
            
            if abs(torque_diff) > max_change:
                current_torque += max_change if torque_diff > 0 else -max_change
                print(f"LIMIT HIT: Torque ramp rate limited to {torque_ramp_rate} Nm/s (current: {current_torque:.3f} Nm, target: {target_torque:.3f} Nm)")
            else:
                current_torque = target_torque
            
            # Safety check: monitor velocity and current
            current_velocity_rad_s = await get_velocity(odrv0)
            current_mph = rad_per_sec_to_mph(current_velocity_rad_s)
            current_amps = await get_current(odrv0)
            
            if abs(current_velocity_rad_s) > max_safe_velocity:
                print(f"LIMIT HIT: VELOCITY SAFETY LIMIT - Speed too high ({current_mph:.2f} mph > {max_safe_mph} mph), cutting torque!")
                current_torque = 0.0
            
            await set_torque(current_torque, odrv0)
            
            # Optional: Print status
            if abs(axis_value) > 0.1:  # Only print when actively controlling
                print(f"Torque: {current_torque:.3f} Nm, Speed: {current_mph:.2f} mph ({current_velocity_rad_s:.2f} rad/s), Current: {current_amps:.2f} A")
            
            await asyncio.sleep(dt)
    except KeyboardInterrupt:
        await set_torque(0, odrv0)
        pygame.quit()

asyncio.run(main())