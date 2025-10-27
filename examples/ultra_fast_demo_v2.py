"""ULTRA FAST v2 - With proper ocean and auto-visualization!"""

from surferbro.environments.surf_env import SurfEnvironment
from stable_baselines3 import SAC
from stable_baselines3.common.vec_env import DummyVecEnv
import time
import numpy as np

print("="*60)
print("🏄 ULTRA FAST DEMO V2 - Complete Workflow!")
print("="*60)
print("\n1. Train for 2 minutes")
print("2. Auto-visualize the results")
print("3. See if agent learned anything!")
print("\n✨ Using PROPER ocean with beach!\n")

# Environment with proper ocean
def make_env():
    return SurfEnvironment(ocean_design="ocean_designs/proper_beach_ocean.json")

env = DummyVecEnv([make_env])

print("Creating SAC agent...")
model = SAC(
    "MlpPolicy",
    env,
    learning_rate=0.0003,
    buffer_size=10000,
    learning_starts=100,
    batch_size=64,
    verbose=1,
)

print("\n" + "="*60)
print("TRAINING (10,000 steps, ~2 minutes)")
print("="*60 + "\n")

start_time = time.time()

try:
    model.learn(total_timesteps=10000, progress_bar=True)

    elapsed = time.time() - start_time
    print(f"\n✅ Training done in {elapsed:.1f} seconds!")

    # Save
    model.save("ultra_fast_model_v2")
    print("Model saved: ultra_fast_model_v2.zip")

    env.close()

    # Now visualize!
    print("\n" + "="*60)
    print("VISUALIZATION - Watch What It Learned!")
    print("="*60)
    print("\nOpening visualization window...\n")
    time.sleep(2)

    # Create rendering environment
    render_env = SurfEnvironment(
        ocean_design="ocean_designs/proper_beach_ocean.json",
        render_mode="human"
    )

    print("Running 2 episodes...\n")

    for episode in range(2):
        print(f"--- Episode {episode + 1}/2 ---")
        obs, info = render_env.reset()
        total_reward = 0
        steps = 0
        max_y = obs[1]  # Track how far toward waves

        while steps < 500:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = render_env.step(action)  # Fixed: use render_env!
            total_reward += reward
            steps += 1

            # Track progress
            if obs[1] > max_y:
                max_y = obs[1]

            render_env.render()
            time.sleep(0.03)

            if terminated or truncated:
                break

        start_y = 10.5  # Approximate start
        distance = max_y - start_y

        print(f"  Reward: {total_reward:.2f}")
        print(f"  Steps: {steps}")
        print(f"  Max distance toward waves: {distance:.1f}m")

        if episode < 1:
            time.sleep(2)

    render_env.close()

    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)

    if distance > 5:
        print("🎉 Agent learned to swim toward waves!")
        print(f"   Moved {distance:.1f}m from starting point")
    elif distance > 2:
        print("📊 Agent shows some learning!")
        print(f"   Moved {distance:.1f}m from starting point")
        print("   Train longer for better results")
    else:
        print("📉 Not much learning yet")
        print("   10k steps is very short - try 100k!")

    print("\nFor better results:")
    print("  surferbro-train --ocean ocean_designs/proper_beach_ocean.json --timesteps 100000 --n-envs 4 --eval-freq 100000")

except KeyboardInterrupt:
    print("\n\nInterrupted!")
    env.close()

print("\n🏄‍♂️ Demo complete!")
