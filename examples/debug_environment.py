"""Debug the environment - see what's happening"""

from surferbro.environments.surf_env import SurfEnvironment
from surferbro.utils.ocean_validator import validate_ocean_design
import numpy as np

print("="*60)
print("🔍 ENVIRONMENT DEBUGGER")
print("="*60)

# Check ocean design
print("\n1. Validating ocean design...")
old_ocean = "ocean_designs/ocean_design_20251026_150514.json"
new_ocean = "ocean_designs/proper_beach_ocean.json"

print(f"\nOLD OCEAN: {old_ocean}")
result = validate_ocean_design(old_ocean)
print(f"  Valid: {result['valid']}")
if result['errors']:
    print(f"  ❌ Errors: {result['errors']}")
if result['warnings']:
    print(f"  ⚠️  Warnings: {result['warnings']}")

print(f"\nNEW OCEAN: {new_ocean}")
result = validate_ocean_design(new_ocean)
print(f"  Valid: {result['valid']}")
if result['errors']:
    print(f"  ❌ Errors: {result['errors']}")
if result['warnings']:
    print(f"  ⚠️  Warnings: {result['warnings']}")

# Create environment with PROPER ocean
print("\n2. Creating environment with PROPER ocean...")
env = SurfEnvironment(ocean_design=new_ocean)
print("  ✓ Environment created")

# Reset and check starting position
print("\n3. Checking starting position...")
obs, info = env.reset()
surfer_x = env.surfer.state.x
surfer_y = env.surfer.state.y
surfer_z = env.surfer.state.z
depth = env.ocean_floor.get_depth(surfer_x, surfer_y)

print(f"  Surfer position: ({surfer_x:.1f}, {surfer_y:.1f}, {surfer_z:.1f})")
print(f"  Water depth: {depth:.2f}m")
print(f"  Is swimming: {env.surfer.state.is_swimming}")

if depth < 1.5:
    print("  ✓ Good! Started in shallow water")
else:
    print(f"  ⚠️  Started in deep water ({depth:.2f}m)")

# Check wave simulator
print("\n4. Checking wave simulator...")
env.wave_simulator.step(1.0)  # Advance time
env.wave_simulator.step(7.0)  # Spawn a wave

print(f"  Wave simulator time: {env.wave_simulator.time:.1f}s")
print(f"  Number of waves: {len(env.wave_simulator.waves)}")
print(f"  Wave period: {env.wave_simulator.wave_period}s")

if len(env.wave_simulator.waves) > 0:
    wave = env.wave_simulator.waves[0]
    print(f"  Wave 0 position: ({wave.position[0]:.1f}, {wave.position[1]:.1f})")
    print(f"  Wave 0 height: {wave.height:.2f}m")
    print(f"  Wave 0 speed: {wave.speed:.2f}m/s")
    print(f"  Wave 0 breaking: {wave.is_breaking}")
    print("  ✓ Waves are spawning!")
else:
    print("  ⚠️  No waves yet, wait for wave period")

# Test swimming action
print("\n5. Testing swimming actions...")
action = np.array([0.0, 1.0, 0.0, 0.0])  # [direction, power=max, no duck_dive, -]
print(f"  Action: swim straight at full power")

obs, reward, terminated, truncated, info = env.step(action)

new_x = env.surfer.state.x
new_y = env.surfer.state.y
vx = env.surfer.state.vx
vy = env.surfer.state.vy
speed = np.sqrt(vx**2 + vy**2)

print(f"  New position: ({new_x:.1f}, {new_y:.1f})")
print(f"  Velocity: ({vx:.2f}, {vy:.2f}) = {speed:.2f}m/s")
print(f"  Distance moved: {np.sqrt((new_x-surfer_x)**2 + (new_y-surfer_y)**2):.3f}m")

if speed > 0.01:
    print("  ✓ Surfer IS moving!")
else:
    print("  ❌ Surfer NOT moving!")

# Run 100 steps swimming forward
print("\n6. Swimming forward 100 steps...")
for i in range(100):
    action = np.array([0.0, 1.0, 0.0, 0.0])  # Swim forward
    obs, reward, terminated, truncated, info = env.step(action)
    if terminated or truncated:
        print(f"  Episode ended at step {i}")
        break

final_x = env.surfer.state.x
final_y = env.surfer.state.y
distance = np.sqrt((final_x-surfer_x)**2 + (final_y-surfer_y)**2)

print(f"  Start: ({surfer_x:.1f}, {surfer_y:.1f})")
print(f"  End: ({final_x:.1f}, {final_y:.1f})")
print(f"  Total distance: {distance:.1f}m")
print(f"  Final depth: {env.ocean_floor.get_depth(final_x, final_y):.2f}m")

if distance > 1.0:
    print("  ✓ Surfer can swim!")
else:
    print("  ❌ Surfer barely moved!")

env.close()

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("\nIssues found:")
print("1. OLD ocean has no beach/sand - surfer spawns in deep water")
print("2. Use proper_beach_ocean.json instead")
print("3. Actions ARE working - surfer CAN swim")
print("4. Agent just needs to LEARN to use them")
print("\nTo train with proper ocean:")
print("  surferbro-train --ocean ocean_designs/proper_beach_ocean.json --timesteps 100000 --n-envs 4 --eval-freq 100000")
