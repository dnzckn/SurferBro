"""Test environment with PROPER ocean design - see everything work!"""

from surferbro.environments.surf_env import SurfEnvironment
import numpy as np
import time

print("="*60)
print("🏄 Testing with PROPER Ocean Design")
print("="*60)

# Create environment with PROPER ocean and rendering
env = SurfEnvironment(
    ocean_design="ocean_designs/proper_beach_ocean.json",
    render_mode="human"
)

print("\nProper ocean features:")
print("  ✓ Beach (sand) for starting")
print("  ✓ Shallow water (0-1.5m)")
print("  ✓ Wave zone (1.5-5m)")
print("  ✓ Deep ocean (5-15m)")
print("\nWatch for:")
print("  • Surfer starts near beach (shallow water)")
print("  • Waves spawn in deep water, move toward beach")
print("  • Surfer can swim (use arrow to move)")
print("\nRunning manual control demo...")
print("Close window or Ctrl+C to stop.\n")

try:
    obs, info = env.reset()

    print(f"Starting position: ({env.surfer.state.x:.1f}, {env.surfer.state.y:.1f})")
    print(f"Starting depth: {env.ocean_floor.get_depth(env.surfer.state.x, env.surfer.state.y):.2f}m")
    print("\nSwimming forward toward waves for 30 seconds...\n")

    start_time = time.time()
    step = 0

    while time.time() - start_time < 30:  # Run for 30 seconds
        # Action: swim forward at full power
        action = np.array([0.0, 1.0, 0.0, 0.0])  # [direction, power=max, no dive, -]

        obs, reward, terminated, truncated, info = env.step(action)
        env.render()
        time.sleep(0.03)  # ~30 FPS

        step += 1

        # Print status every 5 seconds
        if step % 150 == 0:
            elapsed = time.time() - start_time
            print(f"[{elapsed:.1f}s] Position: ({env.surfer.state.x:.1f}, {env.surfer.state.y:.1f}), "
                  f"Depth: {env.ocean_floor.get_depth(env.surfer.state.x, env.surfer.state.y):.2f}m, "
                  f"Waves: {len(env.wave_simulator.waves)}")

        if terminated or truncated:
            print("\nEpisode ended, resetting...")
            obs, info = env.reset()

    print(f"\n✓ Completed {step} steps")
    print(f"Final position: ({env.surfer.state.x:.1f}, {env.surfer.state.y:.1f})")
    print(f"Distance from start: {env.surfer.state.y - 10.5:.1f}m toward waves")

except KeyboardInterrupt:
    print("\n\nStopped by user.")

env.close()

print("\n" + "="*60)
print("WHAT YOU SHOULD HAVE SEEN:")
print("="*60)
print("✓ Surfer started near beach (bottom of screen)")
print("✓ Blue wave circles appearing from top, moving down")
print("✓ Surfer swimming upward (increasing y)")
print("✓ Surfer moving from shallow → deeper water")
print("\nIf you saw this, EVERYTHING WORKS!")
print("\nNext: Train an agent to learn this!")
print("  surferbro-train --ocean ocean_designs/proper_beach_ocean.json --timesteps 100000 --n-envs 4 --eval-freq 100000")
