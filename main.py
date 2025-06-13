import asyncio
import odrive
import pygame
from odrive.enums import AxisState

async def find_device():
    odrv0 = await odrive.find_async()
    await odrv0.axis0.requested_state.write(AxisState.CLOSED_LOOP_CONTROL)
    await odrv0.axis0.clear_errors()
    return odrv0

async def set_speed(speed, device):
    """
    speed: in rad/s
    """
    await device.axis0.controller.input_vel.write(speed)

async def main():
    pygame.init()
    pygame.joystick.init()
    
    odrv0 = await find_device()
    joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
    
    if not joystick:
        print("No joystick found!")
        return
    
    print(f"Using joystick: {joystick.get_name()}")
    
    try:
        while True:
            pygame.event.pump()
            axis_value = joystick.get_axis(1)  # Usually vertical axis
            speed = axis_value * -20  
            await set_speed(speed, odrv0)
            await asyncio.sleep(0.05)  # 20Hz update rate
    except KeyboardInterrupt:
        await set_speed(0, odrv0)
        pygame.quit()

asyncio.run(main())