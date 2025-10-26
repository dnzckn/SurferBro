"""Convert OceanScope designs to physics meshes."""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import trimesh


class OceanMeshConverter:
    """Converts OceanScope 2D designs to 3D meshes for physics simulation."""

    def __init__(self, design_file: str):
        """
        Initialize mesh converter.

        Args:
            design_file: Path to OceanScope JSON design file
        """
        with open(design_file, 'r') as f:
            self.design = json.load(f)

        self.width = self.design['width']
        self.height = self.design['height']
        self.grid_size = self.design['gridSize']
        self.grid = self.design['grid']

    def create_ocean_floor_mesh(self) -> trimesh.Trimesh:
        """
        Create a 3D mesh of the ocean floor from the 2D design.

        Returns:
            Trimesh object representing the ocean floor
        """
        vertices = []
        faces = []

        # Convert grid to 3D vertices
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]

                # Default elevation is 0 (water level)
                if cell['type'] == 'sand':
                    # Sand is above water
                    z = 0.5  # meters above water
                elif cell['type'] == 'ocean':
                    # Ocean floor depth
                    z = -cell['depth']
                elif cell['type'] == 'pier':
                    # Pier pillars
                    z = 2.0  # meters above water
                else:
                    z = 0.0

                # Scale x, y to real-world coordinates
                real_x = x * 0.5  # 0.5 meters per grid cell
                real_y = y * 0.5

                vertices.append([real_x, real_y, z])

        # Create faces (triangles) from grid
        for y in range(self.height - 1):
            for x in range(self.width - 1):
                # Two triangles per quad
                v1 = y * self.width + x
                v2 = y * self.width + (x + 1)
                v3 = (y + 1) * self.width + x
                v4 = (y + 1) * self.width + (x + 1)

                faces.append([v1, v2, v3])
                faces.append([v2, v4, v3])

        vertices = np.array(vertices)
        faces = np.array(faces)

        return trimesh.Trimesh(vertices=vertices, faces=faces)

    def get_depth_map(self) -> np.ndarray:
        """
        Get 2D array of ocean depths.

        Returns:
            2D numpy array of depths (positive values)
        """
        depth_map = np.zeros((self.height, self.width))

        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell['type'] == 'ocean':
                    depth_map[y, x] = cell['depth']

        return depth_map

    def get_pier_positions(self) -> List[Tuple[float, float]]:
        """
        Get positions of pier pillars.

        Returns:
            List of (x, y) coordinates for piers
        """
        piers = []

        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if cell['type'] == 'pier':
                    real_x = x * 0.5
                    real_y = y * 0.5
                    piers.append((real_x, real_y))

        return piers

    def get_beach_line(self) -> np.ndarray:
        """
        Get the beach/water interface line.

        Returns:
            Array of (x, y) coordinates defining the beach edge
        """
        beach_points = []

        for y in range(self.height):
            for x in range(self.width - 1):
                cell = self.grid[y][x]
                next_cell = self.grid[y][x + 1]

                # Check for sand-ocean boundary
                if cell['type'] == 'sand' and next_cell['type'] == 'ocean':
                    real_x = (x + 0.5) * 0.5
                    real_y = y * 0.5
                    beach_points.append([real_x, real_y])

        return np.array(beach_points) if beach_points else np.array([])

    def export_mesh(self, output_path: str, format: str = 'obj'):
        """
        Export mesh to file.

        Args:
            output_path: Output file path
            format: File format ('obj', 'stl', 'ply')
        """
        mesh = self.create_ocean_floor_mesh()
        mesh.export(output_path, file_type=format)

    def get_simulation_data(self) -> Dict:
        """
        Get all data needed for physics simulation.

        Returns:
            Dictionary containing mesh, depth map, pier positions, etc.
        """
        return {
            'mesh': self.create_ocean_floor_mesh(),
            'depth_map': self.get_depth_map(),
            'pier_positions': self.get_pier_positions(),
            'beach_line': self.get_beach_line(),
            'dimensions': {
                'width': self.width * 0.5,
                'height': self.height * 0.5
            }
        }


def load_ocean_design(design_file: str) -> OceanMeshConverter:
    """
    Load ocean design from file.

    Args:
        design_file: Path to design JSON file

    Returns:
        OceanMeshConverter instance
    """
    return OceanMeshConverter(design_file)
