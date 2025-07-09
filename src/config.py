"""
Author: Luigi Ferraioli
Copyright: © 2025 Luigi Ferraioli
"""

import os
import json
from pathlib import Path


class FWConfig:
    """
    Handles reading and writing a configuration file for the FarbenWolf app.
    The configuration is stored as a JSON file in the AppData/Local/FarbenWolf folder.
    """

    def __init__(self):
        """
        Initializes the Config class with default values.
        If the configuration file does not exist, it is created with default settings.
        """
        self.app_name = "FarbenWolf"
        self.file_name = "config.json"
        self.default_config = self.get_default_config()
        self.config_path = self.get_config_path()
        self.config_data = self._load_or_create_config()

    def get(self, key, default=None):
        """
        Retrieves a configuration value by key.

        :param key: Configuration key
        :param default: Default value if key is not found
        :return: Value from config or default
        """
        return self.config_data.get(key, default)

    def update(self, key, value):
        """
        Updates a configuration key with a new value and saves it to disk.

        :param key: Configuration key (e.g. 'einheit')
        :param value: New value for the key
        """
        self.config_data[key] = value
        self.save()

    def save(self):
        """
        Saves the current configuration data to disk.
        """
        self._save_config(self.config_data)

    def reset_to_defaults(self):
        """
        Resets the configuration to the default settings and saves it.
        """
        self.config_data = self.get_default_config()
        self.save()
        print("Configuration has been reset to default values.")

    # --- Private/Internal methods ---

    def get_default_config(self):
        """
        Returns the default configuration dictionary.
        """
        return {
            "Einheit": "m",
            "Ausgabedokument": "pdf",
            "Speicherort": str(Path.home() / "Desktop"),
            "Name": True,
            "Datum": True,
            "Uhrzeit": False,
            "Arbeiten": [
                "Streichen",
                "Verputzen",
                "Tapezieren",
                "Bodenlegen",
                "Lackieren",
                "Grundieren",
                "Schleifen",
            ],
            "Flächenarten": [
                "Decke/Bodenfläche",
                "Wand (rechteckig)",
                "Wand (dreieckig)",
                "Zwei gegenüberliegende Wände",
                "Zwei nebeneinanderliegende Wände",
                "Alle Wände ohne Decke/Sockel",
                "Alle Wände mit Decke",
                "Alle Wände mit einer schrägen Wand (ohne Decke)",
                "Alle Wände mit einer schrägen Wand und Decke",
                "Fassade (Flachdach)",
                "Fassade (Satteldach)",
                "Fassade (Doppelhaushälfte)"
            ]
        }

    def get_config_path(self):
        """
        Returns the full path to the config.json file inside AppData/Local/FarbenWolf.
        Creates the directory if it does not exist.
        """
        local_appdata = os.getenv("LOCALAPPDATA") or (
            Path.home() / ".farbenwolf")
        config_dir = Path(local_appdata) / self.app_name
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / self.file_name

    def set(self, key, value):
        """
        Updates the value of an existing configuration key.

        Parameters:
            key (str): The configuration key to update.
            value (Any): The new value to assign to the key.

        Raises:
            KeyError: If the provided key does not exist in the configuration.
        """
        if key in self.config_data:
            self.config_data[key] = value
        else:
            raise KeyError(f"Unbekannter Konfigurationsschlüssel: {key}")

    def _load_or_create_config(self):
        """
        Loads the config file if it exists. If not, creates it with default values.
        Returns the configuration dictionary.
        """
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading configuration: {e}")
        # Create default config if file doesn't exist or fails to load
        self._save_config(self.default_config)
        return self.default_config.copy()

    def _save_config(self, data):
        """
        Saves the provided configuration dictionary to the config.json file.
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving configuration: {e}")
