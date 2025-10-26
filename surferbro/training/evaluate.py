"""Evaluation script for trained SurferBro agents."""

import argparse
import time
from pathlib import Path

from stable_baselines3 import PPO, SAC, TD3
from surferbro.environments.surf_env import SurfEnvironment


def evaluate(args):
    """
    Evaluate a trained agent.

    Args:
        args: Command line arguments
    """
    print("="*60)
    print("🏄 SurferBro Evaluation")
    print("="*60)

    # Detect algorithm from model path
    model_path = Path(args.model)
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")

    # Try to infer algorithm from path or use specified
    algorithm_class = {
        'PPO': PPO,
        'SAC': SAC,
        'TD3': TD3
    }.get(args.algorithm)

    if algorithm_class is None:
        # Try to infer from filename
        if 'ppo' in str(model_path).lower():
            algorithm_class = PPO
        elif 'sac' in str(model_path).lower():
            algorithm_class = SAC
        elif 'td3' in str(model_path).lower():
            algorithm_class = TD3
        else:
            algorithm_class = PPO  # Default

    print(f"\nLoading model from: {model_path}")
    model = algorithm_class.load(model_path)

    # Create environment
    render_mode = "human" if args.render else None
    env = SurfEnvironment(
        ocean_design=args.ocean,
        config_path=args.config,
        render_mode=render_mode
    )

    print(f"Running {args.episodes} episodes...\n")

    episode_rewards = []
    episode_surf_times = []

    for episode in range(args.episodes):
        obs, info = env.reset()
        total_reward = 0
        done = False
        steps = 0
        max_surf_time = 0

        while not done:
            action, _states = model.predict(obs, deterministic=args.deterministic)
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            steps += 1
            done = terminated or truncated

            if info.get('total_surf_time', 0) > max_surf_time:
                max_surf_time = info['total_surf_time']

            if args.render:
                env.render()
                if args.render_delay > 0:
                    time.sleep(args.render_delay)

        episode_rewards.append(total_reward)
        episode_surf_times.append(max_surf_time)

        print(f"Episode {episode + 1}/{args.episodes}: "
              f"Reward: {total_reward:.2f} | "
              f"Steps: {steps} | "
              f"Surf Time: {max_surf_time:.2f}s")

    # Summary statistics
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    print(f"Average Reward: {sum(episode_rewards) / len(episode_rewards):.2f}")
    print(f"Average Surf Time: {sum(episode_surf_times) / len(episode_surf_times):.2f}s")
    print(f"Max Surf Time: {max(episode_surf_times):.2f}s")
    print(f"Best Episode Reward: {max(episode_rewards):.2f}")

    env.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Evaluate SurferBro agent')

    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to trained model (.zip file)'
    )

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
        default=None,
        choices=['PPO', 'SAC', 'TD3'],
        help='Algorithm (auto-detected if not specified)'
    )

    parser.add_argument(
        '--episodes',
        type=int,
        default=10,
        help='Number of episodes to run'
    )

    parser.add_argument(
        '--render',
        action='store_true',
        help='Render the environment'
    )

    parser.add_argument(
        '--render-delay',
        type=float,
        default=0.0,
        help='Delay between frames (seconds)'
    )

    parser.add_argument(
        '--deterministic',
        action='store_true',
        default=True,
        help='Use deterministic actions'
    )

    args = parser.parse_args()
    evaluate(args)


if __name__ == '__main__':
    main()
