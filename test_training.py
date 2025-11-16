"""
Quick training test for wave-catching mechanics.

Runs a short training session to verify everything works with Stable Baselines3.
"""

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from surferbro.environments.surf_env import SurfEnvironment

print("🌊 Testing Training with New Wave-Catching Mechanics")
print("=" * 60)

# Create environment
print("Creating environment...")
env = SurfEnvironment(render_mode=None)

# Check environment
print("Checking environment compatibility...")
try:
    check_env(env, warn=True)
    print("✓ Environment passes Gymnasium checks")
except Exception as e:
    print(f"✗ Environment check failed: {e}")
    exit(1)

# Create PPO agent
print("\nCreating PPO agent...")
model = PPO(
    "MlpPolicy",
    env,
    verbose=1,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    ent_coef=0.01,
    tensorboard_log="./tensorboard_logs/"
)

print("✓ PPO agent created successfully")
print(f"  Policy architecture: MLP")
print(f"  Action space: {env.action_space.shape}")
print(f"  Observation space: {env.observation_space.shape}")

# Quick training test (just 1000 steps to verify it works)
print("\nRunning quick training test (1000 steps)...")
print("This will verify the agent can learn with the new mechanics")
print("-" * 60)

try:
    model.learn(total_timesteps=1000, progress_bar=True)
    print("-" * 60)
    print("✓ Training completed successfully!")
except Exception as e:
    print(f"✗ Training failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test trained model
print("\nTesting trained model...")
obs, info = env.reset()
total_reward = 0
for step in range(20):
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    total_reward += reward

    if step == 0:
        print(f"  Step {step}: reward={reward:.3f}, position=({info['surfer_position'][0]:.1f}, {info['surfer_position'][1]:.1f})")

    if terminated or truncated:
        break

print(f"✓ Model can generate actions and step environment")
print(f"  Total reward over {step+1} steps: {total_reward:.2f}")

print("\n" + "=" * 60)
print("✅ Training test passed!")
print("\nReady for full training with:")
print("  • 7D action space (swim_x, swim_y, rotate, duck_dive, stand_up, lean, turn)")
print("  • 32D observation space (with angle information)")
print("  • Angle-based wave-catching mechanics")
print("  • Realistic surfing physics")
print("\nTo train for real, increase timesteps to 100K-1M+")
