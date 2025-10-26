"""Pygame-based renderer for the surfing environment."""

import pygame
import numpy as np
from typing import Optional
import sys

from surferbro.physics.ocean_floor import OceanFloor
from surferbro.physics.wave_simulator import WaveSimulator
from surferbro.environments.surfer import Surfer
from surferbro.environments.jellyfish import JellyfishSwarm


class SurfRenderer:
    """
    Renders the surfing environment using Pygame.
    """

    def __init__(self, ocean_floor: OceanFloor, width: int = 1280, height: int = 720):
        """
        Initialize renderer.

        Args:
            ocean_floor: OceanFloor instance
            width: Window width
            height: Window height
        """
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("SurferBro - RL Surfing Simulator")

        self.ocean_floor = ocean_floor
        self.ocean_width, self.ocean_height = ocean_floor.get_dimensions()

        # Camera settings
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = min(width / self.ocean_width, height / self.ocean_height) * 0.8

        # Colors
        self.COLORS = {
            'water_deep': (10, 30, 80),
            'water_shallow': (30, 144, 255),
            'sand': (244, 228, 193),
            'surfer': (255, 100, 100),
            'board': (255, 255, 200),
            'wave': (200, 230, 255),
            'wave_breaking': (255, 255, 255),
            'jellyfish': (255, 100, 200),
            'pier': (139, 69, 19),
            'sky': (135, 206, 235)
        }

        # Font for info display
        self.font = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 36)

        self.clock = pygame.time.Clock()

    def world_to_screen(self, x: float, y: float) -> tuple:
        """Convert world coordinates to screen coordinates."""
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
        """
        Render the environment.

        Args:
            surfer: Surfer instance
            wave_simulator: WaveSimulator instance
            jellyfish_swarm: JellyfishSwarm instance
            mode: Render mode ("human" or "rgb_array")

        Returns:
            RGB array if mode is "rgb_array", None otherwise
        """
        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Update camera to follow surfer
        self.camera_x = surfer.state.x - self.width / (2 * self.zoom)
        self.camera_y = surfer.state.y - self.height / (2 * self.zoom)

        # Clear screen with sky
        self.screen.fill(self.COLORS['sky'])

        # Draw ocean floor (simplified)
        self._draw_ocean()

        # Draw waves
        self._draw_waves(wave_simulator)

        # Draw jellyfish
        self._draw_jellyfish(jellyfish_swarm)

        # Draw surfer
        self._draw_surfer(surfer)

        # Draw HUD
        self._draw_hud(surfer, wave_simulator)

        if mode == "human":
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS
            return None
        elif mode == "rgb_array":
            # Return RGB array
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(self.screen)),
                axes=(1, 0, 2)
            )

    def _draw_ocean(self):
        """Draw ocean and seafloor."""
        # Draw water as gradient
        for y in range(0, self.height, 10):
            world_y = self.camera_y + y / self.zoom
            if 0 <= world_y < self.ocean_height:
                # Get average depth at this y
                depths = []
                for x in range(5):
                    world_x = self.camera_x + (x * self.width / 5) / self.zoom
                    if 0 <= world_x < self.ocean_width:
                        depths.append(self.ocean_floor.get_depth(world_x, world_y))

                if depths:
                    avg_depth = np.mean(depths)
                    # Color based on depth
                    depth_ratio = min(avg_depth / 10.0, 1.0)
                    color = self._interpolate_color(
                        self.COLORS['water_shallow'],
                        self.COLORS['water_deep'],
                        depth_ratio
                    )
                    pygame.draw.rect(self.screen, color, (0, y, self.width, 10))

    def _draw_waves(self, wave_simulator: WaveSimulator):
        """Draw waves."""
        for wave in wave_simulator.waves:
            wx, wy = wave.position
            sx, sy = self.world_to_screen(wx, wy)

            # Wave appearance depends on state
            if wave.is_whitewash:
                color = self.COLORS['wave_breaking']
                radius = int(wave.height * 3 * self.zoom)
            elif wave.is_breaking:
                color = self._interpolate_color(
                    self.COLORS['wave'],
                    self.COLORS['wave_breaking'],
                    0.5
                )
                radius = int(wave.height * 2 * self.zoom)
            else:
                color = self.COLORS['wave']
                radius = int(wave.height * 1.5 * self.zoom)

            if radius > 2:
                pygame.draw.circle(self.screen, color, (sx, sy), radius, 2)

                # Draw wave direction
                dx = np.cos(wave.direction) * radius
                dy = np.sin(wave.direction) * radius
                pygame.draw.line(
                    self.screen,
                    color,
                    (sx, sy),
                    (sx + int(dx), sy + int(dy)),
                    2
                )

    def _draw_jellyfish(self, jellyfish_swarm: JellyfishSwarm):
        """Draw jellyfish."""
        for jelly in jellyfish_swarm.jellyfish:
            sx, sy = self.world_to_screen(jelly.x, jelly.y)
            radius = int(jelly.radius * self.zoom)

            if radius > 1:
                # Pulsing effect
                pulse = int(abs(np.sin(pygame.time.get_ticks() * 0.005)) * 5)
                pygame.draw.circle(
                    self.screen,
                    self.COLORS['jellyfish'],
                    (sx, sy),
                    radius + pulse
                )
                # Tentacles
                for angle in range(0, 360, 45):
                    rad = np.radians(angle)
                    ex = sx + int(np.cos(rad) * (radius + 5))
                    ey = sy + int(np.sin(rad) * (radius + 5))
                    pygame.draw.line(self.screen, self.COLORS['jellyfish'], (sx, sy), (ex, ey), 1)

    def _draw_surfer(self, surfer: Surfer):
        """Draw surfer and board."""
        sx, sy = self.world_to_screen(surfer.state.x, surfer.state.y)

        # Draw board
        board_length = int(surfer.board_length * self.zoom)
        board_width = int(surfer.board_width * self.zoom)

        if board_length > 5:
            # Board as rotated rectangle
            angle_deg = np.degrees(surfer.state.yaw)

            # Create board surface
            board_surf = pygame.Surface((board_length, board_width), pygame.SRCALPHA)
            pygame.draw.rect(board_surf, self.COLORS['board'], board_surf.get_rect(), border_radius=3)
            rotated_board = pygame.transform.rotate(board_surf, -angle_deg)

            # Blit rotated board
            board_rect = rotated_board.get_rect(center=(sx, sy))
            self.screen.blit(rotated_board, board_rect)

        # Draw surfer (circle)
        surfer_radius = int(0.4 * self.zoom)
        if surfer_radius > 2:
            pygame.draw.circle(self.screen, self.COLORS['surfer'], (sx, sy), surfer_radius)

            # Direction indicator
            dx = np.cos(surfer.state.yaw) * surfer_radius * 2
            dy = np.sin(surfer.state.yaw) * surfer_radius * 2
            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                (sx, sy),
                (sx + int(dx), sy + int(dy)),
                2
            )

        # Status indicator
        if surfer.state.is_surfing:
            status_text = self.font.render("SURFING!", True, (0, 255, 0))
            self.screen.blit(status_text, (sx - 30, sy - 40))
        elif surfer.state.is_duck_diving:
            status_text = self.font.render("DIVE", True, (100, 200, 255))
            self.screen.blit(status_text, (sx - 20, sy - 40))

    def _draw_hud(self, surfer: Surfer, wave_simulator: WaveSimulator):
        """Draw heads-up display with info."""
        # Background for HUD
        hud_bg = pygame.Surface((350, 200))
        hud_bg.set_alpha(200)
        hud_bg.fill((0, 0, 0))
        self.screen.blit(hud_bg, (10, 10))

        # Info lines
        y_offset = 20
        info_lines = [
            f"Position: ({surfer.state.x:.1f}, {surfer.state.y:.1f})",
            f"Velocity: {np.sqrt(surfer.state.vx**2 + surfer.state.vy**2):.2f} m/s",
            f"State: {'SURFING' if surfer.state.is_surfing else 'SWIMMING'}",
            f"Board: R:{np.degrees(surfer.state.roll):.1f}° "
            f"P:{np.degrees(surfer.state.pitch):.1f}° "
            f"Y:{np.degrees(surfer.state.yaw):.1f}°",
            f"Waves: {len(wave_simulator.waves)}",
            f"Time: {wave_simulator.time:.1f}s"
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
