"""
Manual control for SurferBro with the nice wave visualization!

Controls:
- W: Move forward (in facing direction)
- S: Move backward
- A/D or Arrow Keys: Turn left/right
- 1: Duck dive
- SPACE: Attempt to catch wave (2 second window)
- ESC: Quit
"""

import numpy as np
import pygame
import sys
from surferbro.physics.ocean_floor import OceanFloor
from surferbro.physics.wave_simulator import WaveSimulator, WavePhase
from surferbro.environments.surfer import Surfer

print("🏄 SurferBro - Manual Control (with nice waves!)")
print("=" * 60)
print("Controls:")
print("  W: Move forward (in facing direction)")
print("  S: Move backward")
print("  A/D or ←/→: Turn left/right")
print("  1: Duck dive")
print("  SPACE: Attempt to catch wave (2 second window)")
print("  ESC: Quit")
print("=" * 60)

# Create ocean with sloping beach
grid_height, grid_width = 400, 200
depth_map = np.zeros((grid_height, grid_width))

# Create sloping beach - shallow at bottom, deep at top
for iy in range(grid_height):
    depth = (iy / grid_height) * 15.0  # 0 to 15 meters
    depth_map[iy, :] = depth

ocean_floor = OceanFloor(depth_map=depth_map, cell_size=0.5)

# Create wave simulator
wave_sim = WaveSimulator(
    ocean_floor=ocean_floor,
    wave_period=12.0,  # Wave every 12 seconds
    base_height=2.0,
    randomness=0.2
)

# Create surfer (even faster!)
surfer = Surfer(mass=75.0, swim_speed=6.0, duck_dive_depth=1.0)  # 2x faster than before!

ocean_width, ocean_height = ocean_floor.get_dimensions()

# Start surfer at beach
start_x = ocean_width / 2
start_y = 5.0  # Near beach
surfer.reset((start_x, start_y))

print(f"\n🌊 Ocean: {ocean_width:.0f}m x {ocean_height:.0f}m")
print(f"🏄 Surfer starts at beach ({start_x:.0f}, {start_y:.0f})")

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SurferBro - Manual Control")
clock = pygame.time.Clock()

# Calculate zoom to fit entire ocean
zoom_x = WIDTH / ocean_width
zoom_y = HEIGHT / ocean_height
zoom = min(zoom_x, zoom_y) * 0.9

def world_to_screen(x, y):
    """Convert world coordinates to screen coordinates."""
    sx = int(x * zoom)
    sy = int(y * zoom)
    return sx, sy

# Colors
OCEAN_DEEP = (20, 40, 100)
OCEAN_SHALLOW = (50, 150, 255)
SKY = (135, 206, 235)
WAVE_BUILDING = (100, 255, 255)
WAVE_BREAKING = (255, 255, 100)
WHITE = (255, 255, 255)
SAND = (244, 228, 193)
SURFER_COLOR = (255, 100, 100)
BOARD_COLOR = (255, 255, 200)

font = pygame.font.Font(None, 24)
font_large = pygame.font.Font(None, 32)

running = True
sim_time = 0.0
dt = 0.05  # 50ms timestep
total_reward = 0.0
crash_timer = 0.0  # Crash state timer
is_crashed = False
catch_attempt_timer = 0.0  # Catch attempt timer (2 seconds)
is_attempting_catch = False

print("\n🌊 Game started! Swim toward waves with W!")

while running:
    # Update crash timer
    if is_crashed:
        crash_timer -= dt
        if crash_timer <= 0:
            is_crashed = False
            print("💪 Recovered from crash!")

    # Update catch attempt timer
    if is_attempting_catch:
        catch_attempt_timer -= dt

    # Reset controls
    swim_x = 0.0
    swim_y = 0.0
    rotate = 0.0
    duck_dive = False
    catch_wave = False  # Changed from stand_up

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    # Get keyboard state (only if not crashed!)
    if not is_crashed:
        keys = pygame.key.get_pressed()

        # Movement (WS) - RELATIVE TO FACING DIRECTION!
        # W = forward, S = backward
        forward_back = 0.0
        if keys[pygame.K_w]:
            forward_back = 1.0  # Forward
        if keys[pygame.K_s]:
            forward_back = -1.0  # Backward

        # Rotation (AD and Arrow keys)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            rotate = -1.0  # Turn left
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            rotate = 1.0  # Turn right

        # Convert forward/back to world coordinates based on facing direction
        if forward_back != 0:
            swim_x = np.cos(surfer.state.yaw) * forward_back
            swim_y = np.sin(surfer.state.yaw) * forward_back

        # Duck dive (1 key)
        if keys[pygame.K_1]:
            duck_dive = True

        # Catch wave (Space) - starts 2-second attempt!
        if keys[pygame.K_SPACE] and not is_attempting_catch:
            is_attempting_catch = True
            catch_attempt_timer = 2.0
            print("🌊 ATTEMPTING TO CATCH WAVE!")
            catch_wave = True

    # Apply controls to surfer (if not crashed)
    if not is_crashed:
        surfer.apply_rotation(rotate, dt)

        # Apply ABSOLUTE movement (not relative to rotation)
        # Directly set velocity in world coordinates
        if swim_x != 0 or swim_y != 0:
            swim_power = np.sqrt(swim_x**2 + swim_y**2)
            swim_power = min(swim_power, 1.0)
            base_speed = swim_power * surfer.swim_speed

            # Calculate movement direction
            movement_angle = np.arctan2(swim_y, swim_x)

            # Calculate angle difference between movement and facing direction
            angle_diff = movement_angle - surfer.state.yaw

            # Normalize angle to [-π, π]
            while angle_diff > np.pi:
                angle_diff -= 2 * np.pi
            while angle_diff < -np.pi:
                angle_diff += 2 * np.pi

            # Speed bonus: 100% faster when moving in facing direction
            # cos(0) = 1.0 (aligned) → 200% speed
            # cos(π/2) = 0.0 (perpendicular) → 100% speed
            # cos(π) = -1.0 (opposite) → 0% speed
            speed_multiplier = 1.0 + 1.0 * np.cos(angle_diff)
            speed = base_speed * speed_multiplier

            # Direct world-space movement
            surfer.state.vx = swim_x * speed
            surfer.state.vy = swim_y * speed

            # Surface if not duck diving
            if not duck_dive and surfer.state.z < 0:
                surfer.state.vz = 1.0
            else:
                surfer.state.vz = 0.0

        # Handle duck dive
        if duck_dive and surfer.state.duck_dive_timer <= 0:
            surfer.state.duck_dive_timer = surfer.state.duck_dive_duration
            surfer.state.is_duck_diving = True

        # Update duck dive timer
        if surfer.state.duck_dive_timer > 0:
            surfer.state.duck_dive_timer -= dt
            surfer.state.is_duck_diving = True
            surfer.state.vx *= 0.5
            surfer.state.vy *= 0.5
            target_depth = -surfer.duck_dive_depth
            if surfer.state.z > target_depth:
                surfer.state.vz = -2.0
            else:
                surfer.state.vz = 0.0
        else:
            surfer.state.is_duck_diving = False

    # Check for wave collision/interaction
    nearest_wave = wave_sim.get_nearest_wave(surfer.state.x, surfer.state.y)
    if nearest_wave and not surfer.state.is_duck_diving and not surfer.state.is_surfing and not is_crashed:
        dist_to_wave = np.linalg.norm(nearest_wave.position - np.array([surfer.state.x, surfer.state.y]))

        # Wave collision zone
        if dist_to_wave < 10.0:
            # Check if wave will break soon (within 2 seconds)
            time_until_breaking = nearest_wave.breaking_duration - nearest_wave.phase_timer if nearest_wave.phase == WavePhase.BUILDING else 0
            catchable = time_until_breaking <= 2.0 or nearest_wave.is_breaking

            # During catch attempt, try to catch if wave is catchable
            if is_attempting_catch and catchable and not nearest_wave.is_whitewash:
                # DEBUG: Print angles
                wave_angle_deg = np.degrees(nearest_wave.angle) % 360
                # TWO optimal angles (can ride left OR right)
                optimal_angle_1 = nearest_wave.angle + np.pi + np.pi / 4
                optimal_angle_2 = nearest_wave.angle + np.pi - np.pi / 4

                # Normalize both
                for opt in [optimal_angle_1, optimal_angle_2]:
                    while opt > np.pi:
                        opt -= 2 * np.pi
                    while opt < -np.pi:
                        opt += 2 * np.pi

                optimal_1_deg = np.degrees(optimal_angle_1) % 360
                optimal_2_deg = np.degrees(optimal_angle_2) % 360
                surfer_angle_deg = np.degrees(surfer.state.yaw) % 360

                def angle_diff(a, b):
                    diff = abs(a - b)
                    if diff > np.pi:
                        diff = 2 * np.pi - diff
                    return diff

                angle_diff_1 = angle_diff(surfer.state.yaw, optimal_angle_1)
                angle_diff_2 = angle_diff(surfer.state.yaw, optimal_angle_2)
                angle_diff_1_deg = np.degrees(angle_diff_1)
                angle_diff_2_deg = np.degrees(angle_diff_2)

                # Show closest optimal angle
                if angle_diff_1 < angle_diff_2:
                    print(f"🎯 Wave: {wave_angle_deg:.1f}° | Optimal: {optimal_1_deg:.1f}° (or {optimal_2_deg:.1f}°) | You: {surfer_angle_deg:.1f}° | Diff: {angle_diff_1_deg:.1f}°")
                else:
                    print(f"🎯 Wave: {wave_angle_deg:.1f}° | Optimal: {optimal_2_deg:.1f}° (or {optimal_1_deg:.1f}°) | You: {surfer_angle_deg:.1f}° | Diff: {angle_diff_2_deg:.1f}°")

                # Try to catch wave
                if surfer.try_catch_wave_angle(nearest_wave):
                    print(f"🌊 CAUGHT WAVE at {sim_time:.1f}s!")
                    total_reward += 50.0
                    # Set to being carried by wave
                    surfer.state.is_surfing = False
                    surfer.state.is_being_carried = True
                    surfer.state.is_swimming = False
                    is_attempting_catch = False
                    catch_attempt_timer = 0.0
                    print(f"🏄 RIDING WAVE!")

        # Wave hits surfer without attempting to catch - CRASH!
        if not is_attempting_catch and nearest_wave.is_breaking and dist_to_wave < 5.0:
            print(f"💥 CRASH! Hit by wave (didn't attempt to catch or duck dive)")
            is_crashed = True
            crash_timer = 5.0
            total_reward -= 15.0
            surfer.state.vx = 0
            surfer.state.vy = 0

    # Failed catch attempt - timer expired
    if is_attempting_catch and catch_attempt_timer <= 0:
        print(f"💥 CRASH! Failed to catch wave (wrong angle or timing)")
        is_crashed = True
        crash_timer = 5.0
        total_reward -= 20.0
        surfer.state.vx = 0
        surfer.state.vy = 0
        is_attempting_catch = False

    # Update physics
    wave_height = wave_sim.get_wave_height_at(surfer.state.x, surfer.state.y)
    wave_vel = wave_sim.get_wave_velocity_at(surfer.state.x, surfer.state.y)
    water_depth = ocean_floor.get_depth(surfer.state.x, surfer.state.y)

    near_wave = False
    if nearest_wave:
        dist = np.linalg.norm(nearest_wave.position - np.array([surfer.state.x, surfer.state.y]))
        near_wave = dist < nearest_wave.height * 3.0

    surfer.update_physics(wave_height, wave_vel, water_depth, dt, near_wave)
    wave_sim.step(dt)
    sim_time += dt

    # Rewards (only for wave catches, not continuous)
    # Removed continuous surfing reward to prevent infinite points

    # Clear screen
    screen.fill(SKY)

    # Draw ocean and beach
    for y in range(HEIGHT):
        world_y = y / zoom
        if world_y < ocean_height:
            depth = ocean_floor.get_depth(ocean_width / 2, world_y)

            if depth < 1.0:
                # Sandy beach
                sand_mix = depth / 1.0
                r = int(SAND[0] + (OCEAN_SHALLOW[0] - SAND[0]) * sand_mix)
                g = int(SAND[1] + (OCEAN_SHALLOW[1] - SAND[1]) * sand_mix)
                b = int(SAND[2] + (OCEAN_SHALLOW[2] - SAND[2]) * sand_mix)
            else:
                # Ocean water
                depth_ratio = min(depth / 10.0, 1.0)
                r = int(OCEAN_SHALLOW[0] + (OCEAN_DEEP[0] - OCEAN_SHALLOW[0]) * depth_ratio)
                g = int(OCEAN_SHALLOW[1] + (OCEAN_DEEP[1] - OCEAN_SHALLOW[1]) * depth_ratio)
                b = int(OCEAN_SHALLOW[2] + (OCEAN_DEEP[2] - OCEAN_SHALLOW[2]) * depth_ratio)

            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Draw waves as ANGLED WAVE SHAPES!
    for wave in wave_sim.waves:
        wx, wy = wave.x, wave.y
        sx, sy = world_to_screen(wx, wy)

        # Choose color based on phase
        if wave.is_whitewash:
            wave_color = WHITE
            foam_color = (240, 240, 240)
        elif wave.is_breaking:
            wave_color = WAVE_BREAKING
            foam_color = WHITE
        else:
            # BUILDING phase - turn GREEN if less than 1 second before it crashes (starts breaking)!
            time_until_crash = wave.building_duration - wave.phase_timer
            if time_until_crash < 1.0:
                wave_color = (0, 255, 100)  # Bright green - about to break!
                foam_color = (200, 255, 200)
            else:
                wave_color = WAVE_BUILDING
                foam_color = (200, 240, 255)

        # Wave dimensions
        wave_length = WIDTH * 1.5
        wave_height = max(int(wave.height * zoom * 6), 30)

        # Draw wave rotated by its angle
        num_points = 100
        wave_points = []

        for i in range(num_points + 1):
            t = (i / num_points - 0.5) * wave_length
            wave_progress = i / num_points
            curve = np.sin(wave_progress * np.pi)

            local_x = t
            local_y = -curve * wave_height

            rotated_x = local_x * np.cos(wave.angle) - local_y * np.sin(wave.angle)
            rotated_y = local_x * np.sin(wave.angle) + local_y * np.cos(wave.angle)

            screen_x = sx + rotated_x
            screen_y = sy + rotated_y

            wave_points.append((screen_x, screen_y))

        # Add bottom points
        if len(wave_points) > 0:
            for i in range(num_points, -1, -1):
                t = (i / num_points - 0.5) * wave_length
                local_x = t
                local_y = 5

                rotated_x = local_x * np.cos(wave.angle) - local_y * np.sin(wave.angle)
                rotated_y = local_x * np.sin(wave.angle) + local_y * np.cos(wave.angle)

                screen_x = sx + rotated_x
                screen_y = sy + rotated_y
                wave_points.append((screen_x, screen_y))

        # Draw filled wave
        if len(wave_points) > 2:
            pygame.draw.polygon(screen, wave_color, wave_points)

            # Draw foam crest
            crest_points = []
            for i in range(num_points + 1):
                t = (i / num_points - 0.5) * wave_length
                wave_progress = i / num_points
                curve = np.sin(wave_progress * np.pi)

                local_x = t
                local_y = -curve * wave_height

                rotated_x = local_x * np.cos(wave.angle) - local_y * np.sin(wave.angle)
                rotated_y = local_x * np.sin(wave.angle) + local_y * np.cos(wave.angle)

                crest_points.append((sx + rotated_x, sy + rotated_y))

            if len(crest_points) > 1:
                pygame.draw.lines(screen, foam_color, False, crest_points, max(wave_height // 4, 3))

                # Foam texture
                if wave.is_whitewash:
                    for i in range(0, len(crest_points), 3):
                        if i < len(crest_points):
                            x, y = crest_points[i]
                            pygame.draw.circle(screen, WHITE, (int(x), int(y)), max(5, wave_height // 4))

    # Draw surfer (MUCH BIGGER!)
    sx, sy = world_to_screen(surfer.state.x, surfer.state.y)

    # Draw board (5x bigger)
    board_length = int(10.0 * zoom)  # 5x bigger!
    board_width = int(2.5 * zoom)    # 5x bigger!
    if board_length > 5:
        angle_deg = np.degrees(surfer.state.yaw)
        board_surf = pygame.Surface((board_length, board_width), pygame.SRCALPHA)
        pygame.draw.rect(board_surf, BOARD_COLOR, board_surf.get_rect(), border_radius=5)
        rotated_board = pygame.transform.rotate(board_surf, -angle_deg)
        board_rect = rotated_board.get_rect(center=(sx, sy))
        screen.blit(rotated_board, board_rect)

    # Draw surfer body (5x bigger)
    surfer_radius = max(int(2.0 * zoom), 10)  # 5x bigger!
    pygame.draw.circle(screen, SURFER_COLOR, (sx, sy), surfer_radius)

    # Direction indicators - shows BOTH OPTIMAL wave-catching angles (GREEN arrows)
    if nearest_wave and np.linalg.norm(nearest_wave.position - np.array([surfer.state.x, surfer.state.y])) < 50.0:
        # Calculate TWO optimal angles (can ride left OR right along wave face)
        # Angle 1: opposite direction + 45°
        optimal_angle_1 = nearest_wave.angle + np.pi + np.pi / 4
        while optimal_angle_1 > np.pi:
            optimal_angle_1 -= 2 * np.pi
        while optimal_angle_1 < -np.pi:
            optimal_angle_1 += 2 * np.pi

        # Angle 2: opposite direction - 45°
        optimal_angle_2 = nearest_wave.angle + np.pi - np.pi / 4
        while optimal_angle_2 > np.pi:
            optimal_angle_2 -= 2 * np.pi
        while optimal_angle_2 < -np.pi:
            optimal_angle_2 += 2 * np.pi

        # Draw BOTH green arrows
        for opt_angle in [optimal_angle_1, optimal_angle_2]:
            dx = np.cos(opt_angle) * surfer_radius * 5
            dy = np.sin(opt_angle) * surfer_radius * 5
            pygame.draw.line(screen, (0, 255, 0), (sx, sy), (sx + int(dx), sy + int(dy)), 4)

    # Status text
    if is_attempting_catch:
        state = f"ATTEMPTING TO CATCH! ({catch_attempt_timer:.1f}s)"
        status_color = (255, 200, 0)  # Orange
    elif is_crashed:
        state = f"CRASHED! ({crash_timer:.1f}s)"
        status_color = (255, 0, 0)  # Red
    elif surfer.state.is_surfing:
        state = "SURFING!"
        status_color = (0, 255, 0)  # Green
    elif surfer.state.is_being_carried:
        state = "BEING CARRIED"
        status_color = (255, 255, 0)  # Yellow
    elif surfer.state.is_duck_diving:
        state = "DUCK DIVING"
        status_color = (100, 200, 255)  # Cyan
    else:
        state = "SWIMMING"
        status_color = WHITE

    # Info overlay
    info_lines = [
        f"Time: {sim_time:.1f}s | Reward: {total_reward:.0f}",
        f"Pos: ({surfer.state.x:.1f}, {surfer.state.y:.1f})",
        f"State: {state}",
        f"Waves: {len(wave_sim.waves)}",
    ]

    # Add angle info if near a wave
    angle_status_text = None
    angle_status_color = WHITE
    if nearest_wave:
        dist = np.linalg.norm(nearest_wave.position - np.array([surfer.state.x, surfer.state.y]))
        if dist < 50.0:  # Show from farther away
            wave_angle_deg = np.degrees(nearest_wave.angle)
            optimal_angle = nearest_wave.angle + np.pi / 4
            while optimal_angle > np.pi:
                optimal_angle -= 2 * np.pi
            while optimal_angle < -np.pi:
                optimal_angle += 2 * np.pi
            optimal_angle_deg = np.degrees(optimal_angle)
            surfer_angle_deg = np.degrees(surfer.state.yaw)

            # Calculate angle difference
            def angle_diff(a, b):
                diff = abs(a - b)
                if diff > np.pi:
                    diff = 2 * np.pi - diff
                return diff

            angle_difference = angle_diff(surfer.state.yaw, optimal_angle)
            angle_diff_deg = np.degrees(angle_difference)

            # Color code based on how close
            if angle_diff_deg <= 5:
                angle_status_color = (0, 255, 0)  # Green - perfect!
                angle_status_text = f"TARGET ANGLE: {optimal_angle_deg:.0f}° | YOU: {surfer_angle_deg:.0f}° | ✓ PERFECT!"
            elif angle_diff_deg <= 15:
                angle_status_color = (255, 255, 0)  # Yellow - good enough
                angle_status_text = f"TARGET ANGLE: {optimal_angle_deg:.0f}° | YOU: {surfer_angle_deg:.0f}° | ✓ GOOD (off by {angle_diff_deg:.0f}°)"
            else:
                angle_status_color = (255, 100, 100)  # Red - too far
                angle_status_text = f"TARGET ANGLE: {optimal_angle_deg:.0f}° | YOU: {surfer_angle_deg:.0f}° | ✗ OFF BY {angle_diff_deg:.0f}°"

    # Draw semi-transparent background for text
    hud_height = len(info_lines) * 25 + 10
    if angle_status_text:
        hud_height += 40  # Extra space for angle status
    hud_bg = pygame.Surface((WIDTH - 20, hud_height))
    hud_bg.set_alpha(200)
    hud_bg.fill((0, 0, 0))
    screen.blit(hud_bg, (10, 10))

    for i, line in enumerate(info_lines):
        text = font.render(line, True, WHITE)
        screen.blit(text, (15, 15 + i * 25))

    # Draw angle status prominently if near a wave
    if angle_status_text:
        y_offset = 15 + len(info_lines) * 25 + 5
        angle_text = font_large.render(angle_status_text, True, angle_status_color)
        screen.blit(angle_text, (15, y_offset))

    # Update display
    pygame.display.flip()
    clock.tick(30)  # 30 FPS

pygame.quit()
print(f"\n✅ Game ended! Total reward: {total_reward:.0f}")
print("Thanks for playing!")
