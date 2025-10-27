"""COMPLETE QUICK DEMO - Train and watch with FIXED visualization!"""

import json
import time
import numpy as np
from surferbro.environments.surf_env import SurfEnvironment
from surferbro.visualization.renderer_fixed import SurfRendererFixed
from stable_baselines3 import SAC
from stable_baselines3.common.vec_env import DummyVecEnv

print("="*60)
print("🏄 COMPLETE QUICK DEMO - Fixed Visualization!")
print("="*60)
print("\n1. Train agent (10k steps, ~2 min)")
print("2. Watch it surf with FIXED renderer")
print("\nAll the fixes:")
print("  ✓ Beach/sand visible")
print("  ✓ Big surfer (3x size)")
print("  ✓ Big waves (3x size)")
print("  ✓ Grid for reference")
print("  ✓ Fixed camera\n")

# Train
print("="*60)
print("STEP 1: TRAINING (2 minutes)")
print("="*60 + "\n")

env = DummyVecEnv([lambda: SurfEnvironment(
    ocean_design="ocean_designs/proper_beach_ocean.json"
)])

model = SAC("MlpPolicy", env, verbose=1)

start = time.time()
model.learn(total_timesteps=10000, progress_bar=True)
elapsed = time.time() - start

print(f"\n✅ Trained in {elapsed:.1f}s!")
model.save("quick_demo_fixed")
env.close()

# Watch
print("\n" + "="*60)
print("STEP 2: WATCHING (with FIXED renderer)")
print("="*60 + "\n")

time.sleep(2)

# Load ocean design with full data
with open("ocean_designs/proper_beach_ocean.json", 'r') as f:
    ocean_design = json.load(f)

# Create environment
watch_env = SurfEnvironment(ocean_design="ocean_designs/proper_beach_ocean.json")

# Create FIXED renderer
renderer = SurfRendererFixed(
    ocean_floor=watch_env.ocean_floor,
    ocean_design_data=ocean_design,
    camera_mode="fixed"
)

print("Running 2 episodes with FIXED visualization...\n")

try:
    for episode in range(2):
        print(f"--- Episode {episode + 1}/2 ---")
        obs, info = watch_env.reset()
        total_reward = 0
        steps = 0
        start_y = watch_env.surfer.state.y
        max_y = start_y

        while steps < 500:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = watch_env.step(action)
            total_reward += reward
            steps += 1

            current_y = watch_env.surfer.state.y
            if current_y > max_y:
                max_y = current_y

            # Render with FIXED renderer
            renderer.render(
                surfer=watch_env.surfer,
                wave_simulator=watch_env.wave_simulator,
                jellyfish_swarm=watch_env.jellyfish_swarm,
                mode="human"
            )

            time.sleep(0.03)

            if terminated or truncated:
                break

        distance = max_y - start_y

        print(f"  Reward: {total_reward:.2f}")
        print(f"  Steps: {steps}")
        print(f"  Distance toward waves: {distance:.1f}m")

        if episode < 1:
            time.sleep(2)

except KeyboardInterrupt:
    print("\n\nStopped.")

renderer.close()
watch_env.close()

print("\n" + "="*60)
print("DEMO COMPLETE! 🏄‍♂️")
print("="*60)
print("\nYou should have seen:")
print("  ✓ TAN BEACH at bottom")
print("  ✓ BIG RED SURFER")
print("  ✓ WHITE WAVE CIRCLES")
print("  ✓ GRID LINES")
print("  ✓ Surfer moving UP")
