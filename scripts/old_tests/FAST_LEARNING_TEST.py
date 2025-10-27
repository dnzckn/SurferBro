"""Fast learning test - shorter episodes, more iterations"""

import time
import numpy as np
from surferbro.environments.surf_env import SurfEnvironment
from stable_baselines3 import SAC
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor

class ShortEpisodeEnv(SurfEnvironment):
    """Wrapper to shorten episodes for faster learning"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_episode_steps = 500  # Override to 500 steps (~16 seconds)

env_count = 0
def make_env():
    global env_count
    def _init():
        env = ShortEpisodeEnv(ocean_design="ocean_designs/small_beach_ocean.json")
        env = Monitor(env, filename=f"logs/training_{env_count}")
        return env
    env_count += 1
    return _init

print("="*70)
print("🏄 FAST LEARNING TEST")
print("="*70)
print("\nSetup:")
print("  • Episode length: 500 steps (~16s)")
print("  • Total steps: 10,000")
print("  • Expected episodes: ~20")
print("  • Small ocean (25m x 15m)")
print("  • Wave period: 3s")
print("\nThis should give us enough episodes to see learning!")
print("\nTraining...")
print()

# Create 4 parallel environments for faster training
env = DummyVecEnv([make_env() for _ in range(4)])

# Create agent
model = SAC(
    "MlpPolicy",
    env,
    verbose=1,
    learning_rate=3e-4,
    buffer_size=50000,
    learning_starts=1000,
    batch_size=256,
    tau=0.005,
    gamma=0.99,
    tensorboard_log="./logs/"
)

start = time.time()

try:
    model.learn(total_timesteps=10000, progress_bar=True)
    elapsed = time.time() - start

    print(f"\n✅ Training complete in {elapsed:.1f}s")
    print(f"   Steps per second: {10000/elapsed:.0f}")

    # Load and analyze monitor logs
    print("\n" + "="*70)
    print("ANALYZING MONITOR LOGS")
    print("="*70)

    import pandas as pd
    import os

    log_files = [f"logs/training_{i}.monitor.csv" for i in range(4) if os.path.exists(f"logs/training_{i}.monitor.csv")]

    all_episodes = []
    for log_file in log_files:
        try:
            df = pd.read_csv(log_file, skiprows=1)
            all_episodes.append(df)
        except Exception as e:
            print(f"Could not read {log_file}: {e}")

    if all_episodes:
        combined = pd.concat(all_episodes, ignore_index=True)
        combined = combined.sort_values('t')  # Sort by time

        print(f"\nTotal episodes: {len(combined)}")
        print(f"Total timesteps: {combined['l'].sum():.0f}")

        print(f"\nReward progression:")
        print(f"  First 5 avg:  {combined['r'].head(5).mean():.2f}")
        if len(combined) > 10:
            print(f"  Middle 5 avg: {combined['r'].iloc[len(combined)//2-2:len(combined)//2+3].mean():.2f}")
            print(f"  Last 5 avg:   {combined['r'].tail(5).mean():.2f}")

        print(f"\nEpisode length:")
        print(f"  First 5 avg:  {combined['l'].head(5).mean():.0f} steps")
        if len(combined) > 10:
            print(f"  Last 5 avg:   {combined['l'].tail(5).mean():.0f} steps")

        print(f"\nReward stats:")
        print(f"  Min:    {combined['r'].min():.2f}")
        print(f"  Max:    {combined['r'].max():.2f}")
        print(f"  Mean:   {combined['r'].mean():.2f}")
        print(f"  Median: {combined['r'].median():.2f}")

        # Check for learning
        if len(combined) > 10:
            early_reward = combined['r'].head(10).mean()
            late_reward = combined['r'].tail(10).mean()
            improvement = late_reward - early_reward

            print(f"\nLearning Assessment:")
            if improvement > 5:
                print(f"  ✅ STRONG learning detected! (+{improvement:.1f} reward)")
            elif improvement > 1:
                print(f"  ✓ SOME learning detected (+{improvement:.1f} reward)")
            elif improvement > -1:
                print(f"  ~ MARGINAL change ({improvement:+.1f} reward)")
            else:
                print(f"  ✗ NEGATIVE trend ({improvement:+.1f} reward)")

    # Save model
    model.save("fast_learning_model")
    env.close()

    print("\n" + "="*70)
    print(f"Model saved to: fast_learning_model.zip")
    print(f"Logs saved to: logs/")
    print("="*70)

except KeyboardInterrupt:
    print("\n\nTraining interrupted!")
    env.close()
except Exception as e:
    print(f"\n\nError: {e}")
    import traceback
    traceback.print_exc()
    env.close()
