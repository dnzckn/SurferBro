"""Test angled wave fronts - realistic wave directions!"""

import json
import time
import numpy as np
from surferbro.environments.surf_env import SurfEnvironment
from surferbro.visualization.renderer_fixed import SurfRendererFixed

print("="*70)
print("🌊 ANGLED WAVE FRONTS - Realistic Wave Directions!")
print("="*70)
print("\nNEW Realistic Wave System:")
print("  ✓ Waves come from DIFFERENT ANGLES (not just straight)")
print("  ✓ Each wave: ±30° variation (210° to 300°)")
print("  ✓ Covers NW → N → NE approaching shore")
print("  ✓ Yellow arrows show direction of travel")
print("  ✓ Wave front = LINE perpendicular to direction")
print("\nWhat makes this realistic:")
print("  • Ocean swells approach at angles based on wind")
print("  • Coastline shape affects wave direction")
print("  • Surfer must match board angle to wave direction!")
print("\nWatch for:")
print("  • ANGLED wave fronts (not horizontal!)")
print("  • Yellow arrows showing travel direction")
print("  • Different angles each wave")
print("  • All advancing toward beach (bottom)")
print("\nRunning 30 second test...")
print("Close window or Ctrl+C to stop\n")

# Load ocean
with open("ocean_designs/small_beach_ocean.json", 'r') as f:
    ocean_design = json.load(f)

env = SurfEnvironment(ocean_design="ocean_designs/small_beach_ocean.json")
renderer = SurfRendererFixed(
    ocean_floor=env.ocean_floor,
    ocean_design_data=ocean_design,
    camera_mode="fixed"
)

obs, info = env.reset()

print(f"Ocean: {env.ocean_floor.get_dimensions()[0]:.0f}m x {env.ocean_floor.get_dimensions()[1]:.0f}m")
print(f"Wave period: 3s")
print(f"Surfer start: ({env.surfer.state.x:.1f}, {env.surfer.state.y:.1f})")
print(f"Surfer facing: {np.degrees(env.surfer.state.yaw):.0f}° (90°=North)\n")

wave_directions = []

try:
    for step in range(900):  # 30 seconds at 30fps
        # Swim forward slowly
        action = np.array([0.0, 0.5, 0.0, 0.0])
        obs, reward, terminated, truncated, info = env.step(action)

        # Track wave directions
        for wave in env.wave_simulator.waves:
            wave_id = id(wave)
            if wave_id not in [id(w) for _, w in wave_directions]:
                angle_deg = np.degrees(wave.direction)
                wave_directions.append((wave_id, wave))
                print(f"  Wave #{len(wave_directions)}: direction={angle_deg:.1f}° "
                      f"(from {'NW' if angle_deg < -255 else 'N' if angle_deg < -285 else 'NE'})")

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

renderer.close()
env.close()

print("\n" + "="*70)
print("TEST COMPLETE - Angled Waves")
print("="*70)
print(f"\nWaves spawned: {len(wave_directions)}")

if wave_directions:
    angles = [np.degrees(w.direction) for _, w in wave_directions]
    print(f"Direction range: {min(angles):.1f}° to {max(angles):.1f}°")
    print(f"Average direction: {np.mean(angles):.1f}°")
    print(f"Variation: {np.std(angles):.1f}° std dev")

print("\nWhat you should have seen:")
print("  ✓ ANGLED wave fronts (not just horizontal!)")
print("  ✓ Yellow arrows showing direction")
print("  ✓ Different angles for each wave")
print("  ✓ All moving toward beach (bottom)")
print("  ✓ Beach at bottom (tan color)")
print("\n🏄 This is much more realistic and challenging!")
print("   Surfer must align with wave angle to catch it!")
