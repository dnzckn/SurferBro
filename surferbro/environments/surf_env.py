"""Gymnasium environment for surfing simulation."""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Dict, Tuple, Any
from pathlib import Path

from surferbro.physics.wave_simulator import WaveSimulator
from surferbro.physics.ocean_floor import OceanFloor
from surferbro.oceanscope.mesh_converter import OceanMeshConverter
from surferbro.environments.surfer import Surfer
from surferbro.environments.jellyfish import JellyfishSwarm
from surferbro.utils.config import Config


class SurfEnvironment(gym.Env):
    """
    Gymnasium environment for learning to surf.

    The agent must:
    1. Swim from shore to the wave zone
    2. Avoid jellyfish obstacles
    3. Catch a wave with correct board orientation
    4. Surf the wave as long as possible
    """

    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}

    def __init__(
        self,
        ocean_design: Optional[str] = None,
        config_path: Optional[str] = None,
        render_mode: Optional[str] = None
    ):
        """
        Initialize environment.

        Args:
            ocean_design: Path to OceanScope design file (optional)
            config_path: Path to config file (optional)
            render_mode: Rendering mode
        """
        super().__init__()

        # Load configuration
        self.config = Config(config_path)
        self.render_mode = render_mode

        # Load or create ocean
        if ocean_design and Path(ocean_design).exists():
            self._load_ocean_design(ocean_design)
        else:
            self._create_default_ocean()

        # Initialize components
        self.surfer = Surfer(
            mass=self.config.get('surfer.mass'),
            swim_speed=self.config.get('surfer.swim_speed'),
            duck_dive_depth=self.config.get('surfer.duck_dive_depth'),
            board_length=self.config.get('surfer.board_length'),
            board_width=self.config.get('surfer.board_width'),
            board_mass=self.config.get('surfer.board_mass')
        )

        self.wave_simulator = WaveSimulator(
            ocean_floor=self.ocean_floor,
            wave_period=self.config.get('waves.period'),
            base_height=self.config.get('waves.base_height'),
            direction=self.config.get('waves.direction'),
            pier_positions=self.pier_positions,
            randomness=self.config.get('waves.randomness'),
            breaking_depth_ratio=self.config.get('waves.breaking_depth_ratio'),
            whitewash_duration=self.config.get('waves.whitewash_duration')
        )

        ocean_width, ocean_height = self.ocean_floor.get_dimensions()
        self.jellyfish_swarm = JellyfishSwarm(
            count=self.config.get('jellyfish.count'),
            ocean_width=ocean_width,
            ocean_height=ocean_height,
            min_depth=self.config.get('jellyfish.min_depth'),
            max_depth=self.config.get('jellyfish.max_depth'),
            speed=self.config.get('jellyfish.speed'),
            radius=self.config.get('jellyfish.radius')
        )

        # Define action and observation spaces
        self._define_spaces()

        # Episode tracking
        self.timestep = 0
        self.max_episode_steps = self.config.get('simulation.max_episode_steps')
        self.dt = self.config.get('simulation.timestep')

        # Rewards tracking
        self.total_surf_time = 0.0
        self.reached_wave_zone = False
        self.caught_wave = False

        # Rendering
        self.renderer = None

    def _load_ocean_design(self, design_path: str):
        """Load ocean from OceanScope design."""
        converter = OceanMeshConverter(design_path)
        sim_data = converter.get_simulation_data()

        self.ocean_floor = OceanFloor(sim_data['depth_map'])
        self.pier_positions = sim_data['pier_positions']

    def _create_default_ocean(self):
        """Create default ocean when no design is provided."""
        width = int(self.config.get('ocean.width') / 0.5)
        length = int(self.config.get('ocean.length') / 0.5)

        # Simple sloping ocean floor
        depth_map = np.zeros((length, width))
        for y in range(length):
            # Depth increases with distance from shore
            depth = (y / length) * self.config.get('ocean.max_depth')
            depth_map[y, :] = depth

        self.ocean_floor = OceanFloor(depth_map)
        self.pier_positions = []

    def _define_spaces(self):
        """Define observation and action spaces."""
        # Observation space:
        # - Surfer state (18 values): x, y, z, vx, vy, vz, roll, pitch, yaw,
        #                             roll_rate, pitch_rate, yaw_rate,
        #                             is_swimming, is_duck_diving, is_being_carried,
        #                             is_surfing, is_whitewash_carry, wave_carry_timer
        # - Wave info (5 values): height, vx, vy, distance to nearest wave, wave is breaking
        # - Jellyfish info (3 values): dx, dy, distance
        # - Environment info (3 values): depth, distance to shore, in wave zone
        # - Angle info (3 values): angle_to_optimal, can_stand_up, nearest_wave_angle
        obs_dim = 18 + 5 + 3 + 3 + 3  # Total: 32 dimensions

        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(obs_dim,),
            dtype=np.float32
        )

        # NEW 7D Action space for wave-catching mechanics:
        # action[0] = swim_x       # -1 to 1 (left/right)
        # action[1] = swim_y       # -1 to 1 (back/forward)
        # action[2] = rotate       # -1 to 1 → convert to ±5° increments
        # action[3] = duck_dive    # >0.5 triggers duck dive
        # action[4] = stand_up     # >0.5 triggers stand up attempt
        # action[5] = lean         # -1 to 1 (while surfing)
        # action[6] = turn         # -1 to 1 (while surfing)
        self.action_space = spaces.Box(
            low=-1.0,
            high=1.0,
            shape=(7,),
            dtype=np.float32
        )

    def _calculate_optimal_angle(self, wave) -> float:
        """
        Calculate optimal surfer angle for catching wave.

        According to wave-catching mechanics:
        - Wave moves at wave.angle
        - Optimal surfer angle = wave.angle + 45°

        Args:
            wave: Wave object

        Returns:
            Optimal surfer yaw angle in radians
        """
        if wave is None:
            return 0.0

        # Optimal angle is opposite wave direction + 45° (to ride WITH the wave)
        optimal_angle = wave.angle + np.pi + np.pi / 4  # 180° + 45°

        # Normalize to [-π, π]
        while optimal_angle > np.pi:
            optimal_angle -= 2 * np.pi
        while optimal_angle < -np.pi:
            optimal_angle += 2 * np.pi

        return optimal_angle

    def _calculate_angle_difference(self, angle1: float, angle2: float) -> float:
        """
        Calculate smallest difference between two angles.

        Args:
            angle1: First angle in radians
            angle2: Second angle in radians

        Returns:
            Angle difference in radians (always positive, 0 to π)
        """
        diff = abs(angle1 - angle2)
        if diff > np.pi:
            diff = 2 * np.pi - diff
        return diff

    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Reset environment to initial state."""
        super().reset(seed=seed)

        # Reset components
        ocean_width, ocean_height = self.ocean_floor.get_dimensions()

        # Find a good starting position (shallow water near beach)
        start_x = ocean_width / 2
        start_y = None

        # Search for shallow water (< 1m depth) to start in
        for y in range(int(ocean_height)):
            y_pos = float(y) * 0.5  # Convert grid to meters
            depth = self.ocean_floor.get_depth(start_x, y_pos)
            if 0.3 < depth < 1.5:  # Shallow water, good starting point
                start_y = y_pos
                break

        # If no shallow water found, start near shore
        if start_y is None:
            start_y = min(10.0, ocean_height * 0.2)

        self.surfer.reset((start_x, start_y))
        self.jellyfish_swarm.reset()
        self.wave_simulator = WaveSimulator(
            ocean_floor=self.ocean_floor,
            wave_period=self.config.get('waves.period'),
            base_height=self.config.get('waves.base_height'),
            direction=self.config.get('waves.direction'),
            pier_positions=self.pier_positions,
            randomness=self.config.get('waves.randomness'),
            breaking_depth_ratio=self.config.get('waves.breaking_depth_ratio'),
            whitewash_duration=self.config.get('waves.whitewash_duration')
        )

        # Reset tracking
        self.timestep = 0
        self.total_surf_time = 0.0
        self.reached_wave_zone = False
        self.caught_wave = False

        observation = self._get_observation()
        info = self._get_info()

        return observation, info

    def step(
        self,
        action: np.ndarray
    ) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """
        Execute one step in the environment.

        Args:
            action: Action array [swim_x, swim_y, rotate, duck_dive, stand_up, lean, turn]

        Returns:
            observation, reward, terminated, truncated, info
        """
        self.timestep += 1

        # Get current state
        surfer_x = self.surfer.state.x
        surfer_y = self.surfer.state.y
        surfer_z = self.surfer.state.z

        # Parse 7D action space
        swim_x = action[0]          # -1 to 1 (left/right)
        swim_y = action[1]          # -1 to 1 (back/forward)
        rotate = action[2]          # -1 to 1 (rotation in 5° increments)
        duck_dive = action[3] > 0.5 # >0.5 triggers duck dive
        stand_up = action[4] > 0.5  # >0.5 triggers stand up
        lean = action[5]            # -1 to 1 (while surfing)
        turn = action[6]            # -1 to 1 (while surfing)

        # Apply rotation (5° increments) - works in all states
        self.surfer.apply_rotation(rotate, self.dt)

        # Apply action based on current phase
        if self.surfer.state.is_swimming:
            # Swimming phase: use swim_x, swim_y for directional swimming
            self.surfer.apply_swimming_action_2d(swim_x, swim_y, duck_dive, self.dt)

            # Check if trying to catch wave
            nearest_wave = self.wave_simulator.get_nearest_wave(surfer_x, surfer_y)
            if nearest_wave and nearest_wave.is_breaking and not nearest_wave.is_whitewash:
                dist_to_wave = np.linalg.norm(
                    nearest_wave.position - np.array([surfer_x, surfer_y])
                )
                # Wave influence radius
                wave_radius = 5.0

                if dist_to_wave < wave_radius:
                    # Try to catch wave with angle check!
                    if self.surfer.try_catch_wave_angle(nearest_wave):
                        self.caught_wave = True

        elif self.surfer.state.is_being_carried:
            # Being carried by wave: allow rotation and stand up attempt
            # Rotation already applied above

            # Try to stand up if triggered
            if stand_up:
                nearest_wave = self.wave_simulator.get_nearest_wave(surfer_x, surfer_y)
                if nearest_wave:
                    # Calculate optimal angle for this wave
                    optimal_angle = self._calculate_optimal_angle(nearest_wave)
                    angle_diff = self._calculate_angle_difference(self.surfer.state.yaw, optimal_angle)

                    # Try to stand up with angle check (±15° tolerance)
                    success, message = self.surfer.try_stand_up_angle(nearest_wave, angle_diff)
                    if not success:
                        # Crashed! Will be handled as wipeout
                        pass

        elif self.surfer.state.is_whitewash_carry:
            # Being carried by whitewash: can duck dive to escape
            if duck_dive:
                self.surfer.apply_swimming_action_2d(0.0, 0.0, duck_dive, self.dt)

        elif self.surfer.state.is_surfing:
            # Surfing phase: use lean and turn
            self.surfer.apply_surfing_control(lean, turn, self.dt)
            self.total_surf_time += self.dt

        # Update physics
        wave_height = self.wave_simulator.get_wave_height_at(surfer_x, surfer_y)
        wave_vel = self.wave_simulator.get_wave_velocity_at(surfer_x, surfer_y)
        water_depth = self.ocean_floor.get_depth(surfer_x, surfer_y)

        # Check if near a wave (for collision/pushback)
        near_wave = False
        nearest_wave = self.wave_simulator.get_nearest_wave(surfer_x, surfer_y)
        if nearest_wave:
            dist_to_wave = np.linalg.norm(
                nearest_wave.position - np.array([surfer_x, surfer_y])
            )
            # Wave collision radius based on wave height
            collision_radius = nearest_wave.height * 3.0
            near_wave = dist_to_wave < collision_radius

        self.surfer.update_physics(wave_height, wave_vel, water_depth, self.dt, near_wave)
        self.wave_simulator.step(self.dt)
        self.jellyfish_swarm.update(self.dt)

        # Check wave zone
        if self.wave_simulator.is_in_wave_zone(surfer_x, surfer_y):
            self.reached_wave_zone = True

        # Calculate reward (pass wave collision info for duck dive rewards)
        reward = self._calculate_reward(near_wave=near_wave)

        # Check termination conditions
        terminated = False
        truncated = False

        # Wipeout (NO LONGER TERMINATES - starts whitewash carry!)
        if self.surfer.check_wipeout(wave_height):
            reward += self.config.get('rewards.fall_penalty')
            # Episode continues - surfer gets carried by whitewash!

        # Jellyfish collision
        if self.jellyfish_swarm.check_collision(surfer_x, surfer_y, surfer_z):
            reward += self.config.get('rewards.jellyfish.penalty')
            terminated = True

        # Out of bounds
        ocean_width, ocean_height = self.ocean_floor.get_dimensions()
        if surfer_x < 0 or surfer_x > ocean_width or surfer_y < 0 or surfer_y > ocean_height:
            terminated = True

        # Max steps
        if self.timestep >= self.max_episode_steps:
            truncated = True

        observation = self._get_observation()
        info = self._get_info()

        return observation, reward, terminated, truncated, info

    def _get_observation(self) -> np.ndarray:
        """Get current observation."""
        surfer_x = self.surfer.state.x
        surfer_y = self.surfer.state.y

        # Surfer state (18 values)
        surfer_obs = self.surfer.get_observation()

        # Wave information (5 values)
        wave_height = self.wave_simulator.get_wave_height_at(surfer_x, surfer_y)
        wave_vx, wave_vy = self.wave_simulator.get_wave_velocity_at(surfer_x, surfer_y)
        nearest_wave = self.wave_simulator.get_nearest_wave(surfer_x, surfer_y)

        if nearest_wave:
            dist_to_wave = np.linalg.norm(
                nearest_wave.position - np.array([surfer_x, surfer_y])
            )
            is_breaking = float(nearest_wave.is_breaking or nearest_wave.is_whitewash)
        else:
            dist_to_wave = 100.0
            is_breaking = 0.0

        wave_obs = np.array([wave_height, wave_vx, wave_vy, dist_to_wave, is_breaking])

        # Jellyfish info (3 values)
        jelly_obs = self.jellyfish_swarm.get_state_vector(surfer_x, surfer_y)

        # Environment info (3 values)
        depth = self.ocean_floor.get_depth(surfer_x, surfer_y)
        ocean_width, ocean_height = self.ocean_floor.get_dimensions()
        dist_to_shore = surfer_y  # Distance from shore (y=0)
        in_wave_zone = float(self.wave_simulator.is_in_wave_zone(surfer_x, surfer_y))

        env_obs = np.array([depth, dist_to_shore, in_wave_zone])

        # NEW: Angle information for wave-catching (3 values)
        if nearest_wave:
            # Calculate optimal angle for this wave (45° to wave direction)
            optimal_angle = self._calculate_optimal_angle(nearest_wave)

            # Angle difference from optimal (how far off surfer is)
            angle_to_optimal = self._calculate_angle_difference(
                self.surfer.state.yaw, optimal_angle
            )

            # Can stand up? (being carried + within ±15° + carried long enough)
            catch_tolerance = np.radians(15)  # ±15 degrees
            within_angle = angle_to_optimal < catch_tolerance
            carried_enough = self.surfer.state.wave_carry_timer >= self.surfer.state.required_carry_duration
            can_stand_up = float(
                self.surfer.state.is_being_carried and within_angle and carried_enough
            )

            # Wave's approach angle
            nearest_wave_angle = nearest_wave.angle
        else:
            angle_to_optimal = 0.0
            can_stand_up = 0.0
            nearest_wave_angle = 0.0

        angle_obs = np.array([angle_to_optimal, can_stand_up, nearest_wave_angle])

        # Concatenate all observations (18 + 5 + 3 + 3 + 3 = 32)
        observation = np.concatenate([surfer_obs, wave_obs, jelly_obs, env_obs, angle_obs])

        return observation.astype(np.float32)

    def _calculate_reward(self, near_wave: bool = False) -> float:
        """Calculate reward for current step.

        Args:
            near_wave: Whether surfer is near a wave (for duck dive rewards)
        """
        reward = 0.0

        # Time penalty (encourages efficiency)
        reward += self.config.get('rewards.time_penalty')

        # Get nearest wave for angle-based rewards
        surfer_x = self.surfer.state.x
        surfer_y = self.surfer.state.y
        nearest_wave = self.wave_simulator.get_nearest_wave(surfer_x, surfer_y)

        # NEW: Angle-based positioning rewards
        if nearest_wave and (self.surfer.state.is_swimming or self.surfer.state.is_being_carried):
            optimal_angle = self._calculate_optimal_angle(nearest_wave)
            angle_diff = self._calculate_angle_difference(self.surfer.state.yaw, optimal_angle)

            # Reward for correct angle (±15°)
            if angle_diff < np.radians(15):
                reward += 0.5 * self.dt  # Continuous feedback

            # Perfect angle bonus (±5°)
            if angle_diff < np.radians(5):
                reward += 1.0 * self.dt  # Extra bonus for precision

        # Reward for moving toward waves (forward progress)
        if self.surfer.state.is_swimming and not self.surfer.state.is_duck_diving:
            # Reward for velocity in +Y direction (toward waves)
            if self.surfer.state.vy > 0:
                reward += self.surfer.state.vy * 0.5 * self.dt  # Immediate feedback

        # Reward for reaching wave zone
        if self.reached_wave_zone and self.timestep < 100:
            reward += self.config.get('rewards.reach_wave_zone')
            self.reached_wave_zone = False  # Only reward once

        # BIG reward for catching wave (starting to be carried)
        if self.caught_wave:
            reward += 50.0  # Big one-time reward!
            self.caught_wave = False

        # Reward for being carried (learning to wait before standing)
        if self.surfer.state.is_being_carried:
            reward += 0.5 * self.dt  # Small reward for being patient

        # BIG reward for surfing (after successfully standing up)
        if self.surfer.state.is_surfing:
            reward += 10.0 * self.dt  # 10 points per second of surfing!

        # Duck dive success (avoiding wave pushback)
        if self.surfer.state.is_duck_diving and near_wave:
            # Reward for being underwater when wave is near (smart timing!)
            reward += self.config.get('rewards.duck_dive_success') * self.dt

        # Reward for escaping whitewash via duck dive
        if self.surfer.state.is_duck_diving and not self.surfer.state.is_whitewash_carry:
            # Small reward for using duck dive effectively
            reward += 1.0 * self.dt

        # Penalty for being stuck in whitewash (encourages escape)
        if self.surfer.state.is_whitewash_carry:
            reward -= 2.0 * self.dt  # Continuous penalty

        # Bonus for distance traveled while surfing
        if self.surfer.state.is_surfing:
            speed = np.sqrt(self.surfer.state.vx**2 + self.surfer.state.vy**2)
            reward += speed * 0.1 * self.dt

        return reward

    def _get_info(self) -> Dict[str, Any]:
        """Get additional info about current state."""
        return {
            'timestep': self.timestep,
            'surfer_position': (self.surfer.state.x, self.surfer.state.y),
            'is_swimming': self.surfer.state.is_swimming,
            'is_surfing': self.surfer.state.is_surfing,
            'total_surf_time': self.total_surf_time,
            'num_waves': len(self.wave_simulator.waves)
        }

    def render(self):
        """Render the environment."""
        if self.render_mode == "human" or self.render_mode == "rgb_array":
            if self.renderer is None:
                from surferbro.visualization.renderer import SurfRenderer
                self.renderer = SurfRenderer(
                    self.ocean_floor,
                    self.config.get('visualization.window_width'),
                    self.config.get('visualization.window_height')
                )

            return self.renderer.render(
                self.surfer,
                self.wave_simulator,
                self.jellyfish_swarm,
                mode=self.render_mode
            )

    def close(self):
        """Clean up resources."""
        if self.renderer is not None:
            self.renderer.close()
            self.renderer = None
