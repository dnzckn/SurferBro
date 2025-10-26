"""Advanced ocean wave simulation with realistic physics."""

import numpy as np
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass
from surferbro.physics.ocean_floor import OceanFloor


@dataclass
class Wave:
    """Represents a single wave."""
    position: np.ndarray  # [x, y] position of wave front
    height: float  # Wave height in meters
    direction: float  # Direction in radians
    speed: float  # Wave speed in m/s
    period: float  # Wave period in seconds
    is_breaking: bool = False
    is_whitewash: bool = False
    whitewash_timer: float = 0.0


class WaveSimulator:
    """
    Simulates ocean waves with realistic physics including:
    - Wave propagation based on depth
    - Breaking waves
    - Whitewash after breaking
    - Pier interference
    - Wave refraction
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

        Args:
            ocean_floor: OceanFloor instance
            wave_period: Time between waves in seconds
            base_height: Base wave height in meters
            direction: Wave direction in degrees (0=North, 90=East, etc.)
            pier_positions: List of (x, y) pier positions
            randomness: Wave height variation (0-1)
            breaking_depth_ratio: Wave breaks when height > depth * ratio
            whitewash_duration: How long whitewash lasts in seconds
        """
        self.ocean_floor = ocean_floor
        self.wave_period = wave_period
        self.base_height = base_height
        self.direction = np.radians(direction)
        self.pier_positions = pier_positions or []
        self.randomness = randomness
        self.breaking_depth_ratio = breaking_depth_ratio
        self.whitewash_duration = whitewash_duration

        self.waves: List[Wave] = []
        self.time = 0.0
        self.last_wave_spawn = 0.0

        # Wave spawn area (far from shore, but ON the map)
        ocean_width, ocean_height = self.ocean_floor.get_dimensions()
        self.spawn_distance = min(150.0, ocean_height * 0.8)  # Don't spawn off-map!

    def step(self, dt: float):
        """
        Advance simulation by dt seconds.

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

            # Remove waves that reached shore or expired whitewash
            if wave.is_whitewash and wave.whitewash_timer <= 0:
                waves_to_remove.append(wave)

        # Clean up finished waves
        for wave in waves_to_remove:
            self.waves.remove(wave)

    def _spawn_wave(self):
        """Spawn a new wave at the spawn distance."""
        # Random height variation
        height = self.base_height * (1 + np.random.uniform(-self.randomness, self.randomness))

        ocean_width, ocean_height = self.ocean_floor.get_dimensions()

        # Spawn waves at FAR end of ocean (deep water) moving toward shore
        # Shore is at y=0, deep ocean at y=ocean_height
        # But keep waves ON the map by spawning closer for small oceans
        if ocean_height < 100:
            spawn_y = ocean_height * 0.65  # Closer for small maps
        else:
            spawn_y = ocean_height * 0.85  # Far for large maps

        spawn_x = ocean_width / 2  # Center

        # Waves should move TOWARD shore (negative y direction)
        # Override direction to point toward beach
        wave_direction = -np.pi / 2  # Pointing toward y=0 (south/toward beach)

        position = np.array([spawn_x, spawn_y])

        # Wave speed - scale based on ocean size to keep waves visible
        # For small oceans, slow down waves to keep them on-screen longer
        base_speed = 1.56 * self.wave_period
        if ocean_height < 100:
            speed = base_speed * 0.3  # Slower for small maps
        else:
            speed = base_speed

        wave = Wave(
            position=position,
            height=height,
            direction=wave_direction,  # Use corrected direction toward shore
            speed=speed,
            period=self.wave_period
        )

        self.waves.append(wave)

    def _update_wave(self, wave: Wave, dt: float):
        """Update a single wave."""
        # Get current depth
        depth = self.ocean_floor.get_depth(wave.position[0], wave.position[1])

        if wave.is_whitewash:
            # Whitewash moves slower and decays
            wave.speed = 2.0  # m/s
            wave.whitewash_timer -= dt
            wave.height *= 0.95  # Decay

        elif wave.is_breaking:
            # Breaking wave transitions to whitewash
            wave.is_whitewash = True
            wave.whitewash_timer = self.whitewash_duration
            wave.height *= 0.7  # Reduce height

        else:
            # Check if wave should break
            if depth > 0 and wave.height > depth * self.breaking_depth_ratio:
                wave.is_breaking = True

            # Wave speed depends on depth (shallow water wave theory)
            if depth > 0:
                # c = sqrt(g * depth) for shallow water
                wave.speed = np.sqrt(9.81 * depth)

            # Wave refraction - waves turn toward shore as they slow
            gradient = self.ocean_floor.get_gradient(wave.position[0], wave.position[1])
            if depth > 0 and depth < 10:
                # Refraction effect
                refraction = -np.arctan2(gradient[1], gradient[0]) * 0.1
                wave.direction += refraction * dt

        # Check pier interference
        for pier_x, pier_y in self.pier_positions:
            dist = np.linalg.norm(wave.position - np.array([pier_x, pier_y]))
            if dist < 2.0:  # Pier interference radius
                # Pier reduces wave height
                wave.height *= 0.7
                # Pier can cause wave to break
                if not wave.is_breaking and not wave.is_whitewash:
                    wave.is_breaking = True

        # Move wave
        dx = np.cos(wave.direction) * wave.speed * dt
        dy = np.sin(wave.direction) * wave.speed * dt
        wave.position += np.array([dx, dy])

    def get_wave_height_at(self, x: float, y: float, current_time: float = None) -> float:
        """
        Get total wave height at a position.

        Args:
            x: X coordinate
            y: Y coordinate
            current_time: Current simulation time (uses self.time if None)

        Returns:
            Wave height in meters
        """
        if current_time is None:
            current_time = self.time

        total_height = 0.0

        for wave in self.waves:
            # Distance from wave front
            dist = np.linalg.norm(np.array([x, y]) - wave.position)

            # Wave profile (sine wave)
            wavelength = wave.speed * wave.period
            if dist < wavelength * 2:  # Only nearby waves affect
                phase = (dist / wavelength) * 2 * np.pi
                # Gaussian envelope to localize wave
                envelope = np.exp(-((dist / wavelength) ** 2))
                height = wave.height * np.sin(phase) * envelope
                total_height += height

        return max(0, total_height)

    def get_wave_velocity_at(self, x: float, y: float) -> Tuple[float, float]:
        """
        Get wave-induced water velocity at a position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            (vx, vy) water velocity in m/s
        """
        vx, vy = 0.0, 0.0

        for wave in self.waves:
            dist = np.linalg.norm(np.array([x, y]) - wave.position)
            wavelength = wave.speed * wave.period

            if dist < wavelength * 2:
                # Wave orbital velocity
                envelope = np.exp(-((dist / wavelength) ** 2))
                v = wave.speed * 0.3 * envelope  # Scale down velocity

                # Direction of wave
                vx += np.cos(wave.direction) * v
                vy += np.sin(wave.direction) * v

        return vx, vy

    def is_in_wave_zone(self, x: float, y: float) -> bool:
        """
        Check if position is in the wave zone (where waves are active).

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
        Get the nearest wave to a position.

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
            dist = np.linalg.norm(np.array([x, y]) - wave.position)
            if dist < min_dist:
                min_dist = dist
                nearest = wave

        return nearest

    def get_state(self) -> Dict:
        """
        Get current wave simulation state.

        Returns:
            Dictionary with wave information
        """
        return {
            'time': self.time,
            'num_waves': len(self.waves),
            'waves': [
                {
                    'position': wave.position.tolist(),
                    'height': wave.height,
                    'is_breaking': wave.is_breaking,
                    'is_whitewash': wave.is_whitewash
                }
                for wave in self.waves
            ]
        }
