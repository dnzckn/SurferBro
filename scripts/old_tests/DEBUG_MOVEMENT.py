"""DEBUG - Check surfer movement direction and wave spawning"""

import numpy as np
from surferbro.environments.surf_env import SurfEnvironment

print("="*60)
print("DEBUG: Checking Surfer Movement")
print("="*60)

# Create environment with small ocean
env = SurfEnvironment(ocean_design="ocean_designs/small_beach_ocean.json")
obs, info = env.reset()

print(f"\nInitial State:")
print(f"  Position: ({env.surfer.state.x:.2f}, {env.surfer.state.y:.2f})")
print(f"  Yaw: {env.surfer.state.yaw:.4f} rad = {np.degrees(env.surfer.state.yaw):.1f}°")
print(f"  Expected: π/2 = {np.pi/2:.4f} rad = 90°")
print(f"\nDirection vectors:")
print(f"  Yaw=0° (EAST/RIGHT):  cos(0)={np.cos(0):.2f}, sin(0)={np.sin(0):.2f} → (+x, 0)")
print(f"  Yaw=90° (NORTH/UP):   cos(π/2)={np.cos(np.pi/2):.2f}, sin(π/2)={np.sin(np.pi/2):.2f} → (0, +y)")
print(f"  Current yaw:          cos={np.cos(env.surfer.state.yaw):.2f}, sin={np.sin(env.surfer.state.yaw):.2f}")

start_x = env.surfer.state.x
start_y = env.surfer.state.y

print(f"\nSwimming forward (action=[0, 1, 0, 0]) for 100 steps...")

wave_count = 0
for step in range(100):
    # Swim forward at full power
    action = np.array([0.0, 1.0, 0.0, 0.0])
    obs, reward, terminated, truncated, info = env.step(action)

    if len(env.wave_simulator.waves) > wave_count:
        wave_count = len(env.wave_simulator.waves)
        wave = env.wave_simulator.waves[-1]
        print(f"  Step {step}: Wave #{wave_count} spawned at ({wave.position[0]:.1f}, {wave.position[1]:.1f})")

end_x = env.surfer.state.x
end_y = env.surfer.state.y

dx = end_x - start_x
dy = end_y - start_y
distance = np.sqrt(dx**2 + dy**2)

print(f"\nResults:")
print(f"  Start: ({start_x:.2f}, {start_y:.2f})")
print(f"  End:   ({end_x:.2f}, {end_y:.2f})")
print(f"  Delta: (Δx={dx:.2f}, Δy={dy:.2f})")
print(f"  Distance: {distance:.2f}m")
print(f"  Waves spawned: {wave_count}")

print(f"\nAnalysis:")
if abs(dx) > abs(dy):
    print(f"  ✗ PRIMARY MOVEMENT: HORIZONTAL ({dx:.2f}m) - WRONG!")
    print(f"    Surfer is moving RIGHT/LEFT (East/West)")
    print(f"    Should be moving UP (North, +Y direction)")
else:
    print(f"  ✓ PRIMARY MOVEMENT: VERTICAL ({dy:.2f}m) - CORRECT!")
    if dy > 0:
        print(f"    Surfer is moving UP (North) toward waves")
    else:
        print(f"    Surfer is moving DOWN (South) away from waves")

if wave_count == 0:
    print(f"  ✗ NO WAVES SPAWNED - Problem with wave simulator!")
else:
    print(f"  ✓ {wave_count} waves spawned - simulator working")

env.close()
