"""QUICK WAVE TEST - See waves spawn and surfer movement in 15 seconds"""

import json
import time
import numpy as np
from surferbro.environments.surf_env import SurfEnvironment
from surferbro.visualization.renderer_fixed import SurfRendererFixed

print("="*60)
print("🌊 QUICK WAVE TEST - 15 seconds")
print("="*60)
print("\nChanges:")
print("  ✓ Wave period: 3 seconds (was 8)")
print("  ✓ Small ocean (25m x 15m)")
print("  ✓ Surfer faces NORTH (90°)")
print("\nWatch for:")
print("  • Surfer moving UP (toward waves)")
print("  • White wave circles spawning every 3 seconds")
print("  • Waves moving DOWN toward beach")
print()

# Load small ocean
with open("ocean_designs/small_beach_ocean.json", 'r') as f:
    ocean_design = json.load(f)

env = SurfEnvironment(ocean_design="ocean_designs/small_beach_ocean.json")
renderer = SurfRendererFixed(
    ocean_floor=env.ocean_floor,
    ocean_design_data=ocean_design,
    camera_mode="fixed"
)

obs, info = env.reset()

print(f"Start: ({env.surfer.state.x:.1f}, {env.surfer.state.y:.1f})")
print(f"Facing: {np.degrees(env.surfer.state.yaw):.0f}° (90°=North ✓)")
print(f"Ocean: {env.ocean_floor.get_dimensions()[0]:.0f}m x {env.ocean_floor.get_dimensions()[1]:.0f}m")
print(f"\nSwimming forward... Watch the screen!")
print("(Close window or Ctrl+C to stop)\n")

start_y = env.surfer.state.y
wave_spawns = []

try:
    for step in range(450):  # 15 seconds at 30fps
        # Swim forward
        action = np.array([0.0, 1.0, 0.0, 0.0])
        obs, reward, terminated, truncated, info = env.step(action)

        # Track wave spawns
        current_wave_count = len(env.wave_simulator.waves)
        if current_wave_count > len(wave_spawns):
            wave = env.wave_simulator.waves[-1]
            wave_spawns.append(step)
            elapsed = step * env.dt
            print(f"  ⚡ Wave #{current_wave_count} at {elapsed:.1f}s! Position: ({wave.position[0]:.1f}, {wave.position[1]:.1f})")

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
    print("\nStopped by user")

end_y = env.surfer.state.y
distance = end_y - start_y

renderer.close()
env.close()

print("\n" + "="*60)
print("RESULTS")
print("="*60)
print(f"Distance moved: {distance:.1f}m {'UP ✓' if distance > 0 else 'WRONG ✗'}")
print(f"Waves spawned: {len(wave_spawns)}")
if len(wave_spawns) >= 2:
    intervals = np.diff([s * env.dt for s in wave_spawns])
    print(f"Wave intervals: {intervals} (should be ~3s)")
    print(f"Average: {np.mean(intervals):.1f}s")

if distance > 2 and len(wave_spawns) > 0:
    print("\n✅ SUCCESS! Movement and waves working correctly!")
else:
    if distance < 2:
        print(f"\n⚠️  Surfer barely moved ({distance:.1f}m)")
    if len(wave_spawns) == 0:
        print("⚠️  No waves spawned")
