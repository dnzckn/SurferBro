# SurferBro Quick Start Guide

Get started with SurferBro in 3 easy steps!

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd SurferBro

# Install dependencies
pip install -e .
```

## Step 1: Design Your Ocean (Optional)

Launch the OceanScope GUI to design your custom surf environment:

```bash
python -m surferbro.oceanscope
```

Or use the command:
```bash
surferbro-oceanscope
```

- Use the Sand tool to create beaches
- Use the Ocean tool to define depths (adjust with slider)
- Use the Pier tool to add obstacles
- Click "Export Design" when done

Your design will be saved in `ocean_designs/` directory.

## Step 2: Train Your Agent

Train SurferBro to surf using PPO (PyTorch backend):

```bash
# Basic training with default ocean
surferbro-train --timesteps 1000000

# Train with your custom ocean
surferbro-train --ocean ocean_designs/ocean_design_20250126_120000.json --timesteps 1000000

# Use SAC algorithm instead
surferbro-train --algorithm SAC --timesteps 500000

# Multi-threaded training (4 parallel environments)
surferbro-train --n-envs 4 --timesteps 1000000
```

Monitor training with TensorBoard:
```bash
tensorboard --logdir=logs/
```

## Step 3: Watch Your Pro Surfer!

Evaluate and visualize your trained agent:

```bash
# Watch the agent surf
surferbro-evaluate --model trained_models/surferbro_PPO_*/best_model/best_model.zip --render --episodes 5

# Slow-motion rendering
surferbro-evaluate --model trained_models/your_model.zip --render --render-delay 0.03
```

## Testing the Environment

Test the environment with random actions:

```bash
python examples/test_environment.py
```

## Quick Training Example

For a quick demo training session:

```bash
python examples/basic_training.py
```

This runs a short 100k step training session to verify everything works.

## Tips for Best Results

1. **Training Time**: For a competent surfer, train for at least 1-2 million timesteps
2. **Algorithm Choice**:
   - PPO: Good all-around, stable
   - SAC: Better for continuous control, may learn faster
   - TD3: Alternative to SAC
3. **Parallel Environments**: Use `--n-envs 4` or more to speed up training significantly
4. **GPU**: If you have CUDA, PyTorch will automatically use it for faster training

## Next Steps

- Experiment with different ocean designs
- Tune reward parameters in `config.yaml`
- Try different RL algorithms
- Create your own training callbacks
- Extend the environment with new obstacles

## Troubleshooting

**Import errors**: Make sure you installed with `pip install -e .`

**Pygame display issues**: Set `SDL_VIDEODRIVER=x11` on Linux if needed

**Training too slow**: Use more parallel environments with `--n-envs`

**Agent not learning**: Try increasing timesteps, adjusting learning rate, or checking reward configuration

## Have Fun!

Watch your SurferBro evolve from a total noob to a gnarly wave rider! 🏄‍♂️🌊
