"""ULTRA FAST 2-minute demo - NO evaluation callbacks, just pure training!"""

from surferbro.environments.surf_env import SurfEnvironment
from stable_baselines3 import SAC
from stable_baselines3.common.vec_env import DummyVecEnv
import time

print("="*60)
print("🏄 ULTRA FAST DEMO - 2 Minutes, NO WAITING!")
print("="*60)
print("\nNo evaluation callbacks = No waiting!")
print("Training: 10,000 steps (~2 minutes)")
print("\n✨ Using PROPER ocean with beach and depth gradient!")
print()

# Simple environment with PROPER ocean
env = DummyVecEnv([lambda: SurfEnvironment(
    ocean_design="ocean_designs/proper_beach_ocean.json"
)])

print("Creating SAC agent...")
model = SAC(
    "MlpPolicy",
    env,
    learning_rate=0.0003,
    buffer_size=10000,
    learning_starts=100,
    batch_size=64,
    verbose=1,
)

print("\nTraining 10,000 steps with NO interruptions...")
print("Watch it go fast!\n")

start_time = time.time()

try:
    # Pure training, no callbacks, no evaluation
    model.learn(total_timesteps=10000, progress_bar=True)

    elapsed = time.time() - start_time
    print(f"\n✅ Done in {elapsed:.1f} seconds!")

    # Save
    model.save("ultra_fast_model")
    print("Model saved: ultra_fast_model.zip")

    # Quick test
    print("\n" + "="*60)
    print("Quick Test")
    print("="*60)

    obs = env.reset()
    total_reward = 0

    for i in range(300):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)
        total_reward += reward[0]

        if done[0]:
            print(f"Episode ended at step {i}")
            break

    print(f"Total reward: {total_reward:.2f}")
    print(f"Surf time: {info[0].get('total_surf_time', 0):.2f}s")

    print("\n💡 The agent learned basic movement!")
    print("For real surfing, train longer:")
    print("  surferbro-train --timesteps 250000 --n-envs 4")

except KeyboardInterrupt:
    print("\nInterrupted!")

env.close()
print("\n🏄‍♂️ Demo complete!")
