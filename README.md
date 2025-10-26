# SurferBro - Reinforcement Learning Surfing Simulator

An advanced reinforcement learning environment where an AI agent learns to surf from complete noob to pro surfer through physical wave simulation and environmental interaction.

## Features

### OceanScope - Beach Designer
- Interactive HTML-based GUI for designing your surf environment
- Place sand beaches with custom topology
- Define ocean depth and floor contours
- Add piers and obstacles
- Real-time mesh generation for physics simulation

### Advanced Ocean Physics
- Realistic wave propagation and interference
- Wave direction, height, and front dynamics
- Post-crash whitewash simulation
- Depth-dependent wave behavior
- Pier interference modeling

### SurferBro RL Agent
The agent learns through three distinct phases:

1. **Swimming Phase**
   - Navigate to the wave zone
   - Control duck diving to get under waves
   - Avoid jellyfish obstacles
   - Directional control

2. **Wave Catching Phase**
   - Precise board orientation (roll, pitch, yaw)
   - Timing the paddle
   - Matching wave speed

3. **Surfing Phase**
   - Dynamic balance control
   - Ride along the wave face
   - Maximize ride duration
   - Avoid wipeouts

### Reward System
- Points for reaching the wave zone
- Duration-based surfing rewards
- Penalties for jellyfish encounters
- Bonus for advanced maneuvers

## Installation

### Prerequisites
- Python 3.8+
- pip

### Install from source
```bash
git clone <repository-url>
cd SurferBro
pip install -e .
```

### Install dependencies
```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Design Your Ocean
```bash
python -m surferbro.oceanscope
```
This launches the OceanScope GUI in your browser where you can design your beach environment.

### 2. Train SurferBro
```bash
python -m surferbro.train --ocean myocean.json --episodes 10000
```

### 3. Watch the Pro Surf
```bash
python -m surferbro.evaluate --model trained_models/surferbro_pro.zip --render
```

## Project Structure

```
SurferBro/
├── surferbro/
│   ├── oceanscope/       # Beach/ocean design GUI
│   ├── physics/          # Wave physics simulation
│   ├── environments/     # Gymnasium RL environment
│   ├── agents/           # RL agent implementations
│   ├── training/         # Training pipelines
│   ├── visualization/    # Rendering and viz
│   └── utils/            # Helper functions
├── examples/             # Example scripts
├── tests/                # Unit tests
└── assets/               # Static files and GUI resources
```

## Configuration

Environment parameters can be configured in `config.yaml`:
- Wave characteristics (height, period, direction)
- Ocean floor topology
- Jellyfish density and distribution
- Reward weights
- Agent physics parameters

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black surferbro/
flake8 surferbro/
```

## Technical Details

### Physics Engine
- Custom fluid dynamics for wave propagation
- Rigid body simulation for surfer and board
- Collision detection for obstacles

### RL Implementation
- Gymnasium-compatible environment
- Supports PPO, SAC, TD3 algorithms
- Multi-threaded training support
- TensorBoard integration

## Citation

If you use SurferBro in your research, please cite:
```
@software{surferbro2025,
  title={SurferBro: Reinforcement Learning Surfing Simulator},
  year={2025}
}
```

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.
