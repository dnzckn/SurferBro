# SurferBro Quick Start Commands

## 🚀 Fast Demo Options

### Option 1: 5-Minute Super Quick Demo
```bash
./super_quick_demo.sh
```
- 25,000 timesteps
- SAC algorithm (learns faster)
- Auto-evaluates when done

### Option 2: 10-Minute Quick Demo  
```bash
./quick_demo.sh
```
- 50,000 timesteps
- PPO algorithm
- Auto-evaluates when done

### Option 3: Python Quick Demo
```bash
python examples/quick_demo.py
```
- 25,000 timesteps
- Simple Python script
- Shows test results

## 📊 Full Training Options

### Short Training (45 minutes)
```bash
surferbro-train --ocean ocean_designs/ocean_design_20251026_150514.json --timesteps 250000 --n-envs 4
```

### Standard Training (3-4 hours)
```bash
surferbro-train --ocean ocean_designs/ocean_design_20251026_150514.json --timesteps 1000000 --n-envs 4
```

### Long Training (overnight, best results)
```bash
surferbro-train --ocean ocean_designs/ocean_design_20251026_150514.json --timesteps 2000000 --n-envs 4
```

## 🎮 Evaluation

### Watch Trained Agent
```bash
# Find your model
ls trained_models/

# Watch it surf
surferbro-evaluate --model trained_models/surferbro_PPO_*/best_model/best_model.zip --render --episodes 5
```

### Slow Motion
```bash
surferbro-evaluate --model trained_models/surferbro_PPO_*/best_model/best_model.zip --render --render-delay 0.05 --episodes 3
```

## 📈 Monitoring

### TensorBoard
```bash
tensorboard --logdir=logs/
# Open http://localhost:6006
```

### Check Running Training
```bash
ps aux | grep surferbro-train
```

## 🛑 Stop Training

```bash
# In the training terminal: Ctrl+C

# Or kill the process:
pkill -f surferbro-train
```

## 🌊 OceanScope Designer

```bash
python -m surferbro.oceanscope
# Opens in browser at http://127.0.0.1:5000
```

## ✅ Verify Installation

```bash
python verify_installation.py
```

## 📝 Test Environment

```bash
python examples/test_environment.py
```

---

## 🎯 Recommended First-Time Workflow

1. **Quick test** (5 min): `./super_quick_demo.sh`
2. **Watch results**: Auto-runs after demo
3. **If looks good, longer training** (overnight): 
   ```bash
   surferbro-train --ocean ocean_designs/ocean_design_20251026_150514.json --timesteps 1000000 --n-envs 4
   ```
4. **Monitor**: `tensorboard --logdir=logs/`
5. **Evaluate**: `surferbro-evaluate --model trained_models/.../best_model.zip --render`

Happy surfing! 🏄‍♂️🌊
