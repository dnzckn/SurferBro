"""Simplified ocean wave simulation - easy to learn and understand!"""

import numpy as np
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass
from surferbro.physics.ocean_floor import OceanFloor


from enum import Enum

class WavePhase(Enum):
    """Wave lifecycle phases - SIMPLIFIED to just 2 phases!"""
    BUILDING = "building"    # Wave is forming, growing
    BREAKING = "breaking"    # Wave is breaking, rideable!

@dataclass
class Wave:
    """Represents a simple circular wave moving toward shore."""
    x: float  # X position (center of wave)
    y: float  # Y position (center of wave)
    height: float  # Current wave height in meters
    max_height: float  # Maximum height this wave will reach
    speed: float  # Wave speed in m/s
    period: float  # Wave period in seconds
    phase: WavePhase = WavePhase.BUILDING
    phase_timer: float = 0.0  # Time in current phase

    # Phase durations
    building_duration: float = 2.0  # 2s to build
    breaking_duration: float = 5.0  # 5s rideable window

    def get_carry_duration(self) -> float:
        """
        Get required carry duration based on wave size.

        Bigger waves require longer carry time (1-3 seconds).

        Returns:
            Carry duration in seconds
        """
        # Map wave height to carry duration
        # Small waves (0.5m) = 1s, Big waves (3m+) = 3s
        min_carry = 1.0
        max_carry = 3.0
        min_height = 0.5
        max_height = 3.0

        # Linear interpolation
        t = (self.max_height - min_height) / (max_height - min_height)
        t = np.clip(t, 0, 1)

        return min_carry + t * (max_carry - min_carry)

    @property
    def position(self) -> np.ndarray:
        """Wave position as numpy array."""
        return np.array([self.x, self.y])

    @property
    def x_start(self) -> float:
        """X coordinate of wave start (for compatibility)."""
        return self.x - 10.0  # Simple wave width

    @property
    def x_end(self) -> float:
        """X coordinate of wave end (for compatibility)."""
        return self.x + 10.0  # Simple wave width

    @property
    def y_position(self) -> float:
        """Y coordinate of wave (for compatibility)."""
        return self.y

    @property
    def is_breaking(self) -> bool:
        """Check if wave is in breaking phase."""
        return self.phase == WavePhase.BREAKING

    @property
    def is_whitewash(self) -> bool:
        """Compatibility property - no whitewash in simplified version."""
        return False


class WaveSimulator:
    """
    SIMPLIFIED ocean wave simulation - easy to learn!

    Waves are simple circles that move straight toward shore.
    Only 2 phases: building and breaking.
    No complex angles or vector math!
    """

    def __init__(
        self,
        ocean_floor: OceanFloor,
        wave_period: float = 8.0,
        base_height: float = 1.5,
        direction: float = 270.0,
        pier_positions: List[Tuple[float, float]] = None,
        randomness: float = 0.2,
        breaking_depth_ratio: float = 1.3,
        whitewash_duration: float = 5.0
    ):
        """
        Initialize wave simulator.

        Automatically detects beach location and spawns waves from deep water.

        Args:
            ocean_floor: OceanFloor instance
            wave_period: Time between waves in seconds
            base_height: Base wave height in meters
            direction: Wave direction in degrees (ignored in simplified version)
            pier_positions: List of (x, y) pier positions (not used)
            randomness: Wave height variation (0-1)
            breaking_depth_ratio: Wave breaks when height > depth * ratio
            whitewash_duration: Not used in simplified version
        """
        self.ocean_floor = ocean_floor
        self.wave_period = wave_period
        self.base_height = base_height
        self.randomness = randomness
        self.breaking_depth_ratio = breaking_depth_ratio

        self.waves: List[Wave] = []
        self.time = 0.0
        self.last_wave_spawn = 0.0

        # AUTO-DETECT beach location (simplified)
        self._detect_beach_location()

    def _detect_beach_location(self):
        """
        SIMPLIFIED: Auto-detect where beach is.

        Just finds shallow water and determines if waves should move up or down.
        """
        ocean_width, ocean_height = self.ocean_floor.get_dimensions()

        # Sample depths at a few points along Y-axis
        center_x = ocean_width / 2
        depth_at_bottom = self.ocean_floor.get_depth(center_x, ocean_height * 0.1)
        depth_at_top = self.ocean_floor.get_depth(center_x, ocean_height * 0.9)

        # Determine which end is the beach (shallower)
        if depth_at_bottom < depth_at_top:
            # Beach at bottom - waves spawn at top, move down
            self.spawn_y_ratio = 0.75
            self.move_direction = -1  # Move toward y=0
            print(f"🏖️  Beach at BOTTOM - waves move DOWN")
        else:
            # Beach at top - waves spawn at bottom, move up
            self.spawn_y_ratio = 0.25
            self.move_direction = 1  # Move toward y=max
            print(f"🏖️  Beach at TOP - waves move UP")

    def step(self, dt: float):
        """
        SIMPLIFIED: Advance simulation by dt seconds.

        Args:
            dt: Time step in seconds
        """
        self.time += dt

        # Spawn new waves periodically
        if self.time - self.last_wave_spawn >= self.wave_period:
            self._spawn_wave()
            self.last_wave_spawn = self.time

        # Update existing waves
        waves_to_remove = []
        for wave in self.waves:
            self._update_wave(wave, dt)

            # Remove waves that reached shore or decayed
            ocean_width, ocean_height = self.ocean_floor.get_dimensions()
            if wave.y <= 0 or wave.y >= ocean_height or wave.height < 0.1:
                waves_to_remove.append(wave)

        # Clean up finished waves
        for wave in waves_to_remove:
            self.waves.remove(wave)

    def _spawn_wave(self):
        """SIMPLIFIED: Spawn a new circular wave from deep water."""
        ocean_width, ocean_height = self.ocean_floor.get_dimensions()

        # Spawn at center X, deep water Y
        spawn_x = ocean_width / 2
        spawn_y = ocean_height * self.spawn_y_ratio

        # Max height with small random variation
        max_height = self.base_height * (1 + np.random.uniform(-self.randomness, self.randomness))
        initial_height = max_height * 0.2

        # Simple wave speed
        speed = 2.0  # Fixed speed in m/s - simple!

        wave = Wave(
            x=spawn_x,
            y=spawn_y,
            height=initial_height,
            max_height=max_height,
            speed=speed,
            period=self.wave_period,
            phase=WavePhase.BUILDING,
            phase_timer=0.0
        )

        self.waves.append(wave)
        print(f"🌊 New wave spawned at ({spawn_x:.1f}, {spawn_y:.1f})")

    def _update_wave(self, wave: Wave, dt: float):
        """SIMPLIFIED: Update wave through 2 simple phases."""
        wave.phase_timer += dt

        # Phase 1: BUILDING - wave grows
        if wave.phase == WavePhase.BUILDING:
            # Grow height over building duration
            growth_progress = wave.phase_timer / wave.building_duration
            wave.height = wave.max_height * (0.2 + 0.8 * min(1.0, growth_progress))

            # Transition to BREAKING when building complete
            if wave.phase_timer >= wave.building_duration:
                wave.phase = WavePhase.BREAKING
                wave.phase_timer = 0.0
                wave.height = wave.max_height
                print(f"🌊 Wave at ({wave.x:.1f}, {wave.y:.1f}) is now BREAKING!")

        # Phase 2: BREAKING - wave is rideable, then decays
        elif wave.phase == WavePhase.BREAKING:
            # Check if we should start decaying
            depth = self.ocean_floor.get_depth(wave.x, wave.y)

            # After some time or in shallow water, start to decay
            if wave.phase_timer > wave.breaking_duration or \
               (depth > 0 and wave.height > depth * self.breaking_depth_ratio):
                wave.height *= 0.95  # Decay

        # Move wave toward shore (simple Y movement!)
        wave.y += self.move_direction * wave.speed * dt

    def get_wave_height_at(self, x: float, y: float, current_time: float = None) -> float:
        """
        SIMPLIFIED: Get wave height at a position.

        Wave affects height if position is within a circular radius.
        Simple distance calculation - no complex vector math!

        Args:
            x: X coordinate
            y: Y coordinate
            current_time: Current simulation time (unused, for compatibility)

        Returns:
            Wave height in meters
        """
        total_height = 0.0

        for wave in self.waves:
            # Simple distance from wave center
            dx = x - wave.x
            dy = y - wave.y
            distance = np.sqrt(dx**2 + dy**2)

            # Wave influence radius
            wave_radius = 5.0  # meters - simple!

            if distance < wave_radius:
                # Height decreases linearly with distance
                influence = 1.0 - (distance / wave_radius)
                total_height += wave.height * influence

        return max(0, total_height)

    def get_wave_velocity_at(self, x: float, y: float) -> Tuple[float, float]:
        """
        SIMPLIFIED: Get wave-induced water velocity at a position.

        Simple distance-based velocity toward shore.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            (vx, vy) water velocity in m/s
        """
        vx, vy = 0.0, 0.0

        for wave in self.waves:
            # Simple distance from wave center
            dx = x - wave.x
            dy = y - wave.y
            distance = np.sqrt(dx**2 + dy**2)

            # Larger influence zone for velocity
            velocity_radius = 8.0  # meters

            if distance < velocity_radius:
                influence = 1.0 - (distance / velocity_radius)

                # Velocity strength based on wave phase
                if wave.phase == WavePhase.BREAKING:
                    v_strength = wave.speed * 0.4  # Breaking pushes moderately
                else:
                    v_strength = wave.speed * 0.1  # Building has little effect

                v = v_strength * influence

                # Velocity pushes toward shore (simple Y direction!)
                vy += self.move_direction * v

        return vx, vy

    def is_in_wave_zone(self, x: float, y: float) -> bool:
        """
        SIMPLIFIED: Check if position is in the wave zone.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if in wave zone
        """
        depth = self.ocean_floor.get_depth(x, y)
        return 2.0 < depth < 15.0  # Sweet spot for surfing

    def get_nearest_wave(self, x: float, y: float) -> Optional[Wave]:
        """
        SIMPLIFIED: Get the nearest wave to a position.

        Uses simple distance calculation!

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Nearest Wave object or None
        """
        if not self.waves:
            return None

        min_dist = float('inf')
        nearest = None

        for wave in self.waves:
            # Simple distance calculation
            dx = x - wave.x
            dy = y - wave.y
            distance = np.sqrt(dx**2 + dy**2)

            if distance < min_dist:
                min_dist = distance
                nearest = wave

        return nearest

    def get_state(self) -> Dict:
        """
        SIMPLIFIED: Get current wave simulation state.

        Returns:
            Dictionary with wave information
        """
        return {
            'time': self.time,
            'num_waves': len(self.waves),
            'waves': [
                {
                    'position': [wave.x, wave.y],
                    'height': wave.height,
                    'is_breaking': wave.is_breaking,
                    'phase': wave.phase.value
                }
                for wave in self.waves
            ]
        }
