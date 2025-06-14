import odrive

from odrive.enums import ControlMode, AxisState
from odrive.utils import dump_errors

import asyncio
import time

async def main():
    odrv0 = await odrive.find_async()
    await odrv0.axis0.clear_errors()
    
    await odrv0.axis0.controller.config.control_mode.write(ControlMode.TORQUE_CONTROL)

    # Approximately 8.23 / Kv where Kv is in the units [rpm / V]
    torque_constant = 8.23 / 150
    await odrv0.axis0.motor.config.torque_constant.write(torque_constant)
    print("✓ Torque constant set successfully")

    await odrv0.axis0.requested_state.write(AxisState.CLOSED_LOOP_CONTROL)

    await asyncio.sleep(1)

    try:
        for _ in range(2):
            await odrv0.axis0.controller.input_torque.write(0.18)
            print("✓ Torque set successfully")

            start_time = time.monotonic()
            while time.monotonic() - start_time < 1.5:
                current_amps = await odrv0.axis0.motor.current_control.Iq_measured.read()
                velocity = await odrv0.axis0.encoder.vel_estimate.read()
                print(f"Current: {current_amps} A, Velocity: {velocity} rpm")
                await dump_errors(odrv0)
                await asyncio.sleep(0.1)

            print("Stop")

            await odrv0.axis0.controller.input_torque.write(0)

            await asyncio.sleep(2)
    finally:
        await odrv0.axis0.controller.input_torque.write(0)

if __name__ == "__main__":
    asyncio.run(main())
