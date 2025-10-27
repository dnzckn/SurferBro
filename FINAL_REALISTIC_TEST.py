"""
FINAL REALISTIC TEST - Complete wave mechanics with analysis

Tests:
1. Visual demonstration of mechanics
2. Training run with detailed logging
3. Analysis of what agent learned
"""

import json
import time
import numpy as np
from surferbro.environments.surf_env import SurfEnvironment
from surferbro.visualization.renderer_fixed import SurfRendererFixed
from stable_baselines3 import SAC
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
import pandas as pd

print("="*80)
print("🏄 FINAL REALISTIC SURFING TEST")
print("="*80)
print("\nREALISTIC MECHANICS:")
print("  ✓ Angled wave fronts (±30° variation)")
print("  ✓ 3-phase lifecycle (building → front → whitewash)")
print("  ✓ Catch at 45° to wave FRONT (±5° tolerance)")
print("  ✓ Carry duration: 1-3s depending on wave size")
print("  ✓ Duck dive: 3s underwater, blocks movement, avoids pushback")
print("  ✓ Auto-detects beach location")
print()

# =============================================================================
# PART 1: Visual Demonstration (10 seconds)
# =============================================================================
print("="*80)
print("PART 1: VISUAL DEMONSTRATION (10s)")
print("="*80)
print("\nShowing realistic wave mechanics...")
print("Watch for angled wave fronts with direction arrows!\n")

with open("ocean_designs/small_beach_ocean.json", 'r') as f:
    ocean_design = json.load(f)

demo_env = SurfEnvironment(ocean_design="ocean_designs/small_beach_ocean.json")
renderer = SurfRendererFixed(
    ocean_floor=demo_env.ocean_floor,
    ocean_design_data=ocean_design,
    camera_mode="fixed"
)

obs, info = demo_env.reset()
print(f"Surfer start: ({demo_env.surfer.state.x:.1f}, {demo_env.surfer.state.y:.1f})")
print(f"Required carry duration will vary by wave size (1-3s)\n")

try:
    for step in range(300):  # 10 seconds
        action = np.array([0.0, 0.8, 0.0, 0.0])  # Swim forward
        obs, reward, terminated, truncated, info = demo_env.step(action)

        renderer.render(
            surfer=demo_env.surfer,
            wave_simulator=demo_env.wave_simulator,
            jellyfish_swarm=demo_env.jellyfish_swarm,
            mode="human"
        )
        time.sleep(0.03)

        if terminated or truncated:
            break

except KeyboardInterrupt:
    print("Skipped...")

renderer.close()
demo_env.close()

print("\n✓ Visual demo complete!")
time.sleep(2)

# =============================================================================
# PART 2: Training with Detailed Logging
# =============================================================================
print("\n" + "="*80)
print("PART 2: TRAINING (10k steps, ~2 min)")
print("="*80)

class DetailedLogger(BaseCallback):
    """Log episode details for analysis."""
    def __init__(self):
        super().__init__()
        self.episodes = []

    def _on_step(self) -> bool:
        for idx, done in enumerate(self.locals['dones']):
            if done:
                info = self.locals['infos'][idx]
                ep_info = info.get('episode', {})

                self.episodes.append({
                    'timestep': self.num_timesteps,
                    'reward': ep_info.get('r', 0),
                    'length': ep_info.get('l', 0),
                    'final_y': info.get('surfer_position', (0, 0))[1],
                    'is_surfing': info.get('is_surfing', False),
                    'surf_time': info.get('total_surf_time', 0),
                    'num_waves': info.get('num_waves', 0)
                })

                if len(self.episodes) % 10 == 0:
                    recent = self.episodes[-10:]
                    avg_reward = np.mean([e['reward'] for e in recent])
                    surfing_rate = sum([e['is_surfing'] for e in recent]) / 10
                    avg_y = np.mean([e['final_y'] for e in recent])
                    print(f"  Ep {len(self.episodes)}: R={avg_reward:.1f}, "
                          f"Surf%={surfing_rate*100:.0f}%, AvgY={avg_y:.1f}m")

        return True

print("\nCreating training environment...")
train_env = DummyVecEnv([lambda: SurfEnvironment(
    ocean_design="ocean_designs/small_beach_ocean.json"
)])

print("Initializing SAC agent...")
model = SAC(
    "MlpPolicy",
    train_env,
    verbose=0,
    learning_rate=3e-4,
    buffer_size=50000,
    batch_size=256,
    learning_starts=1000
)

logger = DetailedLogger()

print("\nTraining for 10,000 steps...")
start_time = time.time()

try:
    model.learn(total_timesteps=10000, callback=logger, progress_bar=True)
    train_time = time.time() - start_time

    print(f"\n✓ Training complete in {train_time:.1f}s ({10000/train_time:.0f} steps/s)")
    model.save("final_realistic_model")

except KeyboardInterrupt:
    print("\nTraining interrupted!")

train_env.close()

# =============================================================================
# PART 3: Analysis
# =============================================================================
print("\n" + "="*80)
print("PART 3: TRAINING ANALYSIS")
print("="*80)

if logger.episodes:
    df = pd.DataFrame(logger.episodes)

    print(f"\nEpisodes completed: {len(df)}")
    print(f"Total timesteps: {df['timestep'].max()}")

    print(f"\n📊 Reward Progression:")
    first10 = df.head(10)['reward'].mean()
    last10 = df.tail(10)['reward'].mean()
    print(f"  First 10 episodes: {first10:.2f}")
    print(f"  Last 10 episodes:  {last10:.2f}")
    print(f"  Improvement:       {last10 - first10:+.2f}")

    print(f"\n📊 Movement (Y position):")
    first_y = df.head(10)['final_y'].mean()
    last_y = df.tail(10)['final_y'].mean()
    print(f"  First 10 avg: {first_y:.2f}m")
    print(f"  Last 10 avg:  {last_y:.2f}m")
    print(f"  Progress:     {last_y - first_y:+.2f}m")

    print(f"\n📊 Surfing Success:")
    total_surfing = df['is_surfing'].sum()
    surf_rate = total_surfing / len(df) * 100
    print(f"  Episodes with surfing: {total_surfing}/{len(df)} ({surf_rate:.1f}%)")

    if total_surfing > 0:
        avg_surf_time = df[df['is_surfing']]['surf_time'].mean()
        print(f"  Avg surf time: {avg_surf_time:.2f}s")

    print(f"\n📊 Learning Indicators:")
    if last10 > first10 + 10:
        print(f"  ✅ STRONG improvement (+{last10-first10:.1f} reward)")
    elif last10 > first10:
        print(f"  ✓ Some improvement (+{last10-first10:.1f} reward)")
    else:
        print(f"  ⚠️  No improvement ({last10-first10:.1f})")

    if last_y > first_y + 2:
        print(f"  ✅ Learning to swim toward waves (+{last_y-first_y:.1f}m)")
    elif last_y > first_y:
        print(f"  ✓ Some forward progress (+{last_y-first_y:.1f}m)")
    else:
        print(f"  ⚠️  Not moving forward ({last_y-first_y:.1f}m)")

    if surf_rate > 10:
        print(f"  ✅ Learning to catch waves ({surf_rate:.0f}% success)")
    elif surf_rate > 0:
        print(f"  ✓ Occasionally catching waves ({surf_rate:.0f}%)")
    else:
        print(f"  ⚠️  Not catching waves yet")

    # Save detailed logs
    df.to_csv("training_analysis.csv", index=False)
    print(f"\n💾 Detailed logs saved to: training_analysis.csv")

print("\n" + "="*80)
print("TEST COMPLETE! 🏄")
print("="*80)
print("\nRun 'tensorboard --logdir=logs/' to see training curves")
print("Model saved to: final_realistic_model.zip")
