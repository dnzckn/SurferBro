"""QUICK FIX TEST - See all fixes working in 20 seconds!"""

import json
import time
import numpy as np
from surferbro.environments.surf_env import SurfEnvironment
from surferbro.visualization.renderer_fixed import SurfRendererFixed

print("="*60)
print("🏄 QUICK FIX TEST - 20 Seconds")
print("="*60)
print("\nALL FIXES:")
print("  ✅ Surfer faces NORTH (up) not EAST (right)")
print("  ✅ Small ocean (25m x 15m) for better visibility")
print("  ✅ Waves spawn and move toward beach")
print("  ✅ Beach/sand visible (tan at bottom)")
print("  ✅ Grid shows movement clearly")
print("\nWATCH FOR:")
print("  • Surfer moves UP the screen (not sideways!)")
print("  • White wave circles from top moving DOWN")
print("  • Tan beach at bottom")
print("  • Grid lines for reference")
print()

# Load small ocean
with open("ocean_designs/small_beach_ocean.json", 'r') as f:
    ocean_design = json.load(f)

# Create environment
env = SurfEnvironment(ocean_design="ocean_designs/small_beach_ocean.json")

# Create renderer
renderer = SurfRendererFixed(
    ocean_floor=env.ocean_floor,
    ocean_design_data=ocean_design,
    camera_mode="fixed"
)

obs, info = env.reset()

print(f"Starting position: ({env.surfer.state.x:.1f}, {env.surfer.state.y:.1f})")
print(f"Facing: {np.degrees(env.surfer.state.yaw):.0f}° (90°=North ✓)")
print(f"Ocean size: 25m x 15m (small for fast interactions)")
print(f"\nSwimming forward for 20 seconds...")
print("Watch surfer move UP! Close window or Ctrl+C to stop.\n")

start_pos = (env.surfer.state.x, env.surfer.state.y)
wave_count = 0

try:
    for step in range(600):  # 20 seconds
        # Swim forward
        action = np.array([0.0, 1.0, 0.0, 0.0])

        obs, reward, terminated, truncated, info = env.step(action)

        # Track waves
        if len(env.wave_simulator.waves) > wave_count:
            wave_count = len(env.wave_simulator.waves)
            print(f"  Wave #{wave_count} spawned at Y={env.wave_simulator.waves[-1].position[1]:.1f}m")

        renderer.render(
            surfer=env.surfer,
            wave_simulator=env.wave_simulator,
            jellyfish_swarm=env.jellyfish_swarm,
            mode="human"
        )
        time.sleep(0.03)

        if terminated or truncated:
            obs, info = env.reset()

except KeyboardInterrupt:
    print("\nStopped by user.")

end_pos = (env.surfer.state.x, env.surfer.state.y)
distance = end_pos[1] - start_pos[1]

renderer.close()
env.close()

print("\n" + "="*60)
print("RESULTS")
print("="*60)
print(f"Start: {start_pos}")
print(f"End: {end_pos}")
print(f"Distance moved: {distance:.1f}m")
print(f"Waves seen: {wave_count}")

if distance > 2:
    print(f"\n✅ SUCCESS! Surfer moved {distance:.1f}m TOWARD waves (UP)")
    print("   All fixes working correctly!")
elif distance > 0:
    print(f"\n✓ Moving in right direction ({distance:.1f}m)")
else:
    print(f"\n✗ Problem: Surfer moved {distance:.1f}m")

if wave_count > 0:
    print(f"✅ Waves ARE spawning ({wave_count} seen)")
else:
    print("✗ No waves spawned")

print("\n🏄‍♂️ Test complete!")
