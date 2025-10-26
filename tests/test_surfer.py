"""Tests for surfer physics."""

import pytest
import numpy as np
from surferbro.environments.surfer import Surfer, SurferState


def test_surfer_creation():
    """Test surfer creation."""
    surfer = Surfer()

    assert surfer is not None
    assert surfer.mass == 75.0
    assert isinstance(surfer.state, SurferState)


def test_surfer_reset():
    """Test surfer reset."""
    surfer = Surfer()
    surfer.reset((10.0, 20.0))

    assert surfer.state.x == 10.0
    assert surfer.state.y == 20.0
    assert surfer.state.is_swimming is True


def test_swimming_action():
    """Test swimming controls."""
    surfer = Surfer()
    surfer.reset((0.0, 0.0))

    surfer.apply_swimming_action(
        swim_direction=0.0,
        swim_power=1.0,
        duck_dive=False,
        dt=0.1
    )

    # Should have some velocity
    speed = np.sqrt(surfer.state.vx**2 + surfer.state.vy**2)
    assert speed > 0


def test_duck_diving():
    """Test duck diving."""
    surfer = Surfer()
    surfer.reset((0.0, 0.0))

    surfer.apply_swimming_action(
        swim_direction=0.0,
        swim_power=0.5,
        duck_dive=True,
        dt=0.1
    )

    assert surfer.state.is_duck_diving is True


def test_surfer_observation():
    """Test observation vector."""
    surfer = Surfer()
    surfer.reset((5.0, 10.0))

    obs = surfer.get_observation()

    assert isinstance(obs, np.ndarray)
    assert obs.shape == (15,)
    assert obs[0] == 5.0  # x position
    assert obs[1] == 10.0  # y position
