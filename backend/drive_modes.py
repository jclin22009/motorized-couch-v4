from typing import Tuple, Literal, Dict, List
import mathutils

SpeedMode = Literal["park", "neutral", "chill", "standard", "sport", "insane"]

SPEED_MODES: List[SpeedMode] = ["park", "neutral", "chill", "standard", "sport", "insane"]

SPEED_MODES_TO_MULTIPLIER: Dict[SpeedMode, float] = {
    "park": 0,
    "neutral": 0,
    "chill": 0.25,
    "standard": 0.5,
    "sport": 0.75,
    "insane": 1,
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


def get_speed_multiplier(speed_mode: SpeedMode) -> float:
    return SPEED_MODES_TO_MULTIPLIER[speed_mode]
