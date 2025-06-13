import asyncio
import odrive
from odrive.enums import AxisState

async def find_device():
    odrv0 = await odrive.find_async()
    await odrv0.axis0.requested_state.write(AxisState.CLOSED_LOOP_CONTROL)
    return odrv0

async def set_speed(speed, device):
    await device.axis0.controller.input_vel.write(speed)

async def main():
    odrv0 = await find_device()
    await set_speed(0, odrv0)

asyncio.run(main())