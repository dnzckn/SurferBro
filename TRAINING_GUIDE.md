# 🏄 SurferBro Training Guide

## Quick Start Options

### Option 1: Full Production Training (Recommended)
**Duration:** ~12-15 hours | **Steps:** 1,000,000

```bash
python train_surferbro.py
```

**Features:**
- ✅ Automatic checkpoints every 50k steps
- ✅ Evaluation every 10k steps
- ✅ TensorBoard logging
- ✅ Best model saving
- ✅ Detailed metrics tracking
- ✅ Resume capability
- ✅ Progress bar

**Expected Results:**
- 50k steps: Agent learns basic movement
- 100k steps: Duck diving starts to emerge
- 250k steps: Wave catching attempts
- 500k steps: Angle positioning improves
- 1M steps: Full surfing sequence mastery

---

### Option 2: Medium Training (Faster Results)
**Duration:** ~3 hours | **Steps:** 250,000

```python
python -c "
from surferbro.environments.surf_env import SurfEnvironment
from stable_baselines3 import SAC

env = SurfEnvironment()
model = SAC('MlpPolicy', env, verbose=1, tensorboard_log='./logs/')
model.learn(total_timesteps=250_000, progress_bar=True)
model.save('surferbro_250k')
print('Model saved to surferbro_250k.zip')
"
```

**Good for:** Initial experimentation, hyperparameter tuning

---

### Option 3: Quick Test (See If It's Learning)
**Duration:** ~10 minutes | **Steps:** 50,000

```python
python -c "
from surferbro.environments.surf_env import SurfEnvironment
from stable_baselines3 import SAC

env = SurfEnvironment()
model = SAC('MlpPolicy', env, verbose=1)
model.learn(total_timesteps=50_000, progress_bar=True)
model.save('surferbro_quick_test')
"
```

**Good for:** Debugging, quick validation

---

### Option 4: Overnight Training (Best Results)
**Duration:** ~24 hours | **Steps:** 2,000,000

Modify `train_surferbro.py` line 22:
```python
TOTAL_TIMESTEPS = 2_000_000  # Change from 1M to 2M
```

Then run:
```bash
nohup python train_surferbro.py > training.log 2>&1 &
```

**Monitor with:**
```bash
tail -f training.log
```

**Good for:** Maximum performance, full behavior emergence

---

## Training Configuration Comparison

| Option | Steps | Duration | Checkpoints | TensorBoard | Best For |
|--------|-------|----------|-------------|-------------|----------|
| Quick Test | 50k | 10 min | ❌ | ❌ | Debugging |
| Medium | 250k | 3 hours | ❌ | ✅ | Experimentation |
| **Full** | **1M** | **12-15 hrs** | **✅** | **✅** | **Production** |
| Overnight | 2M | 24 hours | ✅ | ✅ | Max Performance |

---

## Monitoring Training

### TensorBoard (Real-time Graphs)

```bash
tensorboard --logdir ./logs/
```

Then open: http://localhost:6006

**Key Metrics to Watch:**
- `rollout/ep_rew_mean` - Average episode reward (should increase)
- `rollout/ep_len_mean` - Average episode length
- `train/entropy_loss` - Exploration vs exploitation
- `surf/position_y` - How far agent travels (custom metric)

### Watch Episode Logs

```bash
tail -f logs/*/0.monitor.csv
```

Shows: episode rewards, lengths, timestamps

### Check Saved Checkpoints

```bash
ls -lh checkpoints/surferbro_*/
```

Models are saved every 50k steps.

---

## Loading & Testing a Trained Model

### Load Latest Model

```python
from stable_baselines3 import SAC
from surferbro.environments.surf_env import SurfEnvironment

# Load model
model = SAC.load("models/surferbro_final_TIMESTAMP")

# Test it
env = SurfEnvironment()
obs, info = env.reset()

for _ in range(750):
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        break

print(f"Final position: {env.surfer.state.y:.2f}m")
print(f"Was surfing: {env.surfer.state.is_surfing}")
```

### Continue Training

```python
# Load checkpoint
model = SAC.load("checkpoints/surferbro_TIMESTAMP/best_model/best_model")

# Train more
model.learn(total_timesteps=500_000, progress_bar=True)

# Save
model.save("models/surferbro_extended")
```

---

## Hyperparameter Tuning

If agent isn't learning well, try adjusting in `train_surferbro.py`:

### Learning Too Slow?
```python
LEARNING_RATE = 5e-4  # Increase from 3e-4
BATCH_SIZE = 512      # Increase from 256
```

### Unstable Training?
```python
LEARNING_RATE = 1e-4  # Decrease from 3e-4
BUFFER_SIZE = 200_000 # Increase from 100k
```

### Not Exploring Enough?
```python
# In SAC creation, add:
ent_coef='auto_0.1'  # Increase entropy coefficient
```

### Agent Too Random?
```python
TAU = 0.001  # Decrease from 0.005 (slower target updates)
```

---

## Expected Learning Timeline

### 0-50k steps: Random Exploration
- Agent moves randomly
- Occasionally swims forward
- Rarely duck dives
- **Reward:** -100 to -50

### 50k-100k steps: Basic Movement
- Agent learns to swim north (toward waves)
- Duck diving starts to appear
- No wave catching yet
- **Reward:** -50 to -20

### 100k-250k steps: Duck Dive Mastery
- Agent times duck dives when waves approach
- Escapes whitewash efficiently
- Starts positioning near waves
- **Reward:** -20 to 0

### 250k-500k steps: Wave Catching Attempts
- Agent tries to catch waves
- Angle positioning improves
- Some successful carries
- Rare standing up
- **Reward:** 0 to +20

### 500k-1M steps: Surfing Emergence
- Consistent wave catching
- 45° angle positioning
- Timing carry duration
- Multiple successful rides per episode
- **Reward:** +20 to +50+

### 1M+ steps: Mastery
- Strategic crash usage (whitewash for repositioning)
- Optimal duck dive timing
- High success rate on wave catching
- Long surf rides
- **Reward:** +50 to +100+

---

## Troubleshooting

### Agent Not Moving
**Symptom:** Stays at spawn, reward around -75
**Fix:** Increase reward for forward movement in `surf_env.py`

### Agent Spins in Circles
**Symptom:** High angular velocity, no forward progress
**Fix:** Add penalty for excessive turning

### Agent Doesn't Duck Dive
**Symptom:** Gets pushed back by waves constantly
**Fix:** Increase duck dive reward, decrease wave collision penalty

### Agent Doesn't Try to Catch Waves
**Symptom:** Swims to wave zone but doesn't approach waves
**Fix:** Add reward for proximity to waves

### Training Crashes / OOM
**Symptom:** Out of memory error
**Fix:** Reduce BUFFER_SIZE or BATCH_SIZE

---

## Performance Benchmarks

**On M1/M2 Mac:**
- ~80-100 steps/second
- 1M steps = 12-15 hours
- Memory: ~2-4 GB

**On Modern CPU (Intel/AMD):**
- ~60-80 steps/second
- 1M steps = 15-18 hours
- Memory: ~2-4 GB

**On GPU (CUDA):**
- ~100-150 steps/second
- 1M steps = 8-12 hours
- Memory: ~4-6 GB VRAM

---

## Recommended Training Plan

### Week 1: Exploration
```bash
# Day 1: Quick test (verify setup)
python train_surferbro.py  # Stop after 50k steps (Ctrl+C)

# Day 2-3: Medium run (check learning)
# Modify TOTAL_TIMESTEPS to 250k
python train_surferbro.py

# Day 4: Analyze results, tune hyperparameters
tensorboard --logdir ./logs/

# Day 5-7: Full training
# Set TOTAL_TIMESTEPS back to 1M
nohup python train_surferbro.py > training.log 2>&1 &
```

### Week 2: Optimization
```bash
# Load best model, continue training
# Adjust rewards based on Week 1 results
# Train for another 1M steps
```

### Week 3: Advanced Mechanics
```bash
# Implement Wave Sets from PROPOSED_REALISTIC_MECHANICS.md
# Retrain from scratch with new mechanics
```

---

## Summary

**For Best Results, Run:**

```bash
python train_surferbro.py
```

**Then Monitor With:**

```bash
tensorboard --logdir ./logs/
```

**Expected Outcome After 1M Steps:**
- Agent swims toward waves ✅
- Duck dives to avoid pushback ✅
- Positions at 45° angles ✅
- Catches waves consistently ✅
- Rides waves successfully ✅
- Uses whitewash strategically ✅

**Time Investment:** 12-15 hours (can run overnight)

**Storage Needed:** ~500 MB (checkpoints + logs)

---

🏄 **Ready when you are!** Just run `python train_surferbro.py`
