# Getting Started with SurferBro

This guide will walk you through creating your first trained surfing AI from scratch!

## Prerequisites

- Python 3.8 or higher
- pip package manager
- (Optional) CUDA-capable GPU for faster training

## Installation

### 1. Clone and Install

```bash
git clone <your-repo-url>
cd SurferBro
pip install -e .
```

### 2. Verify Installation

```bash
python verify_installation.py
```

You should see ✓ checkmarks for all components.

## Your First Surfing AI

### Option A: Quick Start (5 minutes)

Use the default ocean and train a basic agent:

```bash
# Run basic training example (100k steps, ~5 minutes)
python examples/basic_training.py
```

This will:
- Create the default ocean environment
- Train a PPO agent for 100k timesteps
- Save the model as `surferbro_basic_demo.zip`
- Run a test episode

### Option B: Full Custom Workflow (30-60 minutes)

#### Step 1: Design Your Ocean (5-10 minutes)

```bash
python -m surferbro.oceanscope
```

Or use the command:
```bash
surferbro-oceanscope
```

In the OceanScope GUI:
1. **Create the beach**: Use the Sand tool (🏖️) to paint a beach area
2. **Define the ocean**:
   - Use the Ocean tool (🌊)
   - Adjust the depth slider (0-20m)
   - Paint deeper water as you move away from shore
3. **Add a pier** (optional): Use the Pier tool (🏗️)
4. **Export**: Click "💾 Export Design"

Your design will be saved in `ocean_designs/ocean_design_YYYYMMDD_HHMMSS.json`

**Tips for Good Designs:**
- Create a gradual slope from beach to deep water
- Wave zone is typically 2-15m depth
- Piers add interesting dynamics but increase difficulty

#### Step 2: Train Your Agent (20-40 minutes)

Train with your custom ocean:

```bash
# Find your design file
ls ocean_designs/

# Train with it (example filename)
surferbro-train \
  --ocean ocean_designs/ocean_design_20250126_143000.json \
  --algorithm PPO \
  --timesteps 1000000 \
  --n-envs 4
```

**Training Parameters:**
- `--ocean`: Your ocean design file (omit for default)
- `--algorithm`: PPO (stable), SAC (faster learning), or TD3
- `--timesteps`: Total training steps (1M = ~20-30 min with 4 envs)
- `--n-envs`: Parallel environments (4 = ~4x faster)
- `--save-freq`: Checkpoint frequency (default: 10000)

**Monitor Training:**

In another terminal, start TensorBoard:
```bash
tensorboard --logdir=logs/
```

Open http://localhost:6006 to see:
- Reward curves
- Surf time metrics
- Wave catches
- Episode lengths

**What to Expect:**
- **First 100k steps**: Random thrashing, occasional swimming
- **100k-300k steps**: Learns to swim, starts avoiding jellyfish
- **300k-600k steps**: Reaches wave zone, attempts wave catching
- **600k-1M steps**: Successfully catches waves, improves surfing
- **1M+ steps**: Consistent wave riding, longer surf times

#### Step 3: Watch Your Pro Surfer! (5 minutes)

```bash
# Find your model
ls trained_models/

# Watch it surf
surferbro-evaluate \
  --model trained_models/surferbro_PPO_*/best_model/best_model.zip \
  --render \
  --episodes 5
```

**Evaluation Options:**
- `--render`: Show visualization
- `--episodes`: Number of episodes to run
- `--render-delay 0.03`: Slow motion effect
- `--deterministic`: Use deterministic policy (default: True)

## Understanding the Visualization

When watching your agent:

**Surfer Colors:**
- 🔴 Red circle: Surfer position
- Yellow rectangle: Surfboard
- White line: Facing direction

**Wave Indicators:**
- Blue circles: Unbroken waves
- White circles: Breaking/whitewash waves
- Larger radius = taller wave

**Jellyfish:**
- 🌸 Pink pulsing circles with tentacles

**Status Text:**
- "SURFING!" (green): Successfully riding a wave
- "DIVE" (blue): Duck diving under a wave

**HUD (top-left):**
- Position in the ocean
- Current velocity
- Swimming vs Surfing state
- Board orientation (Roll, Pitch, Yaw)
- Number of active waves

## Common Training Scenarios

### Scenario 1: Testing the Waters
```bash
# Quick test with default settings
surferbro-train --timesteps 100000 --n-envs 1
```
*Use this to verify everything works before longer training.*

### Scenario 2: Standard Training
```bash
# Good balance of speed and performance
surferbro-train --timesteps 1000000 --n-envs 4 --algorithm PPO
```
*Recommended for first real training run.*

### Scenario 3: Fast Learning
```bash
# SAC often learns faster
surferbro-train --timesteps 500000 --n-envs 8 --algorithm SAC
```
*Try if PPO seems slow to learn.*

### Scenario 4: Maximum Quality
```bash
# Long training for expert performance
surferbro-train --timesteps 5000000 --n-envs 4 --algorithm PPO
```
*Run overnight for best results.*

## Troubleshooting

### Agent not learning to swim
- **Increase timesteps**: Try 2-3M instead of 1M
- **Check rewards**: Jellyfish penalty might be too high
- **Simplify ocean**: Use default ocean first

### Agent swims but doesn't catch waves
- **Wave alignment is hard**: This is normal, needs 500k+ steps
- **Try SAC**: Sometimes learns wave catching faster
- **Check ocean design**: Make sure wave zone is accessible

### Training is slow
- **Increase `--n-envs`**: Try 8 or 16 parallel environments
- **Use GPU**: PyTorch will auto-use CUDA if available
- **Check CPU usage**: Should be 100% * n_envs

### Visualization is laggy
- **Reduce render delay**: Use `--render-delay 0`
- **Check pygame**: Update to latest version
- **Disable rendering during training**: Only render for evaluation

## Next Steps

1. **Experiment with ocean designs**: Different depths, pier placements
2. **Tune rewards**: Edit `config.yaml` to emphasize different behaviors
3. **Try different algorithms**: Compare PPO vs SAC vs TD3
4. **Analyze with TensorBoard**: Understand learning curves
5. **Extend the environment**: Add new obstacles, wave types

## Configuration Tips

Edit `config.yaml` to customize:

**Make waves easier:**
```yaml
waves:
  base_height: 1.0  # Smaller waves
  period: 10.0      # Slower waves
```

**Reduce jellyfish difficulty:**
```yaml
jellyfish:
  count: 5          # Fewer jellyfish
  speed: 0.1        # Slower movement
```

**Emphasize wave riding:**
```yaml
rewards:
  surfing_per_second: 20.0  # Double reward for surfing
  wave_catch_success: 100.0  # Higher catch bonus
```

## Performance Benchmarks

On a modern laptop (4-core CPU):
- **1 environment**: ~500 steps/sec
- **4 environments**: ~1500 steps/sec
- **8 environments**: ~2500 steps/sec

With GPU (training neural network):
- **PPO**: ~2000-3000 steps/sec (4 envs)
- **SAC**: ~1500-2500 steps/sec (4 envs)

Time to 1M steps:
- **4 envs**: ~15-20 minutes
- **8 envs**: ~10-15 minutes

## Have Fun!

You're now ready to train your own SurferBro! Remember:
- Be patient - learning to surf takes time (even for AI!)
- Monitor TensorBoard to see progress
- Experiment with different settings
- Share your best trained agents!

Happy surfing! 🏄‍♂️🌊
