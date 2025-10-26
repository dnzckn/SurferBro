"""Training script for SurferBro using Stable-Baselines3 (PyTorch backend)."""

import argparse
from pathlib import Path
from datetime import datetime
import torch

from stable_baselines3 import PPO, SAC, TD3
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.callbacks import (
    CheckpointCallback,
    EvalCallback,
    CallbackList
)
from stable_baselines3.common.monitor import Monitor

from surferbro.environments.surf_env import SurfEnvironment
from surferbro.utils.config import Config
from surferbro.training.callbacks import SurfProgressCallback


def make_env(ocean_design=None, config_path=None, rank=0):
    """Create environment factory for vectorized environments."""
    def _init():
        env = SurfEnvironment(ocean_design=ocean_design, config_path=config_path)
        env = Monitor(env)
        return env
    return _init


def train(args):
    """
    Train SurferBro agent.

    Args:
        args: Command line arguments
    """
    print("="*60)
    print("🏄 SurferBro Training - PyTorch Backend")
    print("="*60)

    # Load config
    config = Config(args.config)

    # Check PyTorch
    print(f"\nPyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")

    # Create output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path('trained_models') / f'surferbro_{args.algorithm}_{timestamp}'
    output_dir.mkdir(parents=True, exist_ok=True)

    log_dir = Path('logs') / f'{args.algorithm}_{timestamp}'
    log_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nOutput directory: {output_dir}")
    print(f"Log directory: {log_dir}")

    # Create environments
    print(f"\nCreating {args.n_envs} parallel environments...")

    if args.n_envs > 1:
        env = SubprocVecEnv([
            make_env(args.ocean, args.config, i) for i in range(args.n_envs)
        ])
    else:
        env = DummyVecEnv([make_env(args.ocean, args.config, 0)])

    # Create evaluation environment
    eval_env = DummyVecEnv([make_env(args.ocean, args.config, 0)])

    # Select algorithm
    algorithm_class = {
        'PPO': PPO,
        'SAC': SAC,
        'TD3': TD3
    }[args.algorithm]

    print(f"\nInitializing {args.algorithm} agent...")

    # Algorithm-specific configurations
    if args.algorithm == 'PPO':
        model = PPO(
            'MlpPolicy',
            env,
            learning_rate=config.get('training.learning_rate'),
            n_steps=config.get('training.n_steps'),
            batch_size=config.get('training.batch_size'),
            n_epochs=config.get('training.n_epochs'),
            gamma=config.get('training.gamma'),
            gae_lambda=config.get('training.gae_lambda'),
            verbose=1,
            tensorboard_log=str(log_dir),
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
    elif args.algorithm == 'SAC':
        model = SAC(
            'MlpPolicy',
            env,
            learning_rate=config.get('training.learning_rate'),
            buffer_size=100000,
            learning_starts=1000,
            batch_size=config.get('training.batch_size'),
            gamma=config.get('training.gamma'),
            verbose=1,
            tensorboard_log=str(log_dir),
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
    elif args.algorithm == 'TD3':
        model = TD3(
            'MlpPolicy',
            env,
            learning_rate=config.get('training.learning_rate'),
            buffer_size=100000,
            learning_starts=1000,
            batch_size=config.get('training.batch_size'),
            gamma=config.get('training.gamma'),
            verbose=1,
            tensorboard_log=str(log_dir),
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )

    # Callbacks
    checkpoint_callback = CheckpointCallback(
        save_freq=args.save_freq,
        save_path=str(output_dir),
        name_prefix='surferbro'
    )

    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=str(output_dir / 'best_model'),
        log_path=str(log_dir),
        eval_freq=args.eval_freq,
        n_eval_episodes=5,
        deterministic=True
    )

    progress_callback = SurfProgressCallback()

    callback_list = CallbackList([checkpoint_callback, eval_callback, progress_callback])

    # Train
    print(f"\nStarting training for {args.timesteps:,} timesteps...")
    print("Monitor progress with TensorBoard:")
    print(f"  tensorboard --logdir={log_dir}")
    print()

    try:
        model.learn(
            total_timesteps=args.timesteps,
            callback=callback_list,
            progress_bar=True
        )

        # Save final model
        final_path = output_dir / 'final_model.zip'
        model.save(final_path)
        print(f"\n✅ Training complete! Model saved to: {final_path}")

    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
        final_path = output_dir / 'interrupted_model.zip'
        model.save(final_path)
        print(f"Model saved to: {final_path}")

    finally:
        env.close()
        eval_env.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Train SurferBro RL agent')

    parser.add_argument(
        '--ocean',
        type=str,
        default=None,
        help='Path to OceanScope design file'
    )

    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to config file'
    )

    parser.add_argument(
        '--algorithm',
        type=str,
        default='PPO',
        choices=['PPO', 'SAC', 'TD3'],
        help='RL algorithm to use'
    )

    parser.add_argument(
        '--timesteps',
        type=int,
        default=1000000,
        help='Total timesteps to train'
    )

    parser.add_argument(
        '--n-envs',
        type=int,
        default=4,
        help='Number of parallel environments'
    )

    parser.add_argument(
        '--save-freq',
        type=int,
        default=10000,
        help='Checkpoint save frequency'
    )

    parser.add_argument(
        '--eval-freq',
        type=int,
        default=5000,
        help='Evaluation frequency'
    )

    args = parser.parse_args()
    train(args)


if __name__ == '__main__':
    main()
