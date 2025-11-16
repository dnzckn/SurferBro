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
    is_being_carried: bool = False  # Being carried by wave (before standing)
    is_surfing: bool = False
    is_whitewash_carry: bool = False  # Being carried by whitewash after crash
    has_wiped_out: bool = False

    # Duck dive timer (can't move while duck diving!)
    duck_dive_timer: float = 0.0
    duck_dive_duration: float = 3.0  # 3 seconds underwater

    # Wave carrying timer (must be carried before standing)
    wave_carry_timer: float = 0.0
    required_carry_duration: float = 1.0  # Required duration (depends on wave size)

    # Current wave being surfed (for surfing state)
    surfing_wave: object = None  # Wave object reference


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
            yaw=np.pi / 2,  # Face NORTH (+Y direction toward waves)
            is_swimming=True,
            is_on_board=True
        )

    def apply_rotation(self, rotate_action: float, dt: float):
        """
        Apply rotation in 5° increments.

        Args:
            rotate_action: Rotation input (-1 to 1)
            dt: Time step
        """
        # Deadzone to prevent unintentional rotation
        if abs(rotate_action) > 0.3:
            # Rotation direction
            direction = 1 if rotate_action > 0 else -1

            # Apply 6.5° rotation increment (30% faster)
            self.state.yaw += direction * np.radians(6.5) * dt * 10.0  # Scale by dt for smooth rotation

            # Normalize yaw to [-π, π] (equivalent to 0-360°)
            while self.state.yaw > np.pi:
                self.state.yaw -= 2 * np.pi
            while self.state.yaw < -np.pi:
                self.state.yaw += 2 * np.pi

    def apply_swimming_action_2d(
        self,
        swim_x: float,
        swim_y: float,
        duck_dive_trigger: bool,
        dt: float
    ):
        """
        Apply 2D swimming controls with independent X/Y movement.

        IMPORTANT: Can't swim and duck dive at same time!
        Duck dive lasts 3 seconds and prevents movement.

        NEW: Can duck dive while in whitewash_carry to escape!

        Args:
            swim_x: Horizontal swim input (-1 to 1, left/right)
            swim_y: Vertical swim input (-1 to 1, back/forward)
            duck_dive_trigger: Trigger to START a duck dive
            dt: Time step
        """
        # Special case: Duck dive to escape whitewash carry!
        if self.state.is_whitewash_carry and duck_dive_trigger:
            self.state.is_whitewash_carry = False
            self.state.is_swimming = True
            self.state.is_duck_diving = True
            self.state.duck_dive_timer = self.state.duck_dive_duration
            self.state.has_wiped_out = False  # Reset wipeout flag
            return

        if not self.state.is_swimming:
            return

        # Update duck dive timer
        if self.state.duck_dive_timer > 0:
            self.state.duck_dive_timer -= dt
            self.state.is_duck_diving = True
        else:
            self.state.is_duck_diving = False

        # Trigger new duck dive (only if not already diving)
        if duck_dive_trigger and self.state.duck_dive_timer <= 0:
            self.state.duck_dive_timer = self.state.duck_dive_duration
            self.state.is_duck_diving = True

        # DUCK DIVING: Can't swim! Stay underwater, no horizontal movement
        if self.state.is_duck_diving:
            # Apply strong drag to slow down
            self.state.vx *= 0.5
            self.state.vy *= 0.5

            # Dive underwater
            target_depth = -self.duck_dive_depth
            if self.state.z > target_depth:
                self.state.vz = -2.0  # Dive down fast
            else:
                self.state.vz = 0.0  # Stay at depth

        # SWIMMING: Can move in 2D!
        else:
            # Calculate swim direction from inputs
            # swim_x: -1 = left, +1 = right (relative to surfer's orientation)
            # swim_y: -1 = back, +1 = forward (relative to surfer's orientation)

            # Convert to world coordinates based on surfer's yaw
            forward_x = np.cos(self.state.yaw)
            forward_y = np.sin(self.state.yaw)
            right_x = -np.sin(self.state.yaw)
            right_y = np.cos(self.state.yaw)

            # Combine movements
            swim_power = np.sqrt(swim_x**2 + swim_y**2)
            swim_power = min(swim_power, 1.0)  # Clamp to max speed

            # Calculate velocity
            speed = swim_power * self.swim_speed

            # Apply movement
            self.state.vx = speed * (forward_x * swim_y + right_x * swim_x)
            self.state.vy = speed * (forward_y * swim_y + right_y * swim_x)

            # Buoyancy brings back to surface
            if self.state.z < 0:
                self.state.vz = 1.0  # Surface quickly
            else:
                self.state.vz = 0.0

    def apply_swimming_action(
        self,
        swim_direction: float,
        swim_power: float,
        duck_dive_trigger: bool,
        dt: float
    ):
        """
        Apply swimming controls (LEGACY - kept for compatibility).

        IMPORTANT: Can't swim and duck dive at same time!
        Duck dive lasts 3 seconds and prevents movement.

        NEW: Can duck dive while in whitewash_carry to escape!

        Args:
            swim_direction: Direction to swim (-1 to 1, relative to current heading)
            swim_power: Swimming power (0 to 1)
            duck_dive_trigger: Trigger to START a duck dive
            dt: Time step
        """
        # Special case: Duck dive to escape whitewash carry!
        if self.state.is_whitewash_carry and duck_dive_trigger:
            self.state.is_whitewash_carry = False
            self.state.is_swimming = True
            self.state.is_duck_diving = True
            self.state.duck_dive_timer = self.state.duck_dive_duration
            self.state.has_wiped_out = False  # Reset wipeout flag
            return

        if not self.state.is_swimming:
            return

        # Update duck dive timer
        if self.state.duck_dive_timer > 0:
            self.state.duck_dive_timer -= dt
            self.state.is_duck_diving = True
        else:
            self.state.is_duck_diving = False

        # Trigger new duck dive (only if not already diving)
        if duck_dive_trigger and self.state.duck_dive_timer <= 0:
            self.state.duck_dive_timer = self.state.duck_dive_duration
            self.state.is_duck_diving = True

        # DUCK DIVING: Can't swim! Stay underwater, no horizontal movement
        if self.state.is_duck_diving:
            # Apply strong drag to slow down
            self.state.vx *= 0.5
            self.state.vy *= 0.5

            # Dive underwater
            target_depth = -self.duck_dive_depth
            if self.state.z > target_depth:
                self.state.vz = -2.0  # Dive down fast
            else:
                self.state.vz = 0.0  # Stay at depth

        # SWIMMING: Can move, but NOT if duck diving!
        else:
            # Swimming velocity
            speed = swim_power * self.swim_speed

            # Direction (yaw controls swim direction)
            self.state.yaw += swim_direction * dt * 2.0  # Turn rate

            # Update velocity
            self.state.vx = speed * np.cos(self.state.yaw)
            self.state.vy = speed * np.sin(self.state.yaw)

            # Buoyancy brings back to surface
            if self.state.z < 0:
                self.state.vz = 1.0  # Surface quickly
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
        dt: float,
        near_wave: bool = False
    ):
        """
        Update physics based on wave interaction.

        Args:
            wave_height: Current wave height at surfer position
            wave_velocity: (vx, vy) wave-induced velocity
            water_depth: Water depth at current position
            dt: Time step
            near_wave: Is surfer near a wave (for collision/pushback)
        """
        # Update position
        self.state.x += self.state.vx * dt
        self.state.y += self.state.vy * dt
        self.state.z += self.state.vz * dt

        # Wave influence
        if self.state.is_swimming:
            # WAVE COLLISION: Pushes surfer back if NOT duck diving!
            if near_wave and not self.state.is_duck_diving:
                # Big pushback force from wave (opposite of wave direction)
                pushback_strength = 5.0
                self.state.vx += wave_velocity[0] * dt * pushback_strength
                self.state.vy += wave_velocity[1] * dt * pushback_strength
            # Duck diving: NO pushback! You're underwater
            elif not self.state.is_duck_diving:
                # Normal small wave influence
                self.state.vx += wave_velocity[0] * dt * 0.1
                self.state.vy += wave_velocity[1] * dt * 0.1

            # Wave height affects vertical position (if at surface)
            if not self.state.is_duck_diving:
                self.state.z = wave_height

        elif self.state.is_being_carried:
            # Being carried by wave - move in direction surfer is pointing
            self.state.wave_carry_timer += dt

            # Stop being carried after 5 seconds (long enough to ride)
            if self.state.wave_carry_timer >= 5.0:
                self.state.is_being_carried = False
                self.state.is_swimming = True
                self.state.wave_carry_timer = 0.0

            # Move surfer in direction they're pointing at fast speed!
            # Get surfer's direction
            surfer_direction = self.state.yaw  # What direction surfer is facing
            # Fast carry speed (3.6 m/s from wave speed, with 1.5x momentum)
            carry_speed = 5.4  # 3.6 * 1.5
            self.state.vx = np.cos(surfer_direction) * carry_speed
            self.state.vy = np.sin(surfer_direction) * carry_speed

            self.state.z = wave_height + 0.1

        elif self.state.is_surfing:
            # Riding the wave (actively surfing on the wave face!)
            # Attach surfer to the TOP of the wave for clear visual feedback
            self.state.z = wave_height + 0.5  # On top of the wave!

            # Auto-exit surfing when wave becomes whitewash
            if self.state.surfing_wave and self.state.surfing_wave.is_whitewash:
                self.state.is_surfing = False
                self.state.is_swimming = True
                self.state.surfing_wave = None
            else:
                # Surfer controls left/right movement along wave face (5x speed!)
                # Wave provides forward momentum at 1x base speed, surfer moves left/right at 5x
                wave_speed_x = wave_velocity[0]  # Wave forward push
                wave_speed_y = wave_velocity[1]  # Wave forward push

                # Add surfer's left/right movement (perpendicular to wave direction)
                # Allow W/S and A/D controls at high speed
                surfer_leftright_speed = 5.4 * 5.0  # 5x the normal speed for left/right
                surfer_leftright = self.state.vx * 0.01  # Get intended lateral direction

                # Total movement = wave push + surfer's left/right control
                self.state.vx = wave_speed_x + surfer_leftright
                self.state.vy = wave_speed_y

        elif self.state.is_whitewash_carry:
            # Being carried by whitewash after crash
            # Passively pushed toward shore (strong)
            self.state.z = wave_height * 0.5  # Tumbling in foam

            # Strong push toward shore (2x wave velocity)
            self.state.vx = wave_velocity[0] * 2.0
            self.state.vy = wave_velocity[1] * 2.0

            # Add some chaos (tumbling)
            self.state.roll += np.random.uniform(-0.5, 0.5) * dt
            self.state.pitch += np.random.uniform(-0.5, 0.5) * dt

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

        NEW BEHAVIOR: Wipeout starts whitewash carry (not episode end!)
        Surfer gets carried by whitewash toward shore until duck dive.

        Args:
            wave_height: Current wave height

        Returns:
            True if wiped out (state changed to whitewash carry)
        """
        if self.state.is_surfing or self.state.is_being_carried:
            # Excessive roll or pitch causes wipeout
            if abs(self.state.roll) > np.pi / 3 or abs(self.state.pitch) > np.pi / 4:
                self._start_whitewash_carry()
                return True

            # Falling off wave
            if self.state.is_surfing and self.state.z < wave_height - 0.5:
                self._start_whitewash_carry()
                return True

        return False

    def _start_whitewash_carry(self):
        """
        Start being carried by whitewash after crash.

        REALISTIC: Wave carries surfer toward shore.
        Can duck dive to escape whitewash and resume swimming.
        """
        self.state.has_wiped_out = True
        self.state.is_surfing = False
        self.state.is_being_carried = False
        self.state.is_swimming = False  # Not swimming, being carried!
        self.state.is_whitewash_carry = True
        self.state.on_board = True  # Still on board, just tumbling

    def try_catch_wave_angle(
        self,
        wave  # Wave object from wave_simulator
    ) -> bool:
        """
        Attempt to catch a wave with 45° angle mechanics.

        NEW WAVE-CATCHING MECHANICS:
        - Optimal angle: wave.angle + 45°
        - Tolerance: ±15° from optimal angle
        - Must be close to wave and moving toward it

        Args:
            wave: Wave object with angle and speed

        Returns:
            True if wave caught successfully (starts carrying phase)
        """
        print(f"  TRY_CATCH: surfing={self.state.is_surfing}, carrying={self.state.is_being_carried}, swimming={self.state.is_swimming}")
        # Can catch while swimming (stationary or moving), but not while already surfing or being carried
        if self.state.is_surfing or self.state.is_being_carried:
            print(f"  TRY_CATCH: FAIL - already surfing or being carried")
            return False

        # Must be in water (swimming), not on beach or elsewhere
        if not self.state.is_swimming:
            print(f"  TRY_CATCH: FAIL - not in water")
            return False

        # Calculate TWO optimal angles (can ride left OR right along wave face)
        # Match the EXACT angle calculations from the visual green arrows in play_manual.py
        # Arrow 1: wave.angle + π + π/4 + π/2
        # Arrow 2: wave.angle + π - π/4 + π/2
        optimal_angle_1 = wave.angle + np.pi + np.pi / 4 + np.pi / 2
        optimal_angle_2 = wave.angle + np.pi - np.pi / 4 + np.pi / 2

        # Normalize both angles to [-π, π]
        while optimal_angle_1 > np.pi:
            optimal_angle_1 -= 2 * np.pi
        while optimal_angle_1 < -np.pi:
            optimal_angle_1 += 2 * np.pi

        while optimal_angle_2 > np.pi:
            optimal_angle_2 -= 2 * np.pi
        while optimal_angle_2 < -np.pi:
            optimal_angle_2 += 2 * np.pi

        # Calculate angle difference helper
        def angle_diff(a, b):
            diff = abs(a - b)
            if diff > np.pi:
                diff = 2 * np.pi - diff
            return diff

        # Use surfer's yaw directly - no adjustment needed since angles are already in correct system
        surfer_yaw_check = self.state.yaw
        while surfer_yaw_check > np.pi:
            surfer_yaw_check -= 2 * np.pi
        while surfer_yaw_check < -np.pi:
            surfer_yaw_check += 2 * np.pi

        # Check if within ±15° tolerance of EITHER optimal angle
        angle_diff_1 = angle_diff(surfer_yaw_check, optimal_angle_1)
        angle_diff_2 = angle_diff(surfer_yaw_check, optimal_angle_2)

        catch_tolerance = np.radians(15)  # ±15 degrees

        # DEBUG
        print(f"  BACKEND: opt1={np.degrees(optimal_angle_1):.0f}° opt2={np.degrees(optimal_angle_2):.0f}° yaw={np.degrees(surfer_yaw_check):.0f}° diff1={np.degrees(angle_diff_1):.1f}° diff2={np.degrees(angle_diff_2):.1f}°")

        if angle_diff_1 > catch_tolerance and angle_diff_2 > catch_tolerance:
            print(f"  BACKEND: FAIL - angles too far off")
            return False  # Not at correct angle!

        # Speed requirement removed for testing - can catch stationary

        # Success! Start surfing the wave
        print(f"  BACKEND: SUCCESS - CAUGHT!")
        self.state.is_surfing = True
        self.state.is_swimming = False
        self.state.wave_carry_timer = 0.0  # Reset timer
        self.state.surfing_wave = wave  # Store reference to current wave being surfed

        return True

    def try_catch_wave(
        self,
        wave  # Wave object from wave_simulator
    ) -> bool:
        """
        Attempt to catch a wave and start being carried (LEGACY).

        REAL SURFING TECHNIQUE:
        - Must paddle at 45° angle to wave front (perpendicular)
        - Tolerance: ±5° (very precise!)
        - Must be moving with wave speed

        Args:
            wave: Wave object with front_angle and speed

        Returns:
            True if wave caught successfully (starts carrying phase)
        """
        if self.state.is_surfing or self.state.is_being_carried or not self.state.is_swimming:
            return False

        # Get ideal catch angles (45° to wave front)
        angle1, angle2 = wave.get_ideal_catch_angles()

        # Check if surfer yaw matches either ideal angle (±5°)
        tolerance = np.radians(5)  # ±5 degrees

        # Normalize angles for comparison
        def angle_diff(a, b):
            diff = abs(a - b)
            if diff > np.pi:
                diff = 2 * np.pi - diff
            return diff

        diff1 = angle_diff(self.state.yaw, angle1)
        diff2 = angle_diff(self.state.yaw, angle2)

        # Must be within ±5° of one of the ideal angles
        if diff1 > tolerance and diff2 > tolerance:
            return False  # Not at correct angle!

        # Need correct board angle (not too pitched)
        if abs(self.state.pitch) > np.pi / 12:  # 15 degrees
            return False

        # Need to be moving with wave
        surfer_speed = np.sqrt(self.state.vx**2 + self.state.vy**2)
        if surfer_speed < wave.speed * 0.7:
            return False

        # Success! Start being carried by wave
        self.state.is_being_carried = True
        self.state.is_swimming = False
        self.state.wave_carry_timer = 0.0  # Reset timer

        # Store required carry duration (depends on wave size!)
        self.state.required_carry_duration = wave.get_carry_duration()

        return True

    def try_stand_up_angle(
        self,
        wave,  # Wave object
        angle_diff: float
    ) -> Tuple[bool, str]:
        """
        Attempt to stand up with angle-based mechanics.

        NEW STAND-UP MECHANICS:
        - Must be carried for required duration (wave-size dependent)
        - Must be within ±15° of optimal angle
        - Angle is already calculated by caller

        Args:
            wave: Wave object
            angle_diff: Pre-calculated angle difference from optimal

        Returns:
            (success, message): True if successfully stood up, with reason message
        """
        if not self.state.is_being_carried:
            return False, "Not being carried by wave"

        # Check if carried long enough (duration depends on wave size!)
        if self.state.wave_carry_timer < self.state.required_carry_duration:
            # CRASH: Stood up too early!
            self._start_whitewash_carry()
            return False, f"Crashed: stood up too early ({self.state.wave_carry_timer:.2f}s < {self.state.required_carry_duration:.2f}s)"

        # Check angle tolerance (±15°)
        stand_up_tolerance = np.radians(15)  # ±15 degrees
        if angle_diff > stand_up_tolerance:
            # CRASH: Not at correct angle!
            self._start_whitewash_carry()
            return False, f"Crashed: wrong angle ({np.degrees(angle_diff):.1f}° off, need <15°)"

        # SUCCESS! Stand up and start surfing
        self.state.is_being_carried = False
        self.state.is_surfing = True
        return True, "Successfully stood up!"

    def try_stand_up(
        self,
        wave_direction: float
    ) -> Tuple[bool, str]:
        """
        Attempt to stand up and start surfing (LEGACY).

        Must be carried for at least 1 second and match wave direction.

        Args:
            wave_direction: Current wave direction in radians

        Returns:
            (success, message): True if successfully stood up, with reason message
        """
        if not self.state.is_being_carried:
            return False, "Not being carried by wave"

        # Check if carried long enough (duration depends on wave size!)
        if self.state.wave_carry_timer < self.state.required_carry_duration:
            # CRASH: Stood up too early!
            self.state.is_being_carried = False
            self.state.is_swimming = True
            self.state.has_wiped_out = True
            return False, f"Crashed: stood up too early ({self.state.wave_carry_timer:.2f}s < {self.state.required_carry_duration:.2f}s)"

        # Check if orientation matches wave direction
        direction_diff = abs(wave_direction - self.state.yaw)
        if direction_diff > np.pi:
            direction_diff = 2 * np.pi - direction_diff

        # Must be aligned with wave (strict requirement for standing)
        if direction_diff > np.pi / 6:  # 30 degrees max deviation
            # CRASH: Not aligned with wave!
            self.state.is_being_carried = False
            self.state.is_swimming = True
            self.state.has_wiped_out = True
            return False, f"Crashed: not aligned with wave ({np.degrees(direction_diff):.1f}° off)"

        # SUCCESS! Stand up and start surfing
        self.state.is_being_carried = False
        self.state.is_surfing = True
        return True, "Successfully stood up!"

    def get_observation(self) -> np.ndarray:
        """
        Get surfer state as observation vector.

        Returns:
            Observation array (18 values)
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
            float(self.state.is_being_carried),
            float(self.state.is_surfing),
            float(self.state.is_whitewash_carry),
            self.state.wave_carry_timer,  # Time being carried (for agent to know)
        ], dtype=np.float32)
