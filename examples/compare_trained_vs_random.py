"""Compare your trained agent vs random actions"""

from surferbro.environments.surf_env import SurfEnvironment
from stable_baselines3 import SAC
import time

print("="*60)
print("🏄 TRAINED vs RANDOM COMPARISON")
print("="*60)

# Load model
model = SAC.load("ultra_fast_model")

# Create environment with rendering
env = SurfEnvironment(
    ocean_design="ocean_designs/ocean_design_20251026_150514.json",
    render_mode="human"
)

def run_episode(use_model=True, max_steps=500):
    """Run one episode."""
    obs, info = env.reset()
    total_reward = 0
    steps = 0

    while steps < max_steps:
        if use_model:
            action, _ = model.predict(obs, deterministic=True)
        else:
            action = env.action_space.sample()  # Random

        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        steps += 1

        env.render()
        time.sleep(0.02)

        if terminated or truncated:
            break

    return total_reward, steps, info

# Run random agent
print("\n" + "="*60)
print("1. RANDOM AGENT (baseline)")
print("="*60)
print("Watch the surfer thrash randomly...\n")
time.sleep(2)

random_reward, random_steps, random_info = run_episode(use_model=False)

print(f"\nRandom Results:")
print(f"  Reward: {random_reward:.2f}")
print(f"  Steps: {random_steps}")
print(f"  Surf Time: {random_info.get('total_surf_time', 0):.2f}s")

# Run trained agent
print("\n" + "="*60)
print("2. TRAINED AGENT (your model)")
print("="*60)
print("Watch your trained agent...\n")
time.sleep(2)

trained_reward, trained_steps, trained_info = run_episode(use_model=True)

print(f"\nTrained Results:")
print(f"  Reward: {trained_reward:.2f}")
print(f"  Steps: {trained_steps}")
print(f"  Surf Time: {trained_info.get('total_surf_time', 0):.2f}s")

# Comparison
print("\n" + "="*60)
print("COMPARISON")
print("="*60)
improvement = ((trained_reward - random_reward) / abs(random_reward) * 100) if random_reward != 0 else 0
print(f"Reward Improvement: {improvement:+.1f}%")
print(f"Random:  {random_reward:.2f}")
print(f"Trained: {trained_reward:.2f}")

if trained_reward > random_reward:
    print("\n🎉 Your agent learned something!")
    print("   It's better than random!")
else:
    print("\n📊 Agent is still learning...")
    print("   10k steps isn't much. Try 100k steps!")

env.close()

print("\n💡 For better results:")
print("   surferbro-train --timesteps 100000 --n-envs 4 --eval-freq 100000")
