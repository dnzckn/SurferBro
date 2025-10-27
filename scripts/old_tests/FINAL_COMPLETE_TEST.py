"""FINAL COMPLETE TEST - All fixes + small ocean + training analysis"""

import json
import time
import numpy as np
from surferbro.environments.surf_env import SurfEnvironment
from surferbro.visualization.renderer_fixed import SurfRendererFixed
from stable_baselines3 import SAC
from stable_baselines3.common.vec_env import DummyVecEnv
import os

print("="*70)
print("🏄 FINAL COMPLETE TEST - All Fixes Applied!")
print("="*70)
print("\nFIXES:")
print("  ✅ Surfer now faces NORTH (toward waves) not EAST")
print("  ✅ Smaller ocean (25m x 15m = 4x faster interactions)")
print("  ✅ Waves ARE spawning and visible")
print("  ✅ Better visualization (beach, grid, big surfer/waves)")
print()

# ============================================================================
# PART 1: Quick Visual Test (10 seconds)
# ============================================================================
print("="*70)
print("PART 1: VISUAL TEST (10 seconds)")
print("="*70)
print("\nTesting surfer movement and wave visibility...\n")

with open("ocean_designs/small_beach_ocean.json", 'r') as f:
    ocean_design = json.load(f)

test_env = SurfEnvironment(ocean_design="ocean_designs/small_beach_ocean.json")
renderer = SurfRendererFixed(
    ocean_floor=test_env.ocean_floor,
    ocean_design_data=ocean_design,
    camera_mode="fixed"
)

obs, info = test_env.reset()

print(f"Start: ({test_env.surfer.state.x:.1f}, {test_env.surfer.state.y:.1f})")
print(f"Facing: {np.degrees(test_env.surfer.state.yaw):.1f}° (should be 90°=North)")
print(f"Depth: {test_env.ocean_floor.get_depth(test_env.surfer.state.x, test_env.surfer.state.y):.2f}m")
print(f"\nSwimming forward for 10 seconds...\n")

start_y = test_env.surfer.state.y
waves_seen = []

try:
    for step in range(300):  # 10 seconds at 30fps
        action = np.array([0.0, 1.0, 0.0, 0.0])  # Swim forward
        obs, reward, terminated, truncated, info = test_env.step(action)

        renderer.render(
            surfer=test_env.surfer,
            wave_simulator=test_env.wave_simulator,
            jellyfish_swarm=test_env.jellyfish_swarm,
            mode="human"
        )
        time.sleep(0.03)

        # Track waves
        if len(test_env.wave_simulator.waves) > len(waves_seen):
            waves_seen.append(len(test_env.wave_simulator.waves))

        if terminated or truncated:
            break

except KeyboardInterrupt:
    print("\nSkipped...")

end_y = test_env.surfer.state.y
distance = end_y - start_y

print(f"\n✅ Visual Test Results:")
print(f"  Start Y: {start_y:.1f}m")
print(f"  End Y: {end_y:.1f}m")
print(f"  Distance moved: {distance:.1f}m {'TOWARD WAVES ✓' if distance > 0 else 'WRONG DIRECTION ✗'}")
print(f"  Waves spawned: {len(waves_seen)}")
print(f"  Max waves at once: {max(waves_seen) if waves_seen else 0}")

renderer.close()
test_env.close()

if distance < 0.5:
    print("\n⚠️  Surfer barely moved! Stopping here.")
    exit(1)

time.sleep(2)

# ============================================================================
# PART 2: Train Agent (2 minutes)
# ============================================================================
print("\n" + "="*70)
print("PART 2: TRAINING AGENT (10k steps, ~2 min)")
print("="*70 + "\n")

train_env = DummyVecEnv([lambda: SurfEnvironment(
    ocean_design="ocean_designs/small_beach_ocean.json"
)])

model = SAC(
    "MlpPolicy",
    train_env,
    verbose=1,
    tensorboard_log="./logs/"
)

print("Training...")
train_start = time.time()

try:
    model.learn(total_timesteps=10000, progress_bar=True)
    train_time = time.time() - train_start

    print(f"\n✅ Training complete in {train_time:.1f}s")
    print(f"  Steps per second: {10000/train_time:.0f}")

    model.save("final_test_model")
    train_env.close()

except KeyboardInterrupt:
    print("\nTraining interrupted!")
    train_env.close()
    exit(1)

time.sleep(2)

# ============================================================================
# PART 3: Evaluate Trained Agent (watch it!)
# ============================================================================
print("\n" + "="*70)
print("PART 3: WATCHING TRAINED AGENT")
print("="*70 + "\n")

eval_env = SurfEnvironment(ocean_design="ocean_designs/small_beach_ocean.json")
eval_renderer = SurfRendererFixed(
    ocean_floor=eval_env.ocean_floor,
    ocean_design_data=ocean_design,
    camera_mode="fixed"
)

print("Running 3 episodes with trained agent...\n")

episode_stats = []

try:
    for episode in range(3):
        print(f"--- Episode {episode + 1}/3 ---")
        obs, info = eval_env.reset()
        total_reward = 0
        steps = 0
        start_y = eval_env.surfer.state.y
        max_y = start_y
        max_depth = 0

        while steps < 300:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = eval_env.step(action)
            total_reward += reward
            steps += 1

            current_y = eval_env.surfer.state.y
            current_depth = eval_env.ocean_floor.get_depth(
                eval_env.surfer.state.x, current_y
            )

            if current_y > max_y:
                max_y = current_y
            if current_depth > max_depth:
                max_depth = current_depth

            eval_renderer.render(
                surfer=eval_env.surfer,
                wave_simulator=eval_env.wave_simulator,
                jellyfish_swarm=eval_env.jellyfish_swarm,
                mode="human"
            )
            time.sleep(0.03)

            if terminated or truncated:
                break

        distance = max_y - start_y
        episode_stats.append({
            'reward': total_reward,
            'distance': distance,
            'max_depth': max_depth,
            'steps': steps
        })

        print(f"  Reward: {total_reward:.2f}")
        print(f"  Distance: {distance:.1f}m")
        print(f"  Max depth reached: {max_depth:.2f}m")
        print(f"  Steps: {steps}")

        if episode < 2:
            time.sleep(2)

except KeyboardInterrupt:
    print("\nStopped.")

eval_renderer.close()
eval_env.close()

# ============================================================================
# PART 4: Analysis
# ============================================================================
print("\n" + "="*70)
print("FINAL ANALYSIS")
print("="*70)

avg_reward = np.mean([s['reward'] for s in episode_stats])
avg_distance = np.mean([s['distance'] for s in episode_stats])
avg_depth = np.mean([s['max_depth'] for s in episode_stats])

print(f"\nAgent Performance:")
print(f"  Average Reward: {avg_reward:.2f}")
print(f"  Average Distance: {avg_distance:.1f}m")
print(f"  Average Max Depth: {avg_depth:.2f}m")

print(f"\nLearning Assessment:")
if avg_distance > 3:
    print(f"  ✅ EXCELLENT! Agent learned to swim toward waves")
    print(f"     Moved {avg_distance:.1f}m on average")
elif avg_distance > 1:
    print(f"  ✓ GOOD! Agent shows learning")
    print(f"    Moved {avg_distance:.1f}m (train longer for better results)")
elif avg_distance > 0.5:
    print(f"  ~ MARGINAL learning detected")
    print(f"    Only {avg_distance:.1f}m movement")
else:
    print(f"  ✗ NO learning detected")
    print(f"    Agent barely moved ({avg_distance:.1f}m)")

if avg_depth > 2:
    print(f"  ✅ Agent reached deeper water (wave zone)!")
else:
    print(f"  ⚠️  Agent stayed in shallow water")

print(f"\n{'='*70}")
print("DONE! 🏄‍♂️")
print(f"{'='*70}")

# Check logs
if os.path.exists('logs'):
    print(f"\nTensorBoard logs saved in: logs/")
    print(f"View with: tensorboard --logdir=logs/")
