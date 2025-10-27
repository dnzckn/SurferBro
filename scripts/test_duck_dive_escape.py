"""Quick test of duck dive escape from whitewash."""

import numpy as np
from surferbro.environments.surf_env import SurfEnvironment

print("="*70)
print("TESTING: Duck Dive Escape from Whitewash")
print("="*70)
print()

env = SurfEnvironment()
obs, info = env.reset()

print("Step 1: Force surfer into surfing state, then cause wipeout...")
env.surfer.state.is_surfing = True
env.surfer.state.is_swimming = False
env.surfer.state.roll = np.pi / 2  # Excessive roll = wipeout

# Run a step to trigger wipeout check
action = np.zeros(7, dtype=np.float32)
obs, reward, terminated, truncated, info = env.step(action)

print(f"  After crash:")
print(f"    Terminated: {terminated}")
print(f"    Is whitewash carry: {env.surfer.state.is_whitewash_carry}")
print()

if not env.surfer.state.is_whitewash_carry:
    print("❌ FAILED: Crash didn't start whitewash carry!")
    exit(1)

print("Step 2: Trigger duck dive (action[2] = 1.0)...")
action = np.array([0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0], dtype=np.float32)
obs, reward, terminated, truncated, info = env.step(action)

print(f"  After duck dive:")
print(f"    Is whitewash carry: {env.surfer.state.is_whitewash_carry}")
print(f"    Is duck diving: {env.surfer.state.is_duck_diving}")
print(f"    Is swimming: {env.surfer.state.is_swimming}")
print(f"    Duck dive timer: {env.surfer.state.duck_dive_timer:.2f}s")
print()

if env.surfer.state.is_duck_diving and not env.surfer.state.is_whitewash_carry and env.surfer.state.is_swimming:
    print("✅ SUCCESS! Duck dive escaped whitewash carry!")
    print()
    print("Expected behavior:")
    print("  - is_whitewash_carry: False ✓")
    print("  - is_duck_diving: True ✓")
    print("  - is_swimming: True ✓")
    print("  - duck_dive_timer: ~3.0s ✓")
else:
    print("❌ FAILED! Duck dive should escape whitewash!")
    print()
    print("Expected vs Actual:")
    print(f"  is_whitewash_carry: False vs {env.surfer.state.is_whitewash_carry}")
    print(f"  is_duck_diving: True vs {env.surfer.state.is_duck_diving}")
    print(f"  is_swimming: True vs {env.surfer.state.is_swimming}")
    print(f"  duck_dive_timer: ~3.0 vs {env.surfer.state.duck_dive_timer:.2f}")

env.close()
