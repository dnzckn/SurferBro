"""Test the SurferBro environment with random actions."""

import numpy as np
from surferbro.environments.surf_env import SurfEnvironment

# Create environment with rendering
print("Creating SurferBro environment...")
env = SurfEnvironment(render_mode="human")

print("\nRunning random agent for 5 episodes...")
print("Watch the surfer try random actions!\n")

for episode in range(5):
    obs, info = env.reset()
    total_reward = 0
    steps = 0

    print(f"Episode {episode + 1}/5")

    while steps < 1000:
        # Random action
        action = env.action_space.sample()

        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        steps += 1

        # Render
        env.render()

        if terminated or truncated:
            break

    print(f"  Steps: {steps}")
    print(f"  Reward: {total_reward:.2f}")
    print(f"  Surf Time: {info.get('total_surf_time', 0):.2f}s")
    print()

env.close()
print("Done!")
