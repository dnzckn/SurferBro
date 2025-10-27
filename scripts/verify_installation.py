"""Verify SurferBro installation."""

import sys

print("="*60)
print("SurferBro Installation Verification")
print("="*60)

# Check Python version
print(f"\nPython version: {sys.version}")
if sys.version_info < (3, 8):
    print("❌ Python 3.8+ required")
    sys.exit(1)
else:
    print("✓ Python version OK")

# Check imports
required_packages = [
    ('numpy', 'NumPy'),
    ('scipy', 'SciPy'),
    ('gymnasium', 'Gymnasium'),
    ('stable_baselines3', 'Stable-Baselines3'),
    ('torch', 'PyTorch'),
    ('pybullet', 'PyBullet'),
    ('pygame', 'Pygame'),
    ('flask', 'Flask'),
    ('yaml', 'PyYAML'),
    ('matplotlib', 'Matplotlib'),
    ('trimesh', 'Trimesh'),
]

print("\nChecking dependencies...")
all_ok = True
for package, name in required_packages:
    try:
        __import__(package)
        print(f"✓ {name}")
    except ImportError:
        print(f"❌ {name} not found")
        all_ok = False

# Check SurferBro modules
print("\nChecking SurferBro modules...")
surferbro_modules = [
    'surferbro',
    'surferbro.oceanscope',
    'surferbro.physics',
    'surferbro.environments',
    'surferbro.agents',
    'surferbro.training',
    'surferbro.visualization',
    'surferbro.utils',
]

for module in surferbro_modules:
    try:
        __import__(module)
        print(f"✓ {module}")
    except ImportError as e:
        print(f"❌ {module} - {e}")
        all_ok = False

# Check PyTorch CUDA
print("\nPyTorch Configuration:")
try:
    import torch
    print(f"  Version: {torch.__version__}")
    print(f"  CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"  CUDA Device: {torch.cuda.get_device_name(0)}")
except Exception as e:
    print(f"  Error checking PyTorch: {e}")

# Test environment creation
print("\nTesting environment creation...")
try:
    from surferbro.environments.surf_env import SurfEnvironment
    env = SurfEnvironment()
    obs, info = env.reset()
    print(f"✓ Environment created successfully")
    print(f"  Observation shape: {obs.shape}")
    print(f"  Action shape: {env.action_space.shape}")
    env.close()
except Exception as e:
    print(f"❌ Environment creation failed: {e}")
    all_ok = False

# Final verdict
print("\n" + "="*60)
if all_ok:
    print("✅ Installation verified successfully!")
    print("\nNext steps:")
    print("  1. python -m surferbro.oceanscope    # Design your ocean")
    print("  2. surferbro-train --timesteps 1000000  # Train agent")
    print("  3. surferbro-evaluate --model <path> --render  # Watch!")
else:
    print("❌ Some issues found. Please install missing dependencies.")
print("="*60)
