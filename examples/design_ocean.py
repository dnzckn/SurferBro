"""Example: Design ocean using OceanScope and test it."""

import sys
from pathlib import Path

# Run OceanScope
print("="*60)
print("Step 1: Design Your Ocean")
print("="*60)
print("\nLaunching OceanScope GUI...")
print("Design your beach and ocean, then export the design.")
print()

from surferbro.oceanscope.app import main as oceanscope_main

try:
    oceanscope_main()
except KeyboardInterrupt:
    print("\nOceanScope closed.")

# After design is created, test it
print("\n" + "="*60)
print("Step 2: Test Your Ocean Design")
print("="*60)

design_dir = Path('ocean_designs')
if design_dir.exists():
    designs = list(design_dir.glob('*.json'))
    if designs:
        latest_design = max(designs, key=lambda p: p.stat().st_mtime)
        print(f"\nUsing latest design: {latest_design.name}")

        from surferbro.environments.surf_env import SurfEnvironment

        env = SurfEnvironment(ocean_design=str(latest_design), render_mode="human")

        print("Running test episode with random actions...")
        obs, info = env.reset()

        for _ in range(500):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            env.render()

            if terminated or truncated:
                break

        env.close()
        print("\nTest complete!")
    else:
        print("\nNo designs found. Please create one using OceanScope first.")
else:
    print("\nNo designs directory found. Please create a design using OceanScope first.")
