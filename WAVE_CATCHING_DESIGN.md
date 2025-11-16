# Wave-Catching Mechanics Design

## Overview
Upgrade SurferBro to realistic wave-catching with angle-based positioning and precision timing.

## Action Space Changes
**Current**: 4D action space
**New**: 7D action space

```python
action[0] = swim_x       # -1 to 1 (left/right)
action[1] = swim_y       # -1 to 1 (back/forward)
action[2] = rotate       # -1 to 1 → convert to ±5° increments
action[3] = duck_dive    # >0.5 triggers duck dive
action[4] = stand_up     # >0.5 triggers stand up attempt
action[5] = lean         # -1 to 1 (while surfing)
action[6] = turn         # -1 to 1 (while surfing)
```

## Wave-Catching Math

### Golden Angle Formula
```
wave_direction = θ          # Wave's approach angle to beach
wave_front_angle = θ + 90°  # Perpendicular to movement
optimal_surfer_angle = θ + 45°  # 45° to wave front

Examples:
- Wave at 0° (straight):  surfer faces 45°
- Wave at 45° (diagonal): surfer faces 90° (toward beach)
- Wave at -45°:           surfer faces 0° (parallel to beach)
```

### Angle Tolerance
- **Catching window**: ±15° from optimal angle
- **Perfect catch**: Within ±5° (bonus reward)
- **Stand-up timing**: Must be within tolerance when standing

## State Machine Updates

```
SWIMMING → (duck_dive) → DUCK_DIVING (3s) → SWIMMING
    ↓
(wave contact + correct angle)
    ↓
BEING_CARRIED (1-3s based on wave size)
    ↓
(stand_up + correct angle) → SURFING
    ↓
(crash or whitewash) → WHITEWASH_CARRY → (duck_dive) → SWIMMING
```

## Physics Changes

### 1. Wave Interaction (in `surfer.py`)
```python
def check_wave_contact(surfer_pos, wave, dt):
    """Check if surfer is in wave influence zone"""
    distance = calculate_distance(surfer_pos, wave.position)
    if distance < wave_influence_radius:
        angle_diff = calculate_angle_difference(
            surfer.yaw,
            wave.angle + np.pi/4  # 45° to wave
        )
        return True, angle_diff
    return False, 0
```

### 2. Wave Push-Back
```python
# If hit wave at wrong angle:
if not catching and in_wave_zone:
    # Push surfer in wave direction until whitewash
    push_force = wave.speed * wave.height * 0.5
    surfer.vx += push_force * sin(wave.angle)
    surfer.vy += push_force * cos(wave.angle)
```

### 3. Whitewash Carry
```python
# When wave crashes or surfer wipes out:
if wave.is_whitewash and surfer.contact:
    surfer.is_whitewash_carry = True
    # Push back toward beach slowly
    carry_velocity = wave.speed * 0.3
```

### 4. Rotation Control
```python
def apply_rotation(rotate_action):
    """Apply 5° rotation increments"""
    if abs(rotate_action) > 0.3:  # Deadzone
        direction = 1 if rotate_action > 0 else -1
        surfer.yaw += direction * np.radians(5)  # 5° increment
```

## Reward Function

### Per-Step Rewards
```python
rewards = {
    # Positioning
    'correct_angle': +0.5 if within_15_degrees else 0,
    'perfect_angle': +1.0 if within_5_degrees else 0,

    # Actions
    'successful_catch': +50.0,  # One-time
    'successful_standup': +30.0,  # One-time
    'surfing': +10.0 per second,

    # Penalties
    'wrong_angle_catch': -10.0,
    'too_early_standup': -20.0,
    'too_late_standup': -20.0,
    'crash': -30.0,
    'whitewash_carry': -2.0 per second,

    # Survival
    'time_penalty': -0.1 per step,
}
```

## Observation Space Updates

Add to observation (keep existing 29 values):
```python
obs[29] = angle_to_optimal  # Angle difference from optimal catch angle
obs[30] = can_stand_up      # Boolean: in catch window with correct angle
obs[31] = nearest_wave_angle  # Wave's approach angle
```
**New total**: 32 dimensions

## File Modifications

### 1. `surferbro/environments/surf_env.py`
- Update `_define_spaces()`: 4D → 7D actions, 29D → 32D obs
- Update `step()`: Parse new actions
- Update `_calculate_reward()`: Add angle-based rewards
- Add `_calculate_optimal_angle(wave)` helper
- Update `reset()`: Spawn at beach center

### 2. `surferbro/environments/surfer.py`
- Add `apply_rotation(rotate_action)` method
- Update `apply_swimming_action()`: Use swim_x, swim_y
- Add `attempt_standup(wave, angle_tolerance)` method
- Update wave interaction physics

### 3. `surferbro/physics/wave_simulator.py`
- Already has `wave.angle` ✓
- Add `get_wave_influence_at(x, y)` for push forces

### 4. `config.yaml`
- Add rotation_step: 5.0 (degrees)
- Add catch_angle_tolerance: 15.0
- Add perfect_angle_tolerance: 5.0

## Implementation Order

1. ✅ Wave angle system (DONE - waves have angles)
2. Update action space (7D)
3. Add rotation control (5° increments)
4. Implement angle calculation helpers
5. Update wave catching logic
6. Add stand-up mechanics with angle check
7. Implement push-back physics
8. Update reward function
9. Test with training

## Testing Plan

1. **Manual Test**: Spawn wave, swim to it, check angle calculation
2. **Catch Test**: Verify correct angle = catch, wrong angle = push
3. **Stand-up Test**: Verify timing and angle requirements
4. **Training Test**: Run 10K steps, verify agent learns to position correctly

## Success Metrics

After 100K training steps, agent should:
- [ ] Swim from beach to wave zone (>80% of time)
- [ ] Position at correct angle (>60% of time)
- [ ] Catch waves successfully (>40% of time)
- [ ] Stand up with correct timing (>20% of time)
- [ ] Ride waves briefly (>10% of time)

After 1M steps:
- [ ] Consistent wave catching (>80%)
- [ ] Good stand-up timing (>60%)
- [ ] Extended rides (average 3+ seconds)
