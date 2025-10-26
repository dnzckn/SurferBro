"""Jellyfish obstacles for the surfing environment."""

import numpy as np
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Jellyfish:
    """Represents a jellyfish obstacle."""
    x: float
    y: float
    z: float  # Depth
    vx: float = 0.0
    vy: float = 0.0
    radius: float = 0.3


class JellyfishSwarm:
    """Manages a swarm of jellyfish obstacles."""

    def __init__(
        self,
        count: int,
        ocean_width: float,
        ocean_height: float,
        min_depth: float = 0.5,
        max_depth: float = 3.0,
        speed: float = 0.2,
        radius: float = 0.3
    ):
        """
        Initialize jellyfish swarm.

        Args:
            count: Number of jellyfish
            ocean_width: Ocean width in meters
            ocean_height: Ocean height in meters
            min_depth: Minimum spawn depth
            max_depth: Maximum spawn depth
            speed: Movement speed in m/s
            radius: Jellyfish radius for collision
        """
        self.count = count
        self.ocean_width = ocean_width
        self.ocean_height = ocean_height
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.speed = speed
        self.radius = radius

        self.jellyfish: List[Jellyfish] = []
        self._spawn_jellyfish()

    def _spawn_jellyfish(self):
        """Spawn jellyfish randomly in the ocean."""
        self.jellyfish.clear()

        for _ in range(self.count):
            x = np.random.uniform(0, self.ocean_width)
            y = np.random.uniform(0, self.ocean_height)
            z = np.random.uniform(self.min_depth, self.max_depth)

            # Random initial velocity
            angle = np.random.uniform(0, 2 * np.pi)
            vx = np.cos(angle) * self.speed
            vy = np.sin(angle) * self.speed

            jelly = Jellyfish(
                x=x, y=y, z=z,
                vx=vx, vy=vy,
                radius=self.radius
            )
            self.jellyfish.append(jelly)

    def update(self, dt: float):
        """
        Update jellyfish positions.

        Args:
            dt: Time step in seconds
        """
        for jelly in self.jellyfish:
            # Update position
            jelly.x += jelly.vx * dt
            jelly.y += jelly.vy * dt

            # Bounce off boundaries
            if jelly.x < 0 or jelly.x > self.ocean_width:
                jelly.vx = -jelly.vx
                jelly.x = np.clip(jelly.x, 0, self.ocean_width)

            if jelly.y < 0 or jelly.y > self.ocean_height:
                jelly.vy = -jelly.vy
                jelly.y = np.clip(jelly.y, 0, self.ocean_height)

            # Random direction changes
            if np.random.random() < 0.01:  # 1% chance per update
                angle = np.random.uniform(0, 2 * np.pi)
                jelly.vx = np.cos(angle) * self.speed
                jelly.vy = np.sin(angle) * self.speed

    def check_collision(
        self,
        x: float,
        y: float,
        z: float,
        radius: float = 0.5
    ) -> bool:
        """
        Check if position collides with any jellyfish.

        Args:
            x: X position
            y: Y position
            z: Z position (depth, negative = underwater)
            radius: Collision radius

        Returns:
            True if collision detected
        """
        for jelly in self.jellyfish:
            # Only check if at similar depth
            if abs(z + jelly.z) < 1.0:  # Within 1m depth
                dx = x - jelly.x
                dy = y - jelly.y
                dist = np.sqrt(dx * dx + dy * dy)

                if dist < (radius + jelly.radius):
                    return True

        return False

    def get_nearest_jellyfish(
        self,
        x: float,
        y: float,
        max_distance: float = 10.0
    ) -> Tuple[float, float, float]:
        """
        Get relative position of nearest jellyfish.

        Args:
            x: X position
            y: Y position
            max_distance: Maximum distance to consider

        Returns:
            (dx, dy, distance) to nearest jellyfish, or (0, 0, max_distance) if none nearby
        """
        min_dist = max_distance
        nearest_dx = 0.0
        nearest_dy = 0.0

        for jelly in self.jellyfish:
            dx = jelly.x - x
            dy = jelly.y - y
            dist = np.sqrt(dx * dx + dy * dy)

            if dist < min_dist:
                min_dist = dist
                nearest_dx = dx
                nearest_dy = dy

        return nearest_dx, nearest_dy, min_dist

    def get_state_vector(self, x: float, y: float) -> np.ndarray:
        """
        Get jellyfish state relative to position for observation.

        Args:
            x: X position
            y: Y position

        Returns:
            State vector with nearest jellyfish info
        """
        dx, dy, dist = self.get_nearest_jellyfish(x, y)
        return np.array([dx, dy, dist], dtype=np.float32)

    def reset(self):
        """Reset jellyfish swarm."""
        self._spawn_jellyfish()
