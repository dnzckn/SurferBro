"""Watch your trained model surf!"""

import sys
from surferbro.environments.surf_env import SurfEnvironment
from stable_baselines3 import SAC
import time

print("="*60)
print("🏄 Watching Your Trained SurferBro!")
print("="*60)

# Load the model
print("\nLoading model: ultra_fast_model.zip")
try:
    model = SAC.load("ultra_fast_model")
    print("✓ Model loaded!")
except:
    print("❌ Model not found. Make sure ultra_fast_demo.py finished.")
    sys.exit(1)

# Create environment with rendering
print("\nCreating environment with visualization...")
env = SurfEnvironment(
    ocean_design="ocean_designs/ocean_design_20251026_150514.json",
    render_mode="human"
)
print("✓ Environment ready!")

print("\n" + "="*60)
print("WATCHING 3 EPISODES")
print("="*60)
print("\nClose the window or press Ctrl+C to stop.\n")

try:
    for episode in range(3):
        print(f"\n--- Episode {episode + 1}/3 ---")
        obs, info = env.reset()
        total_reward = 0
        steps = 0
        max_surf_time = 0

        while steps < 1000:
            # Get action from trained model
            action, _states = model.predict(obs, deterministic=True)

            # Step environment
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            steps += 1

            # Track surf time
            if info.get('total_surf_time', 0) > max_surf_time:
                max_surf_time = info['total_surf_time']

            # Render
            env.render()
            time.sleep(0.03)  # Slow down slightly for viewing

            if terminated or truncated:
                print(f"Episode ended: {steps} steps")
                break

        print(f"  Reward: {total_reward:.2f}")
        print(f"  Max Surf Time: {max_surf_time:.2f}s")
        print(f"  Surfer Position: ({info['surfer_position'][0]:.1f}, {info['surfer_position'][1]:.1f})")

        if episode < 2:
            print("\nStarting next episode in 2 seconds...")
            time.sleep(2)

except KeyboardInterrupt:
    print("\n\nStopped by user.")

env.close()

print("\n" + "="*60)
print("Done watching! 🏄‍♂️")
print("="*60)
print("\nWhat you should see:")
print("  • Agent moves (even if randomly)")
print("  • Better than completely random")
print("  • For REAL surfing, train 100k+ steps")
print("\nNext step:")
print("  surferbro-train --timesteps 100000 --n-envs 4 --eval-freq 100000")
