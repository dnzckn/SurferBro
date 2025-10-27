"""Test new wave front system - 3 phases, horizontal lines"""

import json
import time
import numpy as np
from surferbro.environments.surf_env import SurfEnvironment
from surferbro.visualization.renderer_fixed import SurfRendererFixed

print("="*70)
print("🌊 WAVE FRONT TEST - New 3-Phase System")
print("="*70)
print("\nNew Wave System:")
print("  ✓ Wave fronts (horizontal lines) instead of circles")
print("  ✓ 3 phases:")
print("    1. BUILDING (dashed light blue) - growing, not rideable")
print("    2. FRONT (bright cyan) - rideable sweet spot!")
print("    3. WHITEWASH (white foam) - broken wave")
print("\nWatch for:")
print("  • Waves spawn at top as DASHED LINES (building)")
print("  • Transform to BRIGHT CYAN (rideable front!)")
print("  • Break into WHITE FOAM (whitewash)")
print("  • All waves move DOWN toward beach as a front")
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
print(f"Surfer start: ({env.surfer.state.x:.1f}, {env.surfer.state.y:.1f})\n")

phase_changes = []
waves_seen = set()

try:
    for step in range(900):  # 30 seconds at 30fps
        # Swim forward slowly to watch waves
        action = np.array([0.0, 0.5, 0.0, 0.0])
        obs, reward, terminated, truncated, info = env.step(action)

        # Track wave phases
        for i, wave in enumerate(env.wave_simulator.waves):
            wave_id = id(wave)
            if wave_id not in waves_seen:
                waves_seen.add(wave_id)
                print(f"  Wave #{len(waves_seen)} spawned at Y={wave.y_position:.1f}m - BUILDING phase")

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
print("TEST COMPLETE")
print("="*70)
print(f"\nWaves spawned: {len(waves_seen)}")
print("\nWhat you should have seen:")
print("  ✓ Horizontal wave fronts (not circles!)")
print("  ✓ Dashed light blue lines appearing at top (BUILDING)")
print("  ✓ Transforming to solid bright cyan (FRONT - rideable!)")
print("  ✓ All advancing downward as fronts toward beach")
print("  ✓ Eventually becoming white foam (WHITEWASH)")
print("\n🏄 If you saw horizontal lines advancing down, SUCCESS!")
