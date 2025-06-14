import math
import time
import asyncio
from odrive.enums import AxisState
import odrive

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
    # Set torque constant - using the correct path found from debugging
    motor_kv = 110  # Our motor ratings and lawton
    torque_constant = 8.23 / motor_kv # from odrive documentation

    odrv0 = await odrive.find_async()
    print("Starting test_motor_temp.py")
    print(f"Setting torque_constant = {torque_constant}")
    await odrv0.axis0.motor.config.torque_constant.write(torque_constant)
    print("✓ Torque constant set successfully")

    
    # Set velocity limit for torque mode (safety feature) - 25 mph max
    max_speed_rad_s = mph_to_rad_per_sec(25.0)
    await odrv0.axis0.controller.config.vel_limit.write(max_speed_rad_s)  # rad/s
    print(f"✓ Velocity limit set to 25.0 mph ({max_speed_rad_s:.1f} rad/s)")

    # Configure current limit controls
    await odrv0.axis0.motor.config.current_lim_margin.write(10)
    await odrv0.axis0.motor.config.requested_current_range.write(25)
    await odrv0.axis0.motor.config.current_lim.write(25)

    
    await odrv0.axis0.requested_state.write(AxisState.CLOSED_LOOP_CONTROL)
    print(f"ODrive found: {odrv0}")

    print("Setting axis0 to closed loop control")
    print(f"Current state: {odrv0.axis0.current_state}")

    p0 = odrv0.axis0.controller.input_pos
    t0 = time.monotonic()
    while odrv0.axis0.current_state == AxisState.CLOSED_LOOP_CONTROL:
        setpoint = p0 + 4.0 * math.sin((time.monotonic() - t0) * 2) # [rev]
        print(f"goto {setpoint}")
        odrv0.axis0.controller.input_pos = setpoint
        await asyncio.sleep(0.01)

if __name__ == "__main__":
    asyncio.run(main())