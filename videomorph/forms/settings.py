from pathlib import Path
from typing import TypedDict

from PyQt6.QtCore import QDir, QPoint, QSettings, QSize

from videomorph.converter.paths import get_settings_file_path


class AppSettings(TypedDict, total=False):
    """Application settings structure."""

    pos: QPoint
    size: QSize
    profile_index: int
    preset_index: int
    output_dir: str
    source_dir: str


class SettingsManager:
    """Manages application settings."""

    def __init__(self) -> None:
        self._settings_file: QSettings = QSettings(
            str(get_settings_file_path()),
            QSettings.Format.IniFormat,
        )
        self._create_initial_settings()

    def _create_initial_settings(self) -> None:
        """Create initial settings if file doesn't exist."""
        if not get_settings_file_path().exists():
            self.write(
                pos=QPoint(100, 50),
                size=QSize(1096, 510),
                profile_index=0,
                preset_index=0,
                output_dir=QDir.homePath(),
                source_dir=QDir.homePath(),
            )

    def read(self) -> AppSettings:
        """Read application settings.

        Returns:
            AppSettings: Dictionary containing loaded settings.
        """
        settings: AppSettings = {}

        settings["pos"] = self._settings_file.value(
            "pos", QPoint(600, 200), type=QPoint
        )
        settings["size"] = self._settings_file.value(
            "size", QSize(1096, 510), type=QSize
        )

        if (
            "profile_index" in self._settings_file.allKeys()
            and "preset_index" in self._settings_file.allKeys()
        ):
            settings["profile_index"] = int(self._settings_file.value("profile_index"))
            settings["preset_index"] = int(self._settings_file.value("preset_index"))

        if "output_dir" in self._settings_file.allKeys():
            dir_path = Path(self._settings_file.value("output_dir"))
            settings["output_dir"] = (
                str(dir_path) if dir_path.is_dir() else QDir.homePath()
            )

        if "source_dir" in self._settings_file.allKeys():
            settings["source_dir"] = str(self._settings_file.value("source_dir"))

        return settings

    def write(self, **app_settings: object) -> None:
        """Write application settings.

        Args:
            app_settings: Keyword arguments for settings to save.
        """
        for key, value in app_settings.items():
            self._settings_file.setValue(key, value)
