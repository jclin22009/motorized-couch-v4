from typing import Tuple
import mathutils

SPEED_MODES = {
    0: 0,
    1: 0.25,
    2: 0.5,
    3: 0.75,
    4: 1
}

def curvture_drive_ik(speed: float, rotation: float) -> Tuple[float, float]:
    """Curvature drive inverse kinematics for a differential drive platform.

    Args:
      speed: The speed along the X axis [-1.0..1.0]. Forward is positive.
      rotation: The normalized curvature [-1.0..1.0]. Counterclockwise is positive.

    Returns:
      Wheel speeds [-1.0..1.0].
    """
    speed, rotation = mathutils.scale_and_deadzone_inputs(speed, rotation, square_rotation=False)
    left_speed = speed + abs(speed) * rotation
    right_speed = speed - abs(speed) * rotation
    return mathutils.desaturate_wheel_speeds(left_speed, right_speed)


def arcade_drive_ik(speed: float, rotation: float) -> Tuple[float, float]:
    """Arcade drive inverse kinematics for a differential drive platform.

    Args:
        speed: The speed along the X axis [-1.0..1.0]. Forward is positive.
        rotation: The normalized curvature [-1.0..1.0]. Counterclockwise is positive.

    Returns:
        Wheel speeds [-1.0..1.0].
    """
    speed, rotation = mathutils.scale_and_deadzone_inputs(speed, rotation)
    left_speed = speed + rotation
    right_speed = speed - rotation
    return mathutils.desaturate_wheel_speeds(left_speed, right_speed)


def get_speed_multiplier(speed_mode: int) -> float:
    return SPEED_MODES[speed_mode]
