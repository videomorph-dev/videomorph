from collections import OrderedDict
from pathlib import Path

from PyQt6.QtCore import QPoint, QSettings, QSize, QDir

from videomorph.converter.paths import settings_file as settings_file_path


class SettingsManager:
    """Manages application settings."""

    def __init__(self):
        self._create_initial_settings()

    @staticmethod
    def _get_settings_file():
        return QSettings(str(settings_file_path()), QSettings.Format.IniFormat)

    def _create_initial_settings(self):
        """Create initial settings file if it doesn't exist."""
        if not settings_file_path().exists():
            self.write(
                pos=QPoint(100, 50),
                size=QSize(1096, 510),
                profile_index=0,
                preset_index=0,
            )

    def load(self):
        """Load application settings.

        Returns:
            dict: A dictionary containing the loaded settings.
        """
        settings_file = self._get_settings_file()
        settings = {}

        settings["pos"] = settings_file.value("pos", QPoint(600, 200), type=QPoint)
        settings["size"] = settings_file.value("size", QSize(1096, 510), type=QSize)

        if "profile_index" in settings_file.allKeys() and "preset_index" in settings_file.allKeys():
            settings["profile_index"] = int(settings_file.value("profile_index"))
            settings["preset_index"] = int(settings_file.value("preset_index"))

        if "output_dir" in settings_file.allKeys():
            directory = str(settings_file.value("output_dir"))
            dir_path = Path(directory)
            settings["output_dir"] = str(dir_path) if dir_path.is_dir() else QDir.homePath()

        if "source_dir" in settings_file.allKeys():
            settings["source_dir"] = str(settings_file.value("source_dir"))

        return settings

    def write(self, **app_settings):
        """Write application settings.

        Args:
            app_settings: Keyword arguments for settings to save.
        """
        settings_file = self._get_settings_file()

        # We don't need to reconstruct the entire OrderedDict every time if we just update what's passed
        # However, to maintain the existing behavior of saving specific keys, we can iterate over the input.
        
        for key, value in app_settings.items():
            settings_file.setValue(key, value)
