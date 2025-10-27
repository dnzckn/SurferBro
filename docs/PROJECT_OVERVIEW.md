# SurferBro - Project Overview

## Architecture

SurferBro is a reinforcement learning environment where an AI agent learns to surf through physics simulation and reward optimization.

### Core Components

#### 1. OceanScope (Beach Designer)
- **Location**: `surferbro/oceanscope/`
- **Purpose**: HTML-based GUI for designing surf environments
- **Features**:
  - Interactive canvas for placing sand, ocean, and piers
  - Depth configuration for ocean floor
  - Mesh conversion for physics simulation
  - JSON export for reproducible environments

#### 2. Physics Engine
- **Location**: `surferbro/physics/`
- **Components**:
  - `ocean_floor.py`: Terrain topology and depth queries
  - `wave_simulator.py`: Advanced wave physics
    - Wave propagation based on depth
    - Breaking waves when depth/height ratio met
    - Whitewash simulation post-break
    - Pier interference modeling
    - Wave refraction

#### 3. RL Environment
- **Location**: `surferbro/environments/`
- **Standard**: Gymnasium-compatible
- **Components**:
  - `surf_env.py`: Main environment class
  - `surfer.py`: Surfer physics and controls
  - `jellyfish.py`: Obstacle system

**Three-Phase Gameplay**:

1. **Swimming Phase**
   - Navigate to wave zone
   - Control: direction, power, duck diving
   - Avoid jellyfish obstacles

2. **Wave Catching Phase**
   - Precise board orientation required
   - Control: roll, pitch, yaw, paddle power
   - Must match wave speed and direction

3. **Surfing Phase**
   - Balance on moving wave
   - Control: lean, turn
   - Maximize ride duration

#### 4. RL Training (PyTorch Backend)
- **Location**: `surferbro/training/`
- **Framework**: Stable-Baselines3 (uses PyTorch)
- **Algorithms**: PPO, SAC, TD3
- **Features**:
  - Multi-environment parallel training
  - Custom callbacks for surf metrics
  - TensorBoard integration
  - Checkpoint saving
  - GPU acceleration (CUDA)

#### 5. Visualization
- **Location**: `surferbro/visualization/`
- **Engine**: Pygame
- **Features**:
  - Real-time rendering
  - Camera follows surfer
  - Wave visualization (breaking, whitewash)
  - Jellyfish animation
  - HUD with state information

## Reward System

```python
rewards = {
    'reach_wave_zone': 100.0,      # One-time bonus
    'surfing_per_second': 10.0,    # Duration reward
    'wave_catch_success': 50.0,     # Successful catch
    'duck_dive_success': 5.0,       # Getting under wave
    'fall_penalty': -20.0,          # Wipeout
    'jellyfish_penalty': -10.0,     # Collision
    'time_penalty': -0.1,           # Efficiency incentive
    'speed_bonus': 0.1 * speed      # Distance traveled while surfing
}
```

## Observation Space (26-dimensional)

1. **Surfer State (15)**:
   - Position (x, y, z)
   - Velocity (vx, vy, vz)
   - Orientation (roll, pitch, yaw)
   - Angular velocity (roll_rate, pitch_rate, yaw_rate)
   - State flags (is_swimming, is_duck_diving, is_surfing)

2. **Wave Info (5)**:
   - Current wave height
   - Wave velocity (vx, vy)
   - Distance to nearest wave
   - Is wave breaking

3. **Jellyfish Info (3)**:
   - Relative position (dx, dy)
   - Distance to nearest jellyfish

4. **Environment Info (3)**:
   - Water depth
   - Distance to shore
   - In wave zone flag

## Action Space (4-dimensional, continuous)

Actions are interpreted based on current phase:

**Swimming**: [direction, power, duck_dive_trigger, yaw_adjust]
**Wave Catching**: [roll, pitch, yaw, paddle_power]
**Surfing**: [lean, turn, -, -]

All actions in range [-1, 1].

## Physics Simulation

### Wave Dynamics
- Deep water speed: `c = 1.56 * period`
- Shallow water speed: `c = sqrt(g * depth)`
- Breaking condition: `height > depth * 1.3`
- Refraction based on depth gradient

### Surfer Dynamics
- Mass-based momentum
- Drag forces
- Buoyancy
- Board orientation affects wave catching
- Balance stability in surfing phase

## Training Pipeline

```bash
# Single environment
surferbro-train --timesteps 1000000

# Multi-threaded (4x faster)
surferbro-train --n-envs 4 --timesteps 1000000

# Custom ocean + SAC algorithm
surferbro-train --ocean my_design.json --algorithm SAC --timesteps 500000
```

## File Structure

```
SurferBro/
├── surferbro/              # Main package
│   ├── oceanscope/        # Beach designer GUI
│   ├── physics/           # Wave & terrain physics
│   ├── environments/      # RL environment
│   ├── agents/            # Agent wrappers
│   ├── training/          # Training scripts
│   ├── visualization/     # Rendering
│   └── utils/             # Helpers
├── examples/              # Example scripts
├── tests/                 # Unit tests
├── assets/                # GUI resources
├── config.yaml           # Configuration
└── ocean_designs/        # Saved designs
```

## Technology Stack

- **Python 3.8+**
- **PyTorch 2.0+**: Neural network backend
- **Stable-Baselines3**: RL algorithms (PPO, SAC, TD3)
- **Gymnasium**: RL environment standard
- **NumPy/SciPy**: Numerical computation
- **PyBullet**: Physics simulation support
- **Pygame**: Visualization
- **Flask**: OceanScope web GUI
- **Trimesh**: Mesh processing

## Configuration

All parameters configurable in `config.yaml`:
- Wave characteristics
- Ocean dimensions
- Jellyfish density
- Reward weights
- Training hyperparameters
- Simulation timestep
- Rendering settings

## Performance Optimization

- Vectorized physics calculations
- Multi-process training environments
- GPU acceleration (PyTorch)
- Efficient depth map interpolation
- Spatial partitioning for obstacles

## Extensibility

Easy to extend:
- Add new obstacle types (sharks, rocks, etc.)
- Implement advanced wave types (rip currents, tides)
- Create custom reward shaping
- Add new RL algorithms
- Enhance visualization
- Multi-agent scenarios
