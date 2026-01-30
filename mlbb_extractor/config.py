"""Configuration file for the MLBB Image Data Extractor."""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration management for the extractor."""

    DEFAULT_CONFIG = {
        "preprocessing": {
            "resize_scale": 2.0,
            "apply_denoise": True,
            "threshold_type": "adaptive",  # Options: 'binary', 'adaptive', 'otsu'
        },
        "ocr": {
            "tesseract_cmd": None,  # Set to tesseract path if not in system PATH
            "config": "--psm 6",  # Tesseract page segmentation mode
        },
        "export": {
            "output_dir": "output",
            "default_formats": ["csv", "json"],
            "default_filename": "game_stats",
        },
        "regions": {
            # Define expected regions for MLBB screenshots
            # These can be customized based on screenshot resolution
            "player_name": {"x": 0, "y": 0, "w": 200, "h": 50},
            "hero_name": {"x": 0, "y": 50, "w": 200, "h": 50},
            "kda": {"x": 200, "y": 0, "w": 150, "h": 50},
            "stats": {"x": 350, "y": 0, "w": 200, "h": 100},
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration.

        Args:
            config_path: Path to custom config file (JSON)
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path:
            self.load_from_file(config_path)

    def load_from_file(self, config_path: str) -> None:
        """
        Load configuration from a JSON file.

        Args:
            config_path: Path to JSON configuration file
        """
        path = Path(config_path)
        if path.exists():
            with open(path, "r") as f:
                custom_config = json.load(f)
                self._merge_config(custom_config)

    def _merge_config(self, custom_config: Dict[str, Any]) -> None:
        """
        Merge custom configuration with defaults.

        Args:
            custom_config: Custom configuration dictionary
        """
        for key, value in custom_config.items():
            if key in self.config and isinstance(value, dict):
                self.config[key].update(value)
            else:
                self.config[key] = value

    def save_to_file(self, config_path: str) -> None:
        """
        Save current configuration to a JSON file.

        Args:
            config_path: Path to save configuration file
        """
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, "w") as f:
            json.dump(self.config, f, indent=2)

    def get(self, section: str, key: Optional[str] = None) -> Any:
        """
        Get configuration value.

        Args:
            section: Configuration section
            key: Optional specific key within section

        Returns:
            Configuration value
        """
        if key is None:
            return self.config.get(section, {})
        return self.config.get(section, {}).get(key)

    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            section: Configuration section
            key: Configuration key
            value: Value to set
        """
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value


# Example config.json structure
EXAMPLE_CONFIG = {
    "preprocessing": {
        "resize_scale": 2.5,
        "apply_denoise": True,
        "threshold_type": "otsu",
    },
    "ocr": {
        "tesseract_cmd": "/usr/bin/tesseract",
        "config": "--psm 6 --oem 3",
    },
    "export": {
        "output_dir": "results",
        "default_formats": ["csv", "json", "excel"],
        "default_filename": "mlbb_stats",
    },
}


def create_example_config(output_path: str = "config.json") -> None:
    """
    Create an example configuration file.

    Args:
        output_path: Path where to save the example config
    """
    with open(output_path, "w") as f:
        json.dump(EXAMPLE_CONFIG, f, indent=2)
    print(f"Example configuration saved to: {output_path}")


if __name__ == "__main__":
    # Create an example config file
    create_example_config("config.example.json")
