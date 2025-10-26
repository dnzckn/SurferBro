# Fast Training Without Evaluation Delays

The `--eval-freq` parameter causes training to pause for evaluation.
This makes it LOOK stuck but it's actually running eval episodes.

## Solution: Train Without Evaluation

### Option 1: Ultra Fast Demo (2 min, no waiting)
```bash
python examples/ultra_fast_demo.py
```
- 10,000 steps
- No evaluation callbacks
- No pauses
- Completes in ~2 minutes

### Option 2: Manual Training Without Eval
```bash
surferbro-train \
  --ocean ocean_designs/ocean_design_20251026_150514.json \
  --timesteps 50000 \
  --n-envs 4 \
  --algorithm SAC \
  --save-freq 50000 \
  --eval-freq 50000
```
Setting eval-freq to 50000 means it only evaluates at the end!

### Option 3: Minimal Test First (30 sec)
```bash
python examples/minimal_test.py
```
Just verifies the environment works, no training.

## What's Happening When It "Hangs"

When you see training pause at 20k/25k steps:
1. It hits the eval checkpoint (--eval-freq 5000)
2. Runs 5 full evaluation episodes (30-60 sec)
3. Saves best model if improved
4. Resumes training

**IT'S NOT STUCK** - just running evaluation!

## Recommended Fast Workflow

```bash
# 1. Quick environment test (30 sec)
python examples/minimal_test.py

# 2. Ultra fast training (2 min)
python examples/ultra_fast_demo.py

# 3. If that works, longer training without frequent eval
surferbro-train \
  --ocean ocean_designs/ocean_design_20251026_150514.json \
  --timesteps 100000 \
  --n-envs 4 \
  --eval-freq 100000
```

This way you see results FAST, then can do longer training later!
