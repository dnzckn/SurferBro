"""Minimal test - Just verify the environment works, 30 seconds"""

from surferbro.environments.surf_env import SurfEnvironment
import numpy as np

print("="*60)
print("🏄 Minimal Environment Test - 30 seconds")
print("="*60)
print("\nJust testing that everything works...\n")

# Create environment
print("1. Creating environment...")
env = SurfEnvironment(
    ocean_design="ocean_designs/ocean_design_20251026_150514.json"
)
print("   ✓ Environment created")

# Reset
print("\n2. Resetting environment...")
obs, info = env.reset()
print(f"   ✓ Observation shape: {obs.shape}")
print(f"   ✓ Action space: {env.action_space.shape}")

# Run random actions
print("\n3. Running 100 random steps...")
total_reward = 0
for i in range(100):
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    total_reward += reward

    if terminated or truncated:
        print(f"   Episode ended at step {i}")
        obs, info = env.reset()

print(f"   ✓ Completed 100 steps")
print(f"   Total reward: {total_reward:.2f}")

# Test with simple policy
print("\n4. Testing simple forward policy...")
obs, info = env.reset()
total_reward = 0

for i in range(100):
    # Simple policy: always swim forward
    action = np.array([0.0, 1.0, 0.0, 0.0])  # [direction, power, duck_dive, yaw]
    obs, reward, terminated, truncated, info = env.step(action)
    total_reward += reward

    if terminated or truncated:
        break

print(f"   ✓ Simple policy reward: {total_reward:.2f}")
print(f"   Surfer position: ({info['surfer_position'][0]:.1f}, {info['surfer_position'][1]:.1f})")

env.close()

print("\n" + "="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\nYour environment is working correctly!")
print("\nNext steps:")
print("  1. python examples/ultra_fast_demo.py  (2 min)")
print("  2. surferbro-train --timesteps 100000   (10 min)")
print("  3. surferbro-train --timesteps 500000   (45 min)")
