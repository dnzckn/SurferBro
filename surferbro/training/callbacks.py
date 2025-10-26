"""Custom callbacks for training."""

from stable_baselines3.common.callbacks import BaseCallback
import numpy as np


class SurfProgressCallback(BaseCallback):
    """
    Custom callback to track surfing-specific metrics.
    """

    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.surf_times = []
        self.wave_catches = 0
        self.wave_zone_reaches = 0

    def _on_step(self) -> bool:
        """Called after each step."""
        # Get info from environments
        if len(self.locals.get('infos', [])) > 0:
            for info in self.locals['infos']:
                if 'total_surf_time' in info and info['total_surf_time'] > 0:
                    self.surf_times.append(info['total_surf_time'])

                if info.get('is_surfing', False):
                    self.wave_catches += 1

        return True

    def _on_rollout_end(self) -> None:
        """Called at the end of a rollout."""
        if len(self.surf_times) > 0:
            avg_surf_time = np.mean(self.surf_times)
            max_surf_time = np.max(self.surf_times)

            self.logger.record('surf/avg_surf_time', avg_surf_time)
            self.logger.record('surf/max_surf_time', max_surf_time)
            self.logger.record('surf/wave_catches', self.wave_catches)

            # Print progress
            if self.verbose > 0:
                print(f"Avg surf time: {avg_surf_time:.2f}s | "
                      f"Max: {max_surf_time:.2f}s | "
                      f"Catches: {self.wave_catches}")

            # Reset for next rollout
            self.surf_times = []
            self.wave_catches = 0
