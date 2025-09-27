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


def arcade_drive_ik(speed: float, rotation: float, rotation_sensitivity: float = 1) -> Tuple[float, float]:
    """Arcade drive inverse kinematics for a differential drive platform.

    Args:
        speed: The speed along the X axis [-1.0..1.0]. Forward is positive.
        rotation: The normalized curvature [-1.0..1.0]. Counterclockwise is positive.
        rotation_sensitivity: Multiplier for rotation input to reduce turning sensitivity [0.0..1.0].
                             Lower values = gentler turning. Default 0.7 makes turning 30% less aggressive.

    Returns:
        Wheel speeds [-1.0..1.0].
    """
    speed, rotation = mathutils.scale_and_deadzone_inputs(speed, rotation)
    # Scale down rotation to make turning less aggressive
    rotation *= rotation_sensitivity
    left_speed = speed + rotation
    right_speed = speed - rotation
    return mathutils.desaturate_wheel_speeds(left_speed, right_speed)


def get_speed_multiplier(speed_mode: SpeedMode) -> float:
    return SPEED_MODES_TO_MULTIPLIER[speed_mode]


def enhanced_curvature_drive_ik(speed: float, rotation: float, quick_turn: bool = False) -> Tuple[float, float]:
    """
    Enhanced curvature drive with professional-grade control features.
    Based on WPILib implementation used in competitive robotics.

    Args:
        speed: Forward/backward speed [-1.0..1.0]. Forward is positive.
        rotation: Turn rate [-1.0..1.0]. Counterclockwise is positive.
        quick_turn: If true, overrides speed-dependent turning for tight maneuvers.

    Returns:
        Wheel speeds [-1.0..1.0] (left, right).
    """
    speed, rotation = mathutils.scale_and_deadzone_inputs(speed, rotation, square_rotation=False)
    
    if quick_turn:
        # Quick turn mode - for stationary or slow-speed tight turns
        left_speed = rotation
        right_speed = -rotation
    else:
        # Speed-dependent curvature turning (the key improvement!)
        # At high speeds, turning becomes less aggressive automatically
        angular_power = abs(speed) * rotation
        
        if speed > 0:
            # Moving forward
            left_speed = speed + angular_power
            right_speed = speed - angular_power
        elif speed < 0:
            # Moving backward
            left_speed = speed - angular_power
            right_speed = speed + angular_power
        else:
            # Stationary - allow rotation in place
            left_speed = rotation
            right_speed = -rotation
    
    return mathutils.desaturate_wheel_speeds(left_speed, right_speed)
