"""Surfer physics and controls."""

import numpy as np
from dataclasses import dataclass
from typing import Tuple


@dataclass
class SurferState:
    """State of the surfer."""
    # Position
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0  # Height above water

    # Velocity
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0

    # Board orientation (Euler angles)
    roll: float = 0.0
    pitch: float = 0.0
    yaw: float = 0.0

    # Angular velocity
    roll_rate: float = 0.0
    pitch_rate: float = 0.0
    yaw_rate: float = 0.0

    # State flags
    is_swimming: bool = True
    is_duck_diving: bool = False
    is_on_board: bool = True
    is_surfing: bool = False
    has_wiped_out: bool = False


class Surfer:
    """Surfer physics simulation."""

    def __init__(
        self,
        mass: float = 75.0,
        swim_speed: float = 1.5,
        duck_dive_depth: float = 1.0,
        board_length: float = 2.0,
        board_width: float = 0.5,
        board_mass: float = 3.0
    ):
        """
        Initialize surfer.

        Args:
            mass: Surfer mass in kg
            swim_speed: Maximum swim speed in m/s
            duck_dive_depth: Depth when duck diving in meters
            board_length: Surfboard length in meters
            board_width: Surfboard width in meters
            board_mass: Surfboard mass in kg
        """
        self.mass = mass
        self.swim_speed = swim_speed
        self.duck_dive_depth = duck_dive_depth
        self.board_length = board_length
        self.board_width = board_width
        self.board_mass = board_mass

        self.state = SurferState()

    def reset(self, position: Tuple[float, float]):
        """Reset surfer to starting position."""
        self.state = SurferState(
            x=position[0],
            y=position[1],
            z=0.0,
            is_swimming=True,
            is_on_board=True
        )

    def apply_swimming_action(
        self,
        swim_direction: float,
        swim_power: float,
        duck_dive: bool,
        dt: float
    ):
        """
        Apply swimming controls.

        Args:
            swim_direction: Direction to swim (-1 to 1, relative to current heading)
            swim_power: Swimming power (0 to 1)
            duck_dive: Whether to duck dive
            dt: Time step
        """
        if not self.state.is_swimming:
            return

        # Update duck dive state
        self.state.is_duck_diving = duck_dive

        # Swimming velocity
        speed = swim_power * self.swim_speed

        # Direction (yaw controls swim direction)
        self.state.yaw += swim_direction * dt * 2.0  # Turn rate

        # Update velocity
        self.state.vx = speed * np.cos(self.state.yaw)
        self.state.vy = speed * np.sin(self.state.yaw)

        # Duck dive depth control
        if duck_dive:
            self.state.vz = -1.0  # Dive down
        else:
            # Buoyancy brings back to surface
            if self.state.z < 0:
                self.state.vz = 0.5
            else:
                self.state.vz = 0.0

    def apply_board_control(
        self,
        roll_input: float,
        pitch_input: float,
        yaw_input: float,
        paddle_power: float,
        dt: float
    ):
        """
        Apply board control for wave catching.

        Args:
            roll_input: Roll control (-1 to 1)
            pitch_input: Pitch control (-1 to 1)
            yaw_input: Yaw control (-1 to 1)
            paddle_power: Paddling power (0 to 1)
            dt: Time step
        """
        # Board rotation rates
        roll_rate = 2.0  # rad/s
        pitch_rate = 1.5
        yaw_rate = 1.0

        # Apply controls
        self.state.roll_rate = roll_input * roll_rate
        self.state.pitch_rate = pitch_input * pitch_rate
        self.state.yaw_rate = yaw_input * yaw_rate

        # Update orientation
        self.state.roll += self.state.roll_rate * dt
        self.state.pitch += self.state.pitch_rate * dt
        self.state.yaw += self.state.yaw_rate * dt

        # Limit roll and pitch
        self.state.roll = np.clip(self.state.roll, -np.pi/3, np.pi/3)
        self.state.pitch = np.clip(self.state.pitch, -np.pi/4, np.pi/4)

        # Paddling adds forward velocity
        if paddle_power > 0:
            paddle_speed = paddle_power * 3.0  # m/s
            self.state.vx += np.cos(self.state.yaw) * paddle_speed * dt
            self.state.vy += np.sin(self.state.yaw) * paddle_speed * dt

    def apply_surfing_control(
        self,
        lean: float,
        turn: float,
        dt: float
    ):
        """
        Apply surfing controls while riding a wave.

        Args:
            lean: Lean control (-1 to 1) for balance
            turn: Turn control (-1 to 1) for direction
            dt: Time step
        """
        if not self.state.is_surfing:
            return

        # Lean affects roll
        target_roll = lean * np.pi / 6  # Max 30 degrees
        self.state.roll += (target_roll - self.state.roll) * dt * 3.0

        # Turn affects yaw
        self.state.yaw += turn * dt * 2.0

    def update_physics(
        self,
        wave_height: float,
        wave_velocity: Tuple[float, float],
        water_depth: float,
        dt: float
    ):
        """
        Update physics based on wave interaction.

        Args:
            wave_height: Current wave height at surfer position
            wave_velocity: (vx, vy) wave-induced velocity
            water_depth: Water depth at current position
            dt: Time step
        """
        # Update position
        self.state.x += self.state.vx * dt
        self.state.y += self.state.vy * dt
        self.state.z += self.state.vz * dt

        # Wave influence
        if self.state.is_swimming:
            # Waves push swimmer
            self.state.vx += wave_velocity[0] * dt * 0.3
            self.state.vy += wave_velocity[1] * dt * 0.3

            # Wave height affects vertical position
            self.state.z = wave_height

        elif self.state.is_surfing:
            # Riding the wave
            self.state.z = wave_height + 0.2  # Slightly above wave

            # Wave propels surfer
            self.state.vx = wave_velocity[0] * 1.5
            self.state.vy = wave_velocity[1] * 1.5

        # Gravity
        self.state.vz -= 9.81 * dt

        # Water surface constraint
        if self.state.z < 0 and not self.state.is_duck_diving:
            self.state.z = 0
            self.state.vz = 0

        # Apply drag
        drag = 0.95
        self.state.vx *= drag
        self.state.vy *= drag
        self.state.vz *= drag

        # Angular damping
        self.state.roll_rate *= 0.9
        self.state.pitch_rate *= 0.9
        self.state.yaw_rate *= 0.9

    def check_wipeout(self, wave_height: float) -> bool:
        """
        Check if surfer has wiped out.

        Args:
            wave_height: Current wave height

        Returns:
            True if wiped out
        """
        if self.state.is_surfing:
            # Excessive roll or pitch causes wipeout
            if abs(self.state.roll) > np.pi / 3 or abs(self.state.pitch) > np.pi / 4:
                self.state.has_wiped_out = True
                self.state.is_surfing = False
                self.state.is_swimming = True
                return True

            # Falling off wave
            if self.state.z < wave_height - 0.5:
                self.state.has_wiped_out = True
                self.state.is_surfing = False
                self.state.is_swimming = True
                return True

        return False

    def try_catch_wave(
        self,
        wave_height: float,
        wave_direction: float,
        wave_speed: float
    ) -> bool:
        """
        Attempt to catch a wave.

        Args:
            wave_height: Wave height
            wave_direction: Wave direction in radians
            wave_speed: Wave speed in m/s

        Returns:
            True if wave caught successfully
        """
        if self.state.is_surfing or not self.state.is_swimming:
            return False

        # Check if board orientation matches wave
        direction_diff = abs(wave_direction - self.state.yaw)
        if direction_diff > np.pi:
            direction_diff = 2 * np.pi - direction_diff

        # Need to be aligned with wave
        if direction_diff > np.pi / 6:  # 30 degrees
            return False

        # Need correct board angle
        if abs(self.state.pitch) > np.pi / 12:  # 15 degrees
            return False

        # Need to be moving with wave
        surfer_speed = np.sqrt(self.state.vx**2 + self.state.vy**2)
        if surfer_speed < wave_speed * 0.7:
            return False

        # Success!
        self.state.is_surfing = True
        self.state.is_swimming = False
        return True

    def get_observation(self) -> np.ndarray:
        """
        Get surfer state as observation vector.

        Returns:
            Observation array
        """
        return np.array([
            self.state.x,
            self.state.y,
            self.state.z,
            self.state.vx,
            self.state.vy,
            self.state.vz,
            self.state.roll,
            self.state.pitch,
            self.state.yaw,
            self.state.roll_rate,
            self.state.pitch_rate,
            self.state.yaw_rate,
            float(self.state.is_swimming),
            float(self.state.is_duck_diving),
            float(self.state.is_surfing),
        ], dtype=np.float32)
