"""Basic training example for SurferBro."""

from surferbro.environments.surf_env import SurfEnvironment
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

# Create environment
print("Creating SurferBro environment...")
env = SurfEnvironment()

# Validate environment
print("Validating environment...")
check_env(env)
print("✓ Environment is valid!")

# Create PPO agent
print("\nCreating PPO agent...")
model = PPO(
    "MlpPolicy",
    env,
    learning_rate=0.0003,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    verbose=1,
    tensorboard_log="./logs/"
)

# Train
print("\nStarting training for 100,000 steps...")
print("This is a short demo. For full training, use surferbro-train command.")
print()

model.learn(total_timesteps=100_000, progress_bar=True)

# Save model
model.save("surferbro_basic_demo")
print("\n✓ Training complete! Model saved as 'surferbro_basic_demo.zip'")

# Test the agent
print("\nTesting trained agent...")
obs, info = env.reset()
total_reward = 0

for _ in range(1000):
    action, _states = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    total_reward += reward

    if terminated or truncated:
        break

print(f"Test episode reward: {total_reward:.2f}")
print(f"Surfing time: {info.get('total_surf_time', 0):.2f}s")

env.close()
