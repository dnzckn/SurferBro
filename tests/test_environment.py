"""Tests for the surfing environment."""

import pytest
import numpy as np
from surferbro.environments.surf_env import SurfEnvironment


def test_environment_creation():
    """Test that environment can be created."""
    env = SurfEnvironment()
    assert env is not None
    env.close()


def test_environment_reset():
    """Test environment reset."""
    env = SurfEnvironment()
    obs, info = env.reset()

    assert obs is not None
    assert isinstance(obs, np.ndarray)
    assert obs.shape == env.observation_space.shape
    assert info is not None
    assert isinstance(info, dict)

    env.close()


def test_environment_step():
    """Test environment step."""
    env = SurfEnvironment()
    env.reset()

    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)

    assert isinstance(obs, np.ndarray)
    assert isinstance(reward, (int, float))
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)
    assert isinstance(info, dict)

    env.close()


def test_action_space():
    """Test action space."""
    env = SurfEnvironment()

    assert env.action_space.shape == (4,)
    assert env.action_space.low[0] == -1.0
    assert env.action_space.high[0] == 1.0

    env.close()


def test_observation_space():
    """Test observation space."""
    env = SurfEnvironment()

    expected_dim = 15 + 5 + 3 + 3  # As defined in environment
    assert env.observation_space.shape == (expected_dim,)

    env.close()


def test_episode_termination():
    """Test that episodes can terminate."""
    env = SurfEnvironment()
    env.reset()

    max_steps = 10000
    for _ in range(max_steps):
        action = env.action_space.sample()
        _, _, terminated, truncated, _ = env.step(action)

        if terminated or truncated:
            break

    # Episode should either terminate or truncate
    assert terminated or truncated

    env.close()
