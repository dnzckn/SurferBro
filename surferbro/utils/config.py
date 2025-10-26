"""Configuration management utilities."""

import yaml
from pathlib import Path
from typing import Any, Dict


class Config:
    """Configuration manager for SurferBro."""

    def __init__(self, config_path: str = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to YAML config file. If None, uses default config.yaml
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config.yaml"

        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.

        Args:
            key: Configuration key (e.g., 'ocean.width')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

        return value if value is not None else default

    def __getitem__(self, key: str) -> Any:
        """Get configuration section."""
        return self._config[key]

    @property
    def all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self._config.copy()
