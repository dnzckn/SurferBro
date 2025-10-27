"""Test with FIXED visualization - see beach, waves, and movement!"""

import json
from surferbro.environments.surf_env import SurfEnvironment
from surferbro.visualization.renderer_fixed import SurfRendererFixed
import numpy as np
import time

print("="*60)
print("🏄 FIXED VISUALIZATION TEST")
print("="*60)
print("\nFixes:")
print("  ✓ Beach/sand now visible (tan color at bottom)")
print("  ✓ Surfer 3x bigger (actually visible!)")
print("  ✓ Waves 3x bigger (white circles)")
print("  ✓ Reference grid (shows movement)")
print("  ✓ Fixed camera (see whole map)")
print("\nLook for:")
print("  • TAN BEACH at bottom of screen")
print("  • BLUE OCEAN gradient (shallow→deep)")
print("  • WHITE WAVE CIRCLES moving down")
print("  • BIG RED SURFER at bottom")
print("  • GRID LINES for reference")
print()

# Load ocean design with full data
with open("ocean_designs/proper_beach_ocean.json", 'r') as f:
    ocean_design = json.load(f)

# Create environment
env = SurfEnvironment(ocean_design="ocean_designs/proper_beach_ocean.json")

# Create FIXED renderer with ocean design data
renderer = SurfRendererFixed(
    ocean_floor=env.ocean_floor,
    ocean_design_data=ocean_design,
    camera_mode="fixed"  # Show whole map!
)

print("Starting visualization...")
print("Surfer will swim forward for 30 seconds.\n")
print("Watch the surfer move UP the screen (toward waves)!")
print("Close window or Ctrl+C to stop.\n")

try:
    obs, info = env.reset()

    print(f"Start position: ({env.surfer.state.x:.1f}, {env.surfer.state.y:.1f})")
    print(f"Start depth: {env.ocean_floor.get_depth(env.surfer.state.x, env.surfer.state.y):.2f}m\n")

    start_time = time.time()
    step = 0

    while time.time() - start_time < 30:
        # Swim forward
        action = np.array([0.0, 1.0, 0.0, 0.0])  # Full power forward

        obs, reward, terminated, truncated, info = env.step(action)
        step += 1

        # Render with FIXED renderer
        renderer.render(
            surfer=env.surfer,
            wave_simulator=env.wave_simulator,
            jellyfish_swarm=env.jellyfish_swarm,
            mode="human"
        )

        time.sleep(0.03)

        # Status update
        if step % 150 == 0:
            print(f"[{step} steps] Pos: ({env.surfer.state.x:.1f}, {env.surfer.state.y:.1f}), "
                  f"Depth: {env.ocean_floor.get_depth(env.surfer.state.x, env.surfer.state.y):.2f}m, "
                  f"Waves: {len(env.wave_simulator.waves)}")

        if terminated or truncated:
            print("Episode ended, resetting...")
            obs, info = env.reset()

    final_pos = (env.surfer.state.x, env.surfer.state.y)
    distance = final_pos[1] - 10.5

    print(f"\n✓ Completed {step} steps")
    print(f"Final position: {final_pos}")
    print(f"Distance traveled: {distance:.1f}m toward waves")

except KeyboardInterrupt:
    print("\n\nStopped by user.")

renderer.close()
env.close()

print("\n" + "="*60)
print("WHAT YOU SHOULD HAVE SEEN:")
print("="*60)
print("✓ TAN BEACH at bottom of screen")
print("✓ BLUE OCEAN getting darker toward top")
print("✓ GRID LINES every 10m")
print("✓ BIG RED SURFER moving UP")
print("✓ WHITE WAVE CIRCLES from top moving DOWN")
print("\nIf you saw this, EVERYTHING IS FIXED!")
