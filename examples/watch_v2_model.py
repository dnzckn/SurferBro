"""Watch the already-trained ultra_fast_model_v2"""

from surferbro.environments.surf_env import SurfEnvironment
from stable_baselines3 import SAC
import time

print("="*60)
print("🏄 Watching Ultra Fast Model V2")
print("="*60)

# Load the model
print("\nLoading model: ultra_fast_model_v2.zip")
model = SAC.load("ultra_fast_model_v2")
print("✓ Model loaded!")

# Create rendering environment
print("\nCreating environment with visualization...")
env = SurfEnvironment(
    ocean_design="ocean_designs/proper_beach_ocean.json",
    render_mode="human"
)
print("✓ Environment ready!\n")

print("="*60)
print("WATCHING 3 EPISODES")
print("="*60)
print("\nClose window or press Ctrl+C to stop.\n")

try:
    for episode in range(3):
        print(f"--- Episode {episode + 1}/3 ---")
        obs, info = env.reset()
        total_reward = 0
        steps = 0
        start_y = env.surfer.state.y
        max_y = start_y

        while steps < 500:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            steps += 1

            # Track max distance
            current_y = env.surfer.state.y
            if current_y > max_y:
                max_y = current_y

            env.render()
            time.sleep(0.03)

            if terminated or truncated:
                break

        distance = max_y - start_y

        print(f"  Reward: {total_reward:.2f}")
        print(f"  Steps: {steps}")
        print(f"  Distance toward waves: {distance:.1f}m")

        if episode < 2:
            time.sleep(2)

except KeyboardInterrupt:
    print("\n\nStopped by user.")

env.close()

print("\n" + "="*60)
print("Done! 🏄‍♂️")
print("="*60)
