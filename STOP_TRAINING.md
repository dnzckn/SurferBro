# How to Stop Current Training

Your training is currently running. Here's how to stop it:

## Option 1: In the Terminal Running Training

Press `Ctrl + C` in the terminal where training is running.

## Option 2: Kill the Process

```bash
# Find the process
ps aux | grep surferbro-train

# Kill it (replace XXXXX with the process ID)
kill XXXXX
```

Or use this one-liner:
```bash
pkill -f surferbro-train
```

## Option 3: Activity Monitor (macOS GUI)

1. Open Activity Monitor
2. Search for "surferbro-train" or "python"
3. Select the process and click "Force Quit"

---

## After Stopping, Run Quick Demo

Choose one:

### 1️⃣ Super Quick (5 minutes)
```bash
./super_quick_demo.sh
```

### 2️⃣ Quick (10 minutes)
```bash
./quick_demo.sh
```

### 3️⃣ Python Quick Demo (5 minutes)
```bash
python examples/quick_demo.py
```

### 4️⃣ Manual Quick Training
```bash
surferbro-train --ocean ocean_designs/ocean_design_20251026_150514.json --timesteps 50000 --n-envs 4
```

---

## Recommended Approach

For your first test, I recommend:

```bash
# 1. Stop current training (Ctrl+C in that terminal)

# 2. Run super quick demo
./super_quick_demo.sh

# 3. Watch it learn in 5 minutes!
```

Then later, run a longer training overnight for better results:
```bash
surferbro-train --ocean ocean_designs/ocean_design_20251026_150514.json --timesteps 500000 --n-envs 4
```
