"""Quick 5-minute demo training - See SurferBro learn fast!"""

from surferbro.environments.surf_env import SurfEnvironment
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

print("="*60)
print("🏄 SurferBro QUICK DEMO - 5 Minutes")
print("="*60)
print("\nTraining with your custom ocean design...")
print("Timesteps: 25,000 (~5 minutes)")
print()

# Create environment with your custom ocean
def make_env():
    return SurfEnvironment(
        ocean_design="ocean_designs/ocean_design_20251026_150514.json"
    )

env = DummyVecEnv([make_env])

# Create PPO agent
print("Creating PPO agent...")
model = PPO(
    "MlpPolicy",
    env,
    learning_rate=0.0003,
    n_steps=2048,
    batch_size=64,
    verbose=1,
    tensorboard_log="./logs/"
)

# Train
print("\nTraining for 25,000 steps...")
print("This will take about 5 minutes.\n")

try:
    model.learn(total_timesteps=25000, progress_bar=True)

    # Save
    model.save("quick_demo_model")
    print("\n✅ Training complete! Model saved as 'quick_demo_model.zip'")

    # Quick test
    print("\n" + "="*60)
    print("Testing the agent...")
    print("="*60)

    obs = env.reset()
    total_reward = 0
    steps = 0

    for _ in range(500):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        total_reward += reward[0]
        steps += 1

        if done[0]:
            break

    print(f"\nTest Results:")
    print(f"  Steps: {steps}")
    print(f"  Total Reward: {total_reward:.2f}")
    print(f"  Surf Time: {info[0].get('total_surf_time', 0):.2f}s")

    print("\n💡 For better results, train longer:")
    print("   surferbro-train --ocean ocean_designs/ocean_design_20251026_150514.json --timesteps 250000")

except KeyboardInterrupt:
    print("\n\nTraining interrupted!")
    model.save("quick_demo_interrupted")
    print("Model saved as 'quick_demo_interrupted.zip'")

env.close()
print("\n🏄‍♂️ Demo complete!")
