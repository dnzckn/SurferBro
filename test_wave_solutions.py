#!/usr/bin/env python3
"""Test script to verify wave catching recognizes both solutions."""

import numpy as np
from surferbro.environments.surfer import Surfer
from surferbro.physics.wave_simulator import Wave, WavePhase

def test_wave_catching_both_solutions():
    """Test that surfer can catch waves from both optimal angles."""

    # Create a surfer
    surfer = Surfer()
    surfer.reset((50.0, 50.0))

    # Create a test wave at various angles
    test_wave_angles = [
        0.0,           # Wave coming straight (north)
        np.pi / 4,     # Wave at 45° northeast
        np.pi / 2,     # Wave at 90° east
        -np.pi / 4,    # Wave at -45° southeast
        np.pi,         # Wave from south
    ]

    print("=" * 70)
    print("TESTING WAVE CATCHING WITH 2 SOLUTIONS")
    print("=" * 70)

    for wave_angle in test_wave_angles:
        print(f"\n📊 Testing wave at angle: {np.degrees(wave_angle):.1f}°")

        # Create wave
        wave = Wave(
            x=50.0,
            y=50.0,
            height=2.0,
            max_height=2.0,
            speed=2.4,
            period=8.0,
            angle=wave_angle,
            phase=WavePhase.BREAKING,
            phase_timer=2.0,
            building_duration=2.0,
            breaking_duration=5.0,
            whitewash_duration=10.0
        )

        # Calculate the two optimal angles for catching this wave
        optimal_angle_1 = wave_angle + np.pi + np.pi / 4  # 180° + 45°
        optimal_angle_2 = wave_angle + np.pi - np.pi / 4  # 180° - 45°

        # Normalize
        while optimal_angle_1 > np.pi:
            optimal_angle_1 -= 2 * np.pi
        while optimal_angle_1 < -np.pi:
            optimal_angle_1 += 2 * np.pi

        while optimal_angle_2 > np.pi:
            optimal_angle_2 -= 2 * np.pi
        while optimal_angle_2 < -np.pi:
            optimal_angle_2 += 2 * np.pi

        print(f"  ├─ Optimal angle 1 (ride right): {np.degrees(optimal_angle_1):.1f}°")
        print(f"  ├─ Optimal angle 2 (ride left):  {np.degrees(optimal_angle_2):.1f}°")

        # Test Solution 1: Surfer approaches from optimal_angle_1
        print(f"  │")
        print(f"  ├─ Testing SOLUTION 1 (surfer at {np.degrees(optimal_angle_1):.1f}°)")
        surfer.reset((50.0, 50.0))
        surfer.state.yaw = optimal_angle_1
        surfer.state.vx = 1.0
        surfer.state.vy = 0.5

        caught_1 = surfer.try_catch_wave_angle(wave)
        print(f"  │  └─ Caught: {caught_1} ✓" if caught_1 else f"  │  └─ Caught: {caught_1} ✗")

        # Test Solution 2: Surfer approaches from optimal_angle_2
        print(f"  │")
        print(f"  ├─ Testing SOLUTION 2 (surfer at {np.degrees(optimal_angle_2):.1f}°)")
        surfer.reset((50.0, 50.0))
        surfer.state.yaw = optimal_angle_2
        surfer.state.vx = 1.0
        surfer.state.vy = 0.5

        caught_2 = surfer.try_catch_wave_angle(wave)
        print(f"  │  └─ Caught: {caught_2} ✓" if caught_2 else f"  │  └─ Caught: {caught_2} ✗")

        # Test tolerance: ±15° from solution 1
        print(f"  │")
        print(f"  └─ Testing TOLERANCE (±15° from solution 1)")
        tolerance_angle = optimal_angle_1 + np.radians(10)  # Should be within tolerance
        surfer.reset((50.0, 50.0))
        surfer.state.yaw = tolerance_angle
        surfer.state.vx = 1.0
        surfer.state.vy = 0.5

        caught_tolerance = surfer.try_catch_wave_angle(wave)
        print(f"     └─ Caught at +10° offset: {caught_tolerance} ✓" if caught_tolerance else f"     └─ Caught at +10° offset: {caught_tolerance} ✗")

        # Verify both solutions work
        if caught_1 and caught_2:
            print(f"  ✓ PASS: Both solutions recognized!")
        else:
            print(f"  ✗ FAIL: Both solutions NOT recognized!")

if __name__ == "__main__":
    test_wave_catching_both_solutions()
    print("\n" + "=" * 70)
    print("Test complete!")
    print("=" * 70)
