"""Tests for physics components."""

import pytest
import numpy as np
from surferbro.physics.ocean_floor import OceanFloor
from surferbro.physics.wave_simulator import WaveSimulator


def test_ocean_floor_creation():
    """Test ocean floor creation."""
    depth_map = np.random.rand(100, 100) * 10
    floor = OceanFloor(depth_map)

    assert floor is not None
    assert floor.width == 100
    assert floor.height == 100


def test_ocean_floor_depth_query():
    """Test depth queries."""
    depth_map = np.ones((100, 100)) * 5.0
    floor = OceanFloor(depth_map, cell_size=1.0)

    depth = floor.get_depth(50.0, 50.0)
    assert abs(depth - 5.0) < 0.1


def test_wave_simulator_creation():
    """Test wave simulator creation."""
    depth_map = np.ones((100, 100)) * 10.0
    floor = OceanFloor(depth_map)

    wave_sim = WaveSimulator(floor)

    assert wave_sim is not None
    assert wave_sim.wave_period == 8.0


def test_wave_spawning():
    """Test that waves are spawned."""
    depth_map = np.ones((100, 100)) * 10.0
    floor = OceanFloor(depth_map)

    wave_sim = WaveSimulator(floor, wave_period=1.0)

    # Step forward in time
    for _ in range(150):
        wave_sim.step(0.01)

    # Should have spawned at least one wave
    assert len(wave_sim.waves) > 0


def test_wave_height_query():
    """Test wave height queries."""
    depth_map = np.ones((100, 100)) * 10.0
    floor = OceanFloor(depth_map)

    wave_sim = WaveSimulator(floor)
    wave_sim.step(1.0)

    height = wave_sim.get_wave_height_at(25.0, 25.0)
    assert isinstance(height, float)
    assert height >= 0.0
