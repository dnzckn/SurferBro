"""
🏄 SurferBro - Long Training Script

This script trains a SAC agent to surf with all realistic mechanics:
- Angled wave fronts (±30°)
- 45° catch angle requirement
- Crash → whitewash carry
- Duck dive escape
- Variable carry duration

Recommended: 500k-1M timesteps for emergent behavior
"""

import os
import time
from datetime import datetime
import numpy as np
from stable_baselines3 import SAC
from stable_baselines3.common.callbacks import (
    CheckpointCallback,
    EvalCallback,
    CallbackList
)
from stable_baselines3.common.monitor import Monitor
from surferbro.environments.surf_env import SurfEnvironment


# ============================================================================
# CONFIGURATION
# ============================================================================

TOTAL_TIMESTEPS = 1_000_000  # 1 million steps (~12-15 hours)
EVAL_FREQ = 10_000           # Evaluate every 10k steps
SAVE_FREQ = 50_000           # Save checkpoint every 50k steps
N_EVAL_EPISODES = 5          # Number of episodes for evaluation

# SAC Hyperparameters (tuned for continuous control)
LEARNING_RATE = 3e-4
BUFFER_SIZE = 100_000
BATCH_SIZE = 256
TAU = 0.005                  # Soft update coefficient
GAMMA = 0.99                 # Discount factor
TRAIN_FREQ = 1               # Update after every step
GRADIENT_STEPS = 1           # Gradient steps per update

# Paths
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_DIR = f"./logs/surferbro_{TIMESTAMP}"
CHECKPOINT_DIR = f"./checkpoints/surferbro_{TIMESTAMP}"
FINAL_MODEL_PATH = f"./models/surferbro_final_{TIMESTAMP}"

# Create directories
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CHECKPOINT_DIR, exist_ok=True)
os.makedirs("./models", exist_ok=True)


# ============================================================================
# CUSTOM CALLBACK FOR DETAILED LOGGING
# ============================================================================

class SurfMetricsCallback(CheckpointCallback):
    """
    Custom callback to log surfing-specific metrics.
    Tracks: wave catches, duck dives, crashes, escapes, distance traveled.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.episode_metrics = {
            'wave_catches': 0,
            'duck_dives': 0,
            'crashes': 0,
            'whitewash_escapes': 0,
            'max_distance': 0,
            'total_surf_time': 0
        }

    def _on_step(self) -> bool:
        # Call parent to handle checkpointing
        result = super()._on_step()

        # Log custom metrics every 1000 steps
        if self.n_calls % 1000 == 0:
            # Get environment (unwrap Monitor if needed)
            env = self.training_env.envs[0]
            if hasattr(env, 'env'):
                env = env.env

            # Log surfing metrics
            if hasattr(env, 'surfer'):
                self.logger.record("surf/position_y", env.surfer.state.y)
                self.logger.record("surf/is_surfing", float(env.surfer.state.is_surfing))
                self.logger.record("surf/is_duck_diving", float(env.surfer.state.is_duck_diving))
                self.logger.record("surf/is_whitewash_carry", float(env.surfer.state.is_whitewash_carry))

        return result


# ============================================================================
# MAIN TRAINING FUNCTION
# ============================================================================

def train():
    """Main training function."""

    print("=" * 80)
    print("🏄 SURFERBRO - LONG TRAINING SESSION")
    print("=" * 80)
    print()
    print("Configuration:")
    print(f"  Total timesteps:    {TOTAL_TIMESTEPS:,}")
    print(f"  Expected duration:  ~{TOTAL_TIMESTEPS / 80 / 3600:.1f} hours (at 80 steps/sec)")
    print(f"  Eval frequency:     Every {EVAL_FREQ:,} steps")
    print(f"  Save frequency:     Every {SAVE_FREQ:,} steps")
    print(f"  Episodes per eval:  {N_EVAL_EPISODES}")
    print()
    print("SAC Hyperparameters:")
    print(f"  Learning rate:      {LEARNING_RATE}")
    print(f"  Buffer size:        {BUFFER_SIZE:,}")
    print(f"  Batch size:         {BATCH_SIZE}")
    print(f"  Gamma:              {GAMMA}")
    print(f"  Tau:                {TAU}")
    print()
    print("Outputs:")
    print(f"  TensorBoard logs:   {LOG_DIR}")
    print(f"  Checkpoints:        {CHECKPOINT_DIR}")
    print(f"  Final model:        {FINAL_MODEL_PATH}")
    print()
    print("Mechanics Enabled:")
    print("  ✅ Angled wave fronts (±30° variation)")
    print("  ✅ 3-phase wave lifecycle (building → front → whitewash)")
    print("  ✅ 45° catch angle requirement (±5° tolerance)")
    print("  ✅ Variable carry duration (1-3s based on wave size)")
    print("  ✅ Crash → whitewash carry (doesn't end episode!)")
    print("  ✅ Duck dive escape from whitewash")
    print("  ✅ Optimized episodes (750 steps = ~25s)")
    print()
    print("=" * 80)
    print()

    # User confirmation
    input("Press ENTER to start training (Ctrl+C to cancel)...")
    print()

    # ========================================================================
    # CREATE ENVIRONMENTS
    # ========================================================================

    print("Creating environments...")

    # Training environment (wrapped in Monitor for logging)
    train_env = Monitor(SurfEnvironment(), LOG_DIR)

    # Evaluation environment (separate instance)
    eval_env = Monitor(SurfEnvironment(), LOG_DIR)

    print("✅ Environments created")
    print()

    # ========================================================================
    # CREATE AGENT
    # ========================================================================

    print("Creating SAC agent...")

    model = SAC(
        "MlpPolicy",
        train_env,
        learning_rate=LEARNING_RATE,
        buffer_size=BUFFER_SIZE,
        batch_size=BATCH_SIZE,
        tau=TAU,
        gamma=GAMMA,
        train_freq=TRAIN_FREQ,
        gradient_steps=GRADIENT_STEPS,
        verbose=1,
        tensorboard_log=LOG_DIR,
        device="auto"  # Use GPU if available, else CPU
    )

    print("✅ SAC agent created")
    print(f"   Device: {model.device}")
    print()

    # ========================================================================
    # CREATE CALLBACKS
    # ========================================================================

    print("Setting up callbacks...")

    # Checkpoint callback - saves model periodically
    checkpoint_callback = SurfMetricsCallback(
        save_freq=SAVE_FREQ,
        save_path=CHECKPOINT_DIR,
        name_prefix="surferbro_ckpt",
        save_replay_buffer=True,
        save_vecnormalize=True,
    )

    # Evaluation callback - evaluates agent performance
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=f"{CHECKPOINT_DIR}/best_model",
        log_path=LOG_DIR,
        eval_freq=EVAL_FREQ,
        n_eval_episodes=N_EVAL_EPISODES,
        deterministic=True,
        render=False,
        verbose=1
    )

    # Combine callbacks
    callbacks = CallbackList([checkpoint_callback, eval_callback])

    print("✅ Callbacks configured")
    print()

    # ========================================================================
    # TRAIN!
    # ========================================================================

    print("=" * 80)
    print("🚀 STARTING TRAINING")
    print("=" * 80)
    print()
    print("Monitor progress:")
    print(f"  TensorBoard: tensorboard --logdir {LOG_DIR}")
    print(f"  Watch live:  tail -f {LOG_DIR}/*.monitor.csv")
    print()
    print("Expected milestones:")
    print(f"  {50_000:>7,} steps: Agent learns to move")
    print(f"  {100_000:>7,} steps: Agent learns duck diving")
    print(f"  {250_000:>7,} steps: Agent attempts wave catching")
    print(f"  {500_000:>7,} steps: Agent positions at angles")
    print(f"  {1_000_000:>7,} steps: Agent masters surfing sequence")
    print()
    print("=" * 80)
    print()

    start_time = time.time()

    try:
        model.learn(
            total_timesteps=TOTAL_TIMESTEPS,
            callback=callbacks,
            log_interval=10,  # Log every 10 episodes
            progress_bar=True
        )
    except KeyboardInterrupt:
        print()
        print("⚠️  Training interrupted by user!")
        print()

    elapsed = time.time() - start_time

    # ========================================================================
    # SAVE FINAL MODEL
    # ========================================================================

    print()
    print("=" * 80)
    print("💾 SAVING FINAL MODEL")
    print("=" * 80)
    print()

    model.save(FINAL_MODEL_PATH)
    print(f"✅ Model saved to: {FINAL_MODEL_PATH}")
    print()

    # ========================================================================
    # TRAINING SUMMARY
    # ========================================================================

    print("=" * 80)
    print("📊 TRAINING SUMMARY")
    print("=" * 80)
    print()
    print(f"Total training time:  {elapsed / 3600:.2f} hours")
    print(f"Steps per second:     {TOTAL_TIMESTEPS / elapsed:.1f}")
    print(f"Total timesteps:      {TOTAL_TIMESTEPS:,}")
    print()
    print("Files created:")
    print(f"  Final model:        {FINAL_MODEL_PATH}.zip")
    print(f"  Best model:         {CHECKPOINT_DIR}/best_model/best_model.zip")
    print(f"  Checkpoints:        {CHECKPOINT_DIR}/surferbro_ckpt_*")
    print(f"  TensorBoard logs:   {LOG_DIR}")
    print()
    print("=" * 80)
    print()

    # ========================================================================
    # EVALUATION
    # ========================================================================

    print("=" * 80)
    print("🎯 EVALUATING TRAINED AGENT")
    print("=" * 80)
    print()

    print("Running 10 test episodes...")
    print()

    eval_rewards = []
    eval_distances = []
    eval_surf_times = []
    eval_crashes = []

    for ep in range(10):
        obs, info = eval_env.reset()
        start_y = eval_env.env.surfer.state.y if hasattr(eval_env, 'env') else eval_env.surfer.state.y
        episode_reward = 0
        crashed = False
        surf_time = 0

        for _ in range(750):
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = eval_env.step(action)
            episode_reward += reward

            surfer = eval_env.env.surfer if hasattr(eval_env, 'env') else eval_env.surfer
            if surfer.state.is_surfing:
                surf_time += 0.01
            if surfer.state.is_whitewash_carry:
                crashed = True

            if terminated or truncated:
                break

        end_y = eval_env.env.surfer.state.y if hasattr(eval_env, 'env') else eval_env.surfer.state.y
        distance = end_y - start_y

        eval_rewards.append(episode_reward)
        eval_distances.append(distance)
        eval_surf_times.append(surf_time)
        eval_crashes.append(crashed)

        print(f"  Episode {ep+1:2d}: reward={episode_reward:7.2f}, "
              f"distance={distance:5.2f}m, surf_time={surf_time:5.2f}s, crashed={crashed}")

    print()
    print("Evaluation Results:")
    print(f"  Avg reward:       {np.mean(eval_rewards):7.2f} ± {np.std(eval_rewards):5.2f}")
    print(f"  Avg distance:     {np.mean(eval_distances):7.2f}m ± {np.std(eval_distances):5.2f}")
    print(f"  Avg surf time:    {np.mean(eval_surf_times):7.2f}s ± {np.std(eval_surf_times):5.2f}")
    print(f"  Crash rate:       {sum(eval_crashes)}/10 episodes")
    print()

    # ========================================================================
    # NEXT STEPS
    # ========================================================================

    print("=" * 80)
    print("🎓 NEXT STEPS")
    print("=" * 80)
    print()
    print("1. View training curves:")
    print(f"   tensorboard --logdir {LOG_DIR}")
    print()
    print("2. Load and test the trained model:")
    print(f"   model = SAC.load('{FINAL_MODEL_PATH}')")
    print()
    print("3. Continue training from checkpoint:")
    print(f"   model = SAC.load('{CHECKPOINT_DIR}/best_model/best_model')")
    print(f"   model.learn(total_timesteps=500_000)")
    print()
    print("4. If agent isn't learning well, try:")
    print("   - Adjust reward weights in surf_env.py")
    print("   - Increase BUFFER_SIZE for more experience replay")
    print("   - Decrease LEARNING_RATE for more stable learning")
    print("   - Train for more steps (2M+)")
    print()
    print("=" * 80)
    print()
    print("🏄 Training complete! Good luck surfing!")
    print()

    # Clean up
    train_env.close()
    eval_env.close()


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    train()
