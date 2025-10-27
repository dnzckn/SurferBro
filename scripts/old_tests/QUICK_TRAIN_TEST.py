"""Quick training test to verify mechanics and analyze logs"""

import time
import numpy as np
from surferbro.environments.surf_env import SurfEnvironment
from stable_baselines3 import SAC
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback

class DetailedLoggingCallback(BaseCallback):
    """Log detailed episode stats"""
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []
        self.episode_lengths = []
        self.episode_stats = []

    def _on_step(self) -> bool:
        # Check if episode ended
        for idx, done in enumerate(self.locals['dones']):
            if done:
                info = self.locals['infos'][idx]
                episode_reward = self.locals['rewards'][idx]

                stats = {
                    'timestep': self.num_timesteps,
                    'reward': info.get('episode', {}).get('r', 0),
                    'length': info.get('episode', {}).get('l', 0),
                    'surfer_position': info.get('surfer_position', (0, 0)),
                    'is_surfing': info.get('is_surfing', False),
                    'surf_time': info.get('total_surf_time', 0),
                    'num_waves': info.get('num_waves', 0)
                }
                self.episode_stats.append(stats)

                if len(self.episode_stats) % 5 == 0:
                    recent = self.episode_stats[-5:]
                    avg_reward = np.mean([s['reward'] for s in recent])
                    avg_y = np.mean([s['surfer_position'][1] for s in recent])
                    surfing_count = sum([s['is_surfing'] for s in recent])
                    print(f"  Episode {len(self.episode_stats)}: "
                          f"Reward={avg_reward:.1f}, "
                          f"AvgY={avg_y:.1f}m, "
                          f"Surfing={surfing_count}/5")
        return True

print("="*70)
print("🏄 QUICK TRAINING TEST (5k steps, ~1 min)")
print("="*70)
print("\nMechanics being tested:")
print("  • Duck dive (3s duration, blocks movement)")
print("  • Wave collision (pushback if not diving)")
print("  • Wave carrying (must wait 1s before standing)")
print("  • Standing up (must align with wave)")
print("\nTraining...")
print()

# Create environment
env = DummyVecEnv([lambda: SurfEnvironment(
    ocean_design="ocean_designs/small_beach_ocean.json"
)])

# Create agent
model = SAC(
    "MlpPolicy",
    env,
    verbose=0,
    learning_rate=3e-4,
    buffer_size=10000,
    batch_size=256,
    tau=0.005,
    gamma=0.99
)

# Train with logging
callback = DetailedLoggingCallback()
start = time.time()

try:
    model.learn(total_timesteps=5000, callback=callback, progress_bar=True)
    elapsed = time.time() - start

    print(f"\n✅ Training complete in {elapsed:.1f}s")
    print(f"   Steps per second: {5000/elapsed:.0f}")

    # Analyze results
    print("\n" + "="*70)
    print("TRAINING ANALYSIS")
    print("="*70)

    if callback.episode_stats:
        stats = callback.episode_stats

        print(f"\nEpisodes completed: {len(stats)}")
        print(f"Total timesteps: {stats[-1]['timestep'] if stats else 0}")

        rewards = [s['reward'] for s in stats]
        y_positions = [s['surfer_position'][1] for s in stats]
        surf_times = [s['surf_time'] for s in stats]

        print(f"\nReward progression:")
        print(f"  First 10 avg: {np.mean(rewards[:10]):.2f}")
        if len(rewards) > 10:
            print(f"  Last 10 avg:  {np.mean(rewards[-10:]):.2f}")
            print(f"  Improvement:  {np.mean(rewards[-10:]) - np.mean(rewards[:10]):.2f}")

        print(f"\nMovement (Y position at episode end):")
        print(f"  First 10 avg: {np.mean(y_positions[:10]):.2f}m")
        if len(y_positions) > 10:
            print(f"  Last 10 avg:  {np.mean(y_positions[-10:]):.2f}m")
            print(f"  Progress:     {np.mean(y_positions[-10:]) - np.mean(y_positions[:10]):.2f}m")

        surfing_episodes = sum([1 for s in stats if s['is_surfing']])
        print(f"\nSurfing success:")
        print(f"  Episodes with surfing: {surfing_episodes}/{len(stats)}")
        print(f"  Success rate: {100*surfing_episodes/len(stats):.1f}%")

        if surfing_episodes > 0:
            avg_surf_time = np.mean([s['surf_time'] for s in stats if s['surf_time'] > 0])
            print(f"  Avg surf time (when surfing): {avg_surf_time:.2f}s")

        print(f"\nKey Learning Indicators:")
        if len(y_positions) > 20:
            early_y = np.mean(y_positions[:10])
            late_y = np.mean(y_positions[-10:])
            if late_y > early_y + 1.0:
                print(f"  ✅ Agent learning to move toward waves (+{late_y - early_y:.1f}m)")
            else:
                print(f"  ⚠️  Limited forward progress ({late_y - early_y:.1f}m)")

        if surfing_episodes > 0:
            print(f"  ✅ Agent learned to catch waves!")
        else:
            print(f"  ⚠️  No surfing yet (needs more training)")

        recent_rewards = rewards[-10:] if len(rewards) > 10 else rewards
        if np.mean(recent_rewards) > -20:
            print(f"  ✅ Positive learning trend (reward: {np.mean(recent_rewards):.1f})")
        else:
            print(f"  ⚠️  Still learning basics (reward: {np.mean(recent_rewards):.1f})")

    # Save model
    model.save("quick_train_model")
    env.close()

    print("\n" + "="*70)
    print(f"Model saved to: quick_train_model.zip")
    print("="*70)

except KeyboardInterrupt:
    print("\n\nTraining interrupted!")
    env.close()
