from dataclasses import asdict, dataclass, field
from pathlib import Path

from PyQt6.QtCore import QDir, QPoint, QSettings, QSize

from videomorph.converter.paths import path_manager


@dataclass
class AppSettings:
    """Application settings structure."""

    pos: QPoint = field(default_factory=lambda: QPoint(100, 50))
    size: QSize = field(default_factory=lambda: QSize(1096, 510))
    profile_index: int = 0
    preset_index: int = 0
    output_dir: str = field(default_factory=QDir.homePath)
    source_dir: str = field(default_factory=QDir.homePath)


class SettingsManager:
    """Manages application settings."""

    def __init__(self) -> None:
        self._settings_file: QSettings = QSettings(
            str(path_manager.settings_file()),
            QSettings.Format.IniFormat,
        )
        self._create_initial_settings()

    def _create_initial_settings(self) -> None:
        """Create initial settings if file doesn't exist."""
        if not path_manager.settings_file().exists():
            defaults = AppSettings()
            self.write(**asdict(defaults))

    def read(self) -> AppSettings:
        """Read application settings.

        Returns:
            AppSettings: Dataclass containing loaded settings.
        """
        defaults = AppSettings()

        pos = self._settings_file.value("pos", defaults.pos, type=QPoint)
        size = self._settings_file.value("size", defaults.size, type=QSize)
        profile_index = int(
            self._settings_file.value("profile_index", defaults.profile_index)
        )
        preset_index = int(
            self._settings_file.value("preset_index", defaults.preset_index)
        )

        # Validate output_dir exists
        output_dir = self._settings_file.value("output_dir", defaults.output_dir)
        dir_path = Path(output_dir)
        validated_output = str(dir_path) if dir_path.is_dir() else defaults.output_dir

        source_dir = str(self._settings_file.value("source_dir", defaults.source_dir))

        return AppSettings(
            pos=pos,
            size=size,
            profile_index=profile_index,
            preset_index=preset_index,
            output_dir=validated_output,
            source_dir=source_dir,
        )

    def write(self, **app_settings: object) -> None:
        """Write application settings.

        Args:
            app_settings: Keyword arguments for settings to save.

        Raises:
            ValueError: If unknown setting key provided.
        """
        valid_keys = set(AppSettings.__dataclass_fields__.keys())
        for key, value in app_settings.items():
            if key not in valid_keys:
                raise ValueError(f"Invalid setting key: {key}")
            self._settings_file.setValue(key, value)
