"""Ocean floor representation for wave physics."""

import numpy as np
from typing import Tuple, Optional


class OceanFloor:
    """Represents the ocean floor topology and provides depth queries."""

    def __init__(self, depth_map: np.ndarray, cell_size: float = 0.5):
        """
        Initialize ocean floor.

        Args:
            depth_map: 2D array of depths (positive values)
            cell_size: Size of each grid cell in meters
        """
        self.depth_map = depth_map
        self.cell_size = cell_size
        self.height, self.width = depth_map.shape

    def get_depth(self, x: float, y: float) -> float:
        """
        Get depth at a specific (x, y) position using bilinear interpolation.

        Args:
            x: X coordinate in meters
            y: Y coordinate in meters

        Returns:
            Depth in meters (positive value)
        """
        # Convert to grid coordinates
        gx = x / self.cell_size
        gy = y / self.cell_size

        # Bounds check
        if gx < 0 or gx >= self.width - 1 or gy < 0 or gy >= self.height - 1:
            return 0.0

        # Get integer and fractional parts
        ix, iy = int(gx), int(gy)
        fx, fy = gx - ix, gy - iy

        # Bilinear interpolation
        d00 = self.depth_map[iy, ix]
        d10 = self.depth_map[iy, ix + 1]
        d01 = self.depth_map[iy + 1, ix]
        d11 = self.depth_map[iy + 1, ix + 1]

        d0 = d00 * (1 - fx) + d10 * fx
        d1 = d01 * (1 - fx) + d11 * fx

        return d0 * (1 - fy) + d1 * fy

    def get_gradient(self, x: float, y: float) -> Tuple[float, float]:
        """
        Get depth gradient (slope) at a position.

        Args:
            x: X coordinate in meters
            y: Y coordinate in meters

        Returns:
            (dx, dy) depth gradients
        """
        epsilon = 0.1
        depth = self.get_depth(x, y)
        depth_dx = self.get_depth(x + epsilon, y)
        depth_dy = self.get_depth(x, y + epsilon)

        return (depth_dx - depth) / epsilon, (depth_dy - depth) / epsilon

    def is_shore(self, x: float, y: float, threshold: float = 0.3) -> bool:
        """
        Check if position is at the shore (shallow water).

        Args:
            x: X coordinate
            y: Y coordinate
            threshold: Depth threshold for shore

        Returns:
            True if at shore
        """
        return self.get_depth(x, y) < threshold

    def get_dimensions(self) -> Tuple[float, float]:
        """
        Get ocean dimensions in meters.

        Returns:
            (width, height) in meters
        """
        return self.width * self.cell_size, self.height * self.cell_size
