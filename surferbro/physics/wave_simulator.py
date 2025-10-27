"""Advanced ocean wave simulation with realistic physics."""

import numpy as np
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass
from surferbro.physics.ocean_floor import OceanFloor


from enum import Enum

class WavePhase(Enum):
    """Wave lifecycle phases."""
    BUILDING = "building"    # Wave is forming, growing
    FRONT = "front"          # Wave front is formed, rideable!
    WHITEWASH = "whitewash"  # Wave has broken, just foam

@dataclass
class Wave:
    """Represents an angled wave front moving toward shore."""
    front_start: np.ndarray  # [x, y] start point of wave front line
    front_end: np.ndarray    # [x, y] end point of wave front line
    height: float  # Current wave height in meters
    max_height: float  # Maximum height this wave will reach
    speed: float  # Wave speed in m/s (how fast front advances)
    period: float  # Wave period in seconds
    direction: float  # Direction wave is traveling (in radians)
    phase: WavePhase = WavePhase.BUILDING
    phase_timer: float = 0.0  # Time in current phase

    # Phase durations
    building_duration: float = 2.0  # 2s to build
    front_duration: float = 3.0  # 3s rideable window

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
        """Center position of wave front."""
        return (self.front_start + self.front_end) / 2

    @property
    def x_start(self) -> float:
        """X coordinate of front start (for compatibility)."""
        return self.front_start[0]

    @property
    def x_end(self) -> float:
        """X coordinate of front end (for compatibility)."""
        return self.front_end[0]

    @property
    def y_position(self) -> float:
        """Y coordinate of front center (for compatibility)."""
        return self.position[1]

    @property
    def is_breaking(self) -> bool:
        """Compatibility property."""
        return self.phase == WavePhase.FRONT

    @property
    def is_whitewash(self) -> bool:
        """Compatibility property."""
        return self.phase == WavePhase.WHITEWASH

    @property
    def front_angle(self) -> float:
        """
        Angle of the wave front LINE (perpendicular to wave direction).

        Returns:
            Angle in radians of the wave front line
        """
        # Wave front is perpendicular to wave direction
        # If wave travels at angle θ, front line is at θ + 90°
        return self.direction + np.pi/2

    def get_ideal_catch_angles(self) -> tuple[float, float]:
        """
        Get the two ideal angles for catching this wave.

        Surfer should be at 45° to the wave front (perpendicular).

        Returns:
            (angle1, angle2): Two valid catch angles in radians
        """
        # Wave front angle
        front_angle = self.front_angle

        # Surfer should be at ±45° to the front
        angle1 = front_angle + np.pi/4  # +45°
        angle2 = front_angle - np.pi/4  # -45°

        return (angle1, angle2)


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

        Automatically detects beach location and spawns waves from deep water.

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
        self.pier_positions = pier_positions or []
        self.randomness = randomness
        self.breaking_depth_ratio = breaking_depth_ratio
        self.whitewash_duration = whitewash_duration

        self.waves: List[Wave] = []
        self.time = 0.0
        self.last_wave_spawn = 0.0

        # AUTO-DETECT beach location and wave direction
        self._detect_beach_and_wave_direction(direction)

    def _detect_beach_and_wave_direction(self, base_direction_deg: float):
        """
        Auto-detect where beach is and set wave spawn location/direction.

        Analyzes ocean floor to find shallow water (beach) and deep water,
        then spawns waves from deep water toward beach.

        Args:
            base_direction_deg: Base direction in degrees (for angle variation)
        """
        ocean_width, ocean_height = self.ocean_floor.get_dimensions()

        # Sample depths along Y-axis at center X
        center_x = ocean_width / 2
        y_samples = 10
        depths_at_y = []

        for i in range(y_samples):
            y = (i / (y_samples - 1)) * ocean_height
            depth = self.ocean_floor.get_depth(center_x, y)
            depths_at_y.append((y, depth))

        # Find where shallow water is (beach)
        shallow_y = []
        deep_y = []

        for y, depth in depths_at_y:
            if depth < 2.0:  # Shallow = beach
                shallow_y.append(y)
            elif depth > 5.0:  # Deep water
                deep_y.append(y)

        # Determine beach location
        if shallow_y and deep_y:
            avg_shallow = np.mean(shallow_y)
            avg_deep = np.mean(deep_y)

            # Beach is where shallow water is
            beach_at_bottom = avg_shallow < avg_deep

            if beach_at_bottom:
                # Beach at low Y (y=0 side)
                # Waves spawn at high Y, move toward y=0
                self.spawn_y_ratio = 0.75  # Spawn at 75% of height
                self.wave_base_direction = -np.pi / 2  # South (-Y direction)
                print(f"🏖️  Beach detected at BOTTOM (y≈{avg_shallow:.1f}m)")
                print(f"🌊 Waves will spawn at TOP and move DOWN")
            else:
                # Beach at high Y (y=max side)
                # Waves spawn at low Y, move toward y=max
                self.spawn_y_ratio = 0.25  # Spawn at 25% of height
                self.wave_base_direction = np.pi / 2  # North (+Y direction)
                print(f"🏖️  Beach detected at TOP (y≈{avg_shallow:.1f}m)")
                print(f"🌊 Waves will spawn at BOTTOM and move UP")
        else:
            # Fallback: assume standard setup (beach at bottom)
            self.spawn_y_ratio = 0.75
            self.wave_base_direction = -np.pi / 2
            print("⚠️  Could not auto-detect beach, using default (bottom)")

        # Store for later use
        self.direction = np.radians(base_direction_deg)  # Store for variation

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

            # Remove waves that:
            # 1. Reached shore (y <= 0)
            # 2. Whitewash that has decayed (height < 0.1m)
            if wave.y_position <= 0 or \
               (wave.phase == WavePhase.WHITEWASH and wave.height < 0.1):
                waves_to_remove.append(wave)

        # Clean up finished waves
        for wave in waves_to_remove:
            self.waves.remove(wave)

    def _spawn_wave(self):
        """Spawn a new wave front with angled direction from deep water."""
        ocean_width, ocean_height = self.ocean_floor.get_dimensions()

        # Use detected spawn location (deep water side)
        spawn_y = ocean_height * self.spawn_y_ratio

        # ANGLED WAVE DIRECTION with variation
        # Use detected base direction (toward beach)
        angle_variation = np.radians(30)  # ±30 degrees variation
        wave_direction = self.wave_base_direction + np.random.uniform(-angle_variation, angle_variation)

        # Clamp to reasonable range based on base direction
        # If moving south (-Y), allow -2π/3 to -π/3 (240° to 300°)
        # If moving north (+Y), allow π/3 to 2π/3 (60° to 120°)
        if self.wave_base_direction < 0:  # Moving south
            wave_direction = np.clip(wave_direction, -2*np.pi/3, -np.pi/3)
        else:  # Moving north
            wave_direction = np.clip(wave_direction, np.pi/3, 2*np.pi/3)

        # Calculate wave front LINE perpendicular to wave direction
        # Front line direction is perpendicular (rotate by 90°)
        front_line_angle = wave_direction + np.pi/2

        # Front line extends across ocean
        # Calculate endpoints that span the ocean
        center_x = ocean_width / 2
        half_length = ocean_width * 0.7  # Front line length

        # Front line endpoints
        dx = np.cos(front_line_angle) * half_length
        dy = np.sin(front_line_angle) * half_length

        front_start = np.array([center_x - dx, spawn_y - dy])
        front_end = np.array([center_x + dx, spawn_y + dy])

        # Max height with random variation
        max_height = self.base_height * (1 + np.random.uniform(-self.randomness, self.randomness))
        initial_height = max_height * 0.2

        # Wave speed - slower for small oceans
        base_speed = 1.56 * self.wave_period
        if ocean_height < 100:
            speed = base_speed * 0.25
        else:
            speed = base_speed * 0.5

        wave = Wave(
            front_start=front_start,
            front_end=front_end,
            height=initial_height,
            max_height=max_height,
            speed=speed,
            period=self.wave_period,
            direction=wave_direction,  # Angled!
            phase=WavePhase.BUILDING,
            phase_timer=0.0
        )

        self.waves.append(wave)

    def _update_wave(self, wave: Wave, dt: float):
        """Update wave front through its lifecycle phases."""
        wave.phase_timer += dt

        # Phase transitions
        if wave.phase == WavePhase.BUILDING:
            # Grow height over building duration
            growth_progress = wave.phase_timer / wave.building_duration
            wave.height = wave.max_height * (0.2 + 0.8 * min(1.0, growth_progress))

            # Transition to FRONT when building complete
            if wave.phase_timer >= wave.building_duration:
                wave.phase = WavePhase.FRONT
                wave.phase_timer = 0.0
                wave.height = wave.max_height

        elif wave.phase == WavePhase.FRONT:
            # Front phase: maintain max height, this is rideable!
            wave.height = wave.max_height

            # Check depth-based breaking
            center_x = (wave.x_start + wave.x_end) / 2
            depth = self.ocean_floor.get_depth(center_x, wave.y_position)

            # Transition to WHITEWASH when too shallow OR front duration expires
            if (depth > 0 and wave.height > depth * self.breaking_depth_ratio) or \
               (wave.phase_timer >= wave.front_duration):
                wave.phase = WavePhase.WHITEWASH
                wave.phase_timer = 0.0

        elif wave.phase == WavePhase.WHITEWASH:
            # Whitewash phase: decay height, move slower
            wave.height *= 0.98  # Gradual decay
            wave.speed *= 0.95  # Slow down

        # Move wave front in its direction
        # Both endpoints move together (parallel translation)
        dx = np.cos(wave.direction) * wave.speed * dt
        dy = np.sin(wave.direction) * wave.speed * dt
        movement = np.array([dx, dy])

        wave.front_start += movement
        wave.front_end += movement

        # Check if wave reached shore (center y < 0)
        if wave.position[1] < 0:
            # Clamp to shore
            wave.front_start[1] = max(0, wave.front_start[1])
            wave.front_end[1] = max(0, wave.front_end[1])

    def get_wave_height_at(self, x: float, y: float, current_time: float = None) -> float:
        """
        Get wave height at a position (from wave fronts).

        Wave affects height if position is within the front's influence zone.

        Args:
            x: X coordinate
            y: Y coordinate
            current_time: Current simulation time (unused, for compatibility)

        Returns:
            Wave height in meters
        """
        if current_time is None:
            current_time = self.time

        total_height = 0.0

        for wave in self.waves:
            # Calculate distance from point to wave front LINE
            # Use perpendicular distance formula
            point = np.array([x, y])

            # Vector along wave front
            front_vec = wave.front_end - wave.front_start
            front_length = np.linalg.norm(front_vec)

            if front_length < 0.01:
                continue  # Degenerate wave

            # Vector from front start to point
            to_point = point - wave.front_start

            # Project point onto front line
            t = np.dot(to_point, front_vec) / (front_length ** 2)
            t = np.clip(t, 0, 1)  # Clamp to line segment

            # Closest point on line segment
            closest = wave.front_start + t * front_vec

            # Distance from point to front line
            dist_to_front = np.linalg.norm(point - closest)

            # Wave influence based on distance (thickness zone)
            front_thickness = 2.0  # meters
            if dist_to_front < front_thickness:
                influence = 1.0 - (dist_to_front / front_thickness)
                total_height += wave.height * influence

        return max(0, total_height)

    def get_wave_velocity_at(self, x: float, y: float) -> Tuple[float, float]:
        """
        Get wave-induced water velocity at a position (from wave fronts).

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            (vx, vy) water velocity in m/s
        """
        vx, vy = 0.0, 0.0

        for wave in self.waves:
            # Calculate distance from point to wave front
            point = np.array([x, y])
            front_vec = wave.front_end - wave.front_start
            front_length = np.linalg.norm(front_vec)

            if front_length < 0.01:
                continue

            to_point = point - wave.front_start
            t = np.dot(to_point, front_vec) / (front_length ** 2)
            t = np.clip(t, 0, 1)
            closest = wave.front_start + t * front_vec
            dist_to_front = np.linalg.norm(point - closest)

            # Larger influence zone for velocity
            front_thickness = 3.0
            if dist_to_front < front_thickness:
                influence = 1.0 - (dist_to_front / front_thickness)

                # Velocity strength based on wave phase
                if wave.phase == WavePhase.WHITEWASH:
                    v_strength = wave.speed * 0.5  # Whitewash pushes hard
                elif wave.phase == WavePhase.FRONT:
                    v_strength = wave.speed * 0.3  # Front pushes moderately
                else:
                    v_strength = wave.speed * 0.1  # Building has little effect

                v = v_strength * influence

                # Velocity in wave's direction
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
        Get the nearest wave front to a position.

        For wave fronts, "nearest" means closest in y-direction.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Nearest Wave object or None
        """
        if not self.waves:
            return None

        min_y_dist = float('inf')
        nearest = None

        for wave in self.waves:
            # Check if within x-range of this wave front
            if wave.x_start <= x <= wave.x_end:
                y_dist = abs(y - wave.y_position)
                if y_dist < min_y_dist:
                    min_y_dist = y_dist
                    nearest = wave

        # If no wave contains this x position, find closest by y anyway
        if nearest is None and self.waves:
            for wave in self.waves:
                y_dist = abs(y - wave.y_position)
                if y_dist < min_y_dist:
                    min_y_dist = y_dist
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
