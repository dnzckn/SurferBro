"""FIXED Pygame renderer with proper beach, waves, and scale."""

import pygame
import numpy as np
from typing import Optional
import sys

from surferbro.physics.ocean_floor import OceanFloor
from surferbro.physics.wave_simulator import WaveSimulator
from surferbro.environments.surfer import Surfer
from surferbro.environments.jellyfish import JellyfishSwarm


class SurfRendererFixed:
    """
    FIXED renderer with:
    - Proper beach/sand visualization
    - Visible waves
    - Bigger surfer
    - Fixed camera OR reference grid
    - Better scale
    """

    def __init__(
        self,
        ocean_floor: OceanFloor,
        ocean_design_data: dict = None,
        width: int = 1280,
        height: int = 720,
        camera_mode: str = "fixed"  # "fixed" or "follow"
    ):
        """
        Initialize renderer.

        Args:
            ocean_floor: OceanFloor instance
            ocean_design_data: Full ocean design with sand/ocean types
            width: Window width
            height: Window height
            camera_mode: "fixed" shows whole map, "follow" follows surfer
        """
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("SurferBro - RL Surfing Simulator [FIXED]")

        self.ocean_floor = ocean_floor
        self.ocean_design = ocean_design_data  # Store full design for sand info
        self.ocean_width, self.ocean_height = ocean_floor.get_dimensions()
        self.camera_mode = camera_mode

        # Camera settings
        self.camera_x = 0
        self.camera_y = 0

        # Zoom to fit WHOLE ocean in view (fixed camera)
        if camera_mode == "fixed":
            zoom_x = width / self.ocean_width
            zoom_y = height / self.ocean_height
            self.zoom = min(zoom_x, zoom_y) * 0.9  # 90% to leave margin
        else:
            self.zoom = min(width / self.ocean_width, height / self.ocean_height) * 0.8

        # Colors
        self.COLORS = {
            'sky': (135, 206, 235),
            'water_deep': (10, 50, 120),
            'water_shallow': (60, 180, 255),
            'sand': (244, 228, 193),
            'surfer': (255, 100, 100),
            'board': (255, 255, 200),
            'wave': (200, 240, 255),
            'wave_breaking': (255, 255, 255),
            'jellyfish': (255, 100, 200),
            'pier': (139, 69, 19),
            'grid_line': (200, 200, 200)
        }

        # Font
        self.font = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 36)

        self.clock = pygame.time.Clock()

        # Pre-compute sand areas for fast rendering
        self.sand_areas = []
        if ocean_design_data:
            self._precompute_sand_areas()

    def _precompute_sand_areas(self):
        """Find all sand tiles for rendering."""
        grid = self.ocean_design['grid']
        cell_size = 0.5  # meters

        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell['type'] == 'sand':
                    # Store in world coordinates
                    world_x = x * cell_size
                    world_y = y * cell_size
                    self.sand_areas.append((world_x, world_y, cell_size, cell_size))

    def world_to_screen(self, x: float, y: float) -> tuple:
        """Convert world coordinates to screen coordinates."""
        if self.camera_mode == "fixed":
            # Fixed camera - show whole map
            sx = int(x * self.zoom)
            sy = int(y * self.zoom)
        else:
            # Following camera
            sx = int((x - self.camera_x) * self.zoom)
            sy = int((y - self.camera_y) * self.zoom)
        return sx, sy

    def render(
        self,
        surfer: Surfer,
        wave_simulator: WaveSimulator,
        jellyfish_swarm: JellyfishSwarm,
        mode: str = "human"
    ) -> Optional[np.ndarray]:
        """Render the environment."""
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update camera if following
        if self.camera_mode == "follow":
            self.camera_x = surfer.state.x - self.width / (2 * self.zoom)
            self.camera_y = surfer.state.y - self.height / (2 * self.zoom)

        # Clear screen with sky
        self.screen.fill(self.COLORS['sky'])

        # Draw ocean and beach
        self._draw_ocean_and_beach()

        # Draw reference grid (helps see movement)
        self._draw_grid()

        # Draw waves
        self._draw_waves(wave_simulator)

        # Draw jellyfish
        self._draw_jellyfish(jellyfish_swarm)

        # Draw surfer (bigger!)
        self._draw_surfer(surfer)

        # Draw HUD
        self._draw_hud(surfer, wave_simulator)

        if mode == "human":
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS
            return None
        elif mode == "rgb_array":
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(self.screen)),
                axes=(1, 0, 2)
            )

    def _draw_ocean_and_beach(self):
        """Draw ocean with proper beach/sand visualization."""
        # First draw all ocean
        for y in range(0, int(self.ocean_height), 1):
            world_y = float(y)
            sy = int(world_y * self.zoom)

            if sy < 0 or sy > self.height:
                continue

            # Sample depth across width
            depths = []
            for x_sample in np.linspace(0, self.ocean_width, 20):
                depth = self.ocean_floor.get_depth(x_sample, world_y)
                depths.append(depth)

            avg_depth = np.mean(depths)

            # Color based on depth
            if avg_depth < 0.1:
                color = self.COLORS['sand']  # Basically beach level
            else:
                depth_ratio = min(avg_depth / 10.0, 1.0)
                color = self._interpolate_color(
                    self.COLORS['water_shallow'],
                    self.COLORS['water_deep'],
                    depth_ratio
                )

            rect_height = max(int(self.zoom * 1), 2)
            pygame.draw.rect(self.screen, color, (0, sy, self.width, rect_height))

        # Draw sand areas ON TOP
        for wx, wy, w, h in self.sand_areas:
            sx, sy = self.world_to_screen(wx, wy)
            sw = int(w * self.zoom)
            sh = int(h * self.zoom)

            if sw > 0 and sh > 0:
                pygame.draw.rect(self.screen, self.COLORS['sand'], (sx, sy, sw, sh))

    def _draw_grid(self):
        """Draw reference grid to show movement."""
        # Draw vertical lines every 10m
        for x in range(0, int(self.ocean_width), 10):
            sx, sy_top = self.world_to_screen(x, 0)
            _, sy_bottom = self.world_to_screen(x, self.ocean_height)

            if 0 <= sx <= self.width:
                pygame.draw.line(
                    self.screen,
                    self.COLORS['grid_line'],
                    (sx, max(0, sy_top)),
                    (sx, min(self.height, sy_bottom)),
                    1
                )

        # Draw horizontal lines every 10m
        for y in range(0, int(self.ocean_height), 10):
            sx_left, sy = self.world_to_screen(0, y)
            sx_right, _ = self.world_to_screen(self.ocean_width, y)

            if 0 <= sy <= self.height:
                pygame.draw.line(
                    self.screen,
                    self.COLORS['grid_line'],
                    (max(0, sx_left), sy),
                    (min(self.width, sx_right), sy),
                    1
                )

    def _draw_waves(self, wave_simulator: WaveSimulator):
        """Draw angled wave fronts advancing toward shore."""
        from surferbro.physics.wave_simulator import WavePhase

        for wave in wave_simulator.waves:
            # Convert wave front endpoints to screen coordinates
            x1_screen, y1_screen = self.world_to_screen(wave.front_start[0], wave.front_start[1])
            x2_screen, y2_screen = self.world_to_screen(wave.front_end[0], wave.front_end[1])

            # Line thickness based on wave height and phase
            base_thickness = max(int(wave.height * self.zoom * 4), 3)

            # Color and styling based on phase
            if wave.phase == WavePhase.BUILDING:
                # Building: light blue, semi-transparent effect (thinner)
                color = (100, 200, 255)
                thickness = max(base_thickness // 2, 2)
                style = "dashed"
            elif wave.phase == WavePhase.FRONT:
                # Front: bright white/cyan, thick (RIDEABLE!)
                color = (0, 255, 255)
                thickness = base_thickness
                style = "solid"
            else:  # WHITEWASH
                # Whitewash: white foam
                color = (255, 255, 255)
                thickness = base_thickness
                style = "solid"

            # Draw the angled wave front line
            if style == "solid":
                # Solid line for FRONT and WHITEWASH
                pygame.draw.line(
                    self.screen,
                    color,
                    (x1_screen, y1_screen),
                    (x2_screen, y2_screen),
                    thickness
                )
                # Add highlight/shimmer for FRONT phase
                if wave.phase == WavePhase.FRONT:
                    # Draw parallel highlight line
                    # Calculate perpendicular offset
                    dx = x2_screen - x1_screen
                    dy = y2_screen - y1_screen
                    length = max(1, (dx**2 + dy**2)**0.5)
                    # Perpendicular vector (rotated 90°)
                    px = -dy / length * (thickness // 2)
                    py = dx / length * (thickness // 2)

                    pygame.draw.line(
                        self.screen,
                        (255, 255, 255),
                        (int(x1_screen + px), int(y1_screen + py)),
                        (int(x2_screen + px), int(y2_screen + py)),
                        2
                    )
            else:  # dashed for BUILDING phase
                # Draw dashed line along angled front
                dx = x2_screen - x1_screen
                dy = y2_screen - y1_screen
                line_length = (dx**2 + dy**2)**0.5

                if line_length > 0:
                    # Unit vector along line
                    ux = dx / line_length
                    uy = dy / line_length

                    dash_length = 20
                    pos = 0
                    while pos < line_length:
                        x_start = int(x1_screen + ux * pos)
                        y_start = int(y1_screen + uy * pos)
                        next_pos = min(pos + dash_length, line_length)
                        x_end = int(x1_screen + ux * next_pos)
                        y_end = int(y1_screen + uy * next_pos)

                        pygame.draw.line(
                            self.screen,
                            color,
                            (x_start, y_start),
                            (x_end, y_end),
                            thickness
                        )
                        pos += dash_length * 2

            # Add direction arrow to show wave travel direction
            center_x = (x1_screen + x2_screen) // 2
            center_y = (y1_screen + y2_screen) // 2
            arrow_length = 30
            arrow_x = int(center_x + np.cos(wave.direction) * arrow_length)
            arrow_y = int(center_y + np.sin(wave.direction) * arrow_length)

            # Draw small direction indicator
            pygame.draw.line(
                self.screen,
                (255, 255, 0),
                (center_x, center_y),
                (arrow_x, arrow_y),
                2
            )
            # Arrowhead
            pygame.draw.circle(self.screen, (255, 255, 0), (arrow_x, arrow_y), 3)

    def _draw_jellyfish(self, jellyfish_swarm: JellyfishSwarm):
        """Draw jellyfish."""
        for jelly in jellyfish_swarm.jellyfish:
            sx, sy = self.world_to_screen(jelly.x, jelly.y)
            radius = max(int(jelly.radius * self.zoom), 3)  # At least 3 pixels

            if radius > 1 and 0 <= sx <= self.width and 0 <= sy <= self.height:
                # Pulsing effect
                pulse = int(abs(np.sin(pygame.time.get_ticks() * 0.005)) * 3)
                pygame.draw.circle(
                    self.screen,
                    self.COLORS['jellyfish'],
                    (sx, sy),
                    radius + pulse
                )

    def _draw_surfer(self, surfer: Surfer):
        """Draw surfer - BIGGER and more visible."""
        sx, sy = self.world_to_screen(surfer.state.x, surfer.state.y)

        # Make surfer BIGGER - at least 15 pixels
        surfer_radius = max(int(0.4 * self.zoom), 15)

        # Draw board (bigger too!)
        board_length = max(int(surfer.board_length * self.zoom), 30)
        board_width = max(int(surfer.board_width * self.zoom), 10)

        if board_length > 5:
            angle_deg = np.degrees(surfer.state.yaw)
            board_surf = pygame.Surface((board_length, board_width), pygame.SRCALPHA)
            pygame.draw.rect(board_surf, self.COLORS['board'], board_surf.get_rect(), border_radius=3)
            rotated_board = pygame.transform.rotate(board_surf, -angle_deg)
            board_rect = rotated_board.get_rect(center=(sx, sy))
            self.screen.blit(rotated_board, board_rect)

        # Draw surfer (bigger circle)
        pygame.draw.circle(self.screen, self.COLORS['surfer'], (sx, sy), surfer_radius)

        # Direction indicator (bigger arrow)
        dx = np.cos(surfer.state.yaw) * surfer_radius * 2
        dy = np.sin(surfer.state.yaw) * surfer_radius * 2
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (sx, sy),
            (sx + int(dx), sy + int(dy)),
            3
        )

        # Status text
        if surfer.state.is_surfing:
            status_text = self.font_large.render("SURFING!", True, (0, 255, 0))
            self.screen.blit(status_text, (sx - 40, sy - 50))
        elif surfer.state.is_duck_diving:
            status_text = self.font.render("DIVE", True, (100, 200, 255))
            self.screen.blit(status_text, (sx - 20, sy - 40))

    def _draw_hud(self, surfer: Surfer, wave_simulator: WaveSimulator):
        """Draw heads-up display."""
        hud_bg = pygame.Surface((400, 250))
        hud_bg.set_alpha(200)
        hud_bg.fill((0, 0, 0))
        self.screen.blit(hud_bg, (10, 10))

        y_offset = 20
        info_lines = [
            f"Position: ({surfer.state.x:.1f}, {surfer.state.y:.1f})",
            f"Velocity: {np.sqrt(surfer.state.vx**2 + surfer.state.vy**2):.2f} m/s",
            f"Depth: {self.ocean_floor.get_depth(surfer.state.x, surfer.state.y):.2f}m",
            f"State: {'SURFING' if surfer.state.is_surfing else 'SWIMMING'}",
            f"Yaw: {np.degrees(surfer.state.yaw):.1f}°",
            f"Waves: {len(wave_simulator.waves)}",
            f"Time: {wave_simulator.time:.1f}s",
            f"Camera: {self.camera_mode}"
        ]

        for line in info_lines:
            text = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text, (20, y_offset))
            y_offset += 30

    def _interpolate_color(self, color1, color2, ratio):
        """Interpolate between two colors."""
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        return (r, g, b)

    def close(self):
        """Clean up pygame resources."""
        pygame.quit()
