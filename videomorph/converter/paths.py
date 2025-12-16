"""Centralized path helpers for VideoMorph."""

import configparser
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from sys import platform, prefix
from typing import Optional

_BASE_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True, slots=True)
class _PlatformPaths:
    """Platform-specific path structure."""

    apps: Path
    config: Path
    icons: Path
    i18n: Path
    profiles: Path
    sounds: Path
    doc: Path
    help: Path
    man: Path
    bin: Path

    @classmethod
    def for_current_platform(cls) -> "_PlatformPaths":
        """Create platform-specific paths for the current system."""
        user_config = Path.home() / ".videomorph"

        if platform == "win32":
            program_files = Path(os.environ.get("ProgramFiles", "C:\\Program Files"))
            vm_root = program_files / "VideoMorph"
            return cls(
                apps=vm_root,
                config=user_config,
                icons=vm_root / "icons",
                i18n=vm_root / "translations",
                profiles=vm_root / "profiles",
                sounds=vm_root / "sounds",
                doc=vm_root / "videomorph",
                help=vm_root / "videomorph" / "manual",
                man=vm_root / "man1",
                bin=vm_root / "bin",
            )

        # Unix-like platforms (Linux, macOS)
        system_prefix = Path(prefix)
        share = system_prefix / "share"
        vm_share = share / "videomorph"
        doc_share = share / "doc" / "videomorph"

        return cls(
            apps=share / "applications",
            config=user_config,
            icons=share / "icons",
            i18n=vm_share / "translations",
            profiles=vm_share / "profiles",
            sounds=vm_share / "sounds",
            doc=doc_share,
            help=doc_share / "manual",
            man=share / "man" / "man1",
            bin=system_prefix / "bin",
        )


@dataclass(slots=True)
class PathManager:
    """Manage VideoMorph resource and user paths with override support."""

    platform_paths: _PlatformPaths
    base_dir: Path
    _config: configparser.ConfigParser = field(init=False)
    _user_root: Path = field(init=False)

    def __post_init__(self) -> None:
        """Initialize user directory and load path overrides."""
        self._user_root = self.platform_paths.config
        self._user_root.mkdir(parents=True, exist_ok=True)

        self._config = configparser.ConfigParser()
        paths_ini = self._user_root / "paths.ini"
        if paths_ini.exists():
            self._config.read(paths_ini)

    def _get_override(self, key: str) -> Optional[Path]:
        """Return user override path if configured and exists."""
        if self._config.has_option("paths", key):
            candidate = Path(self._config.get("paths", key)).expanduser()
            if candidate.exists():
                return candidate
        return None

    def _resolve_with_fallback(self, key: str, *parts: str) -> Path:
        """Resolve path with override → system → base fallback chain."""
        # Check user override
        if override := self._get_override(key):
            candidate = override.joinpath(*parts) if parts else override
            if candidate.exists():
                return candidate

        # Check system installation
        system_path = getattr(self.platform_paths, key, None)
        if system_path:
            candidate = system_path.joinpath(*parts) if parts else system_path
            if candidate.exists():
                return candidate

        # Fallback to base directory
        base_mapping = {
            "i18n": "share/videomorph/translations",
            "help": "share/doc/videomorph/manual",
            "sounds": "share/videomorph/sounds",
            "profiles": "share/videomorph/profiles",
            "icons": "share/icons",
            "doc": "share/doc/videomorph",
        }
        subdir = base_mapping.get(key, key)
        return self.base_dir.joinpath(subdir, *parts)

    def _extra_tool_dirs(self) -> list[Path]:
        """Return common installation directories for multimedia tools."""
        dirs: list[Path] = []
        if platform == "darwin":
            dirs.extend(
                [
                    Path("/opt/homebrew/bin"),
                    Path("/usr/local/bin"),
                    Path("/opt/local/bin"),
                    Path("/usr/bin"),
                ]
            )
        elif platform.startswith("linux"):
            dirs.extend(
                [
                    Path("/usr/local/bin"),
                    Path("/usr/bin"),
                    Path("/snap/bin"),
                ]
            )
        elif platform == "win32":
            dirs.extend(
                [
                    Path("C:/Program Files/ffmpeg/bin"),
                    Path("C:/Program Files (x86)/ffmpeg/bin"),
                    Path("C:/ffmpeg/bin"),
                ]
            )
        return dirs

    def _locate_tool(self, tool_name: str) -> Optional[str]:
        """Locate ffmpeg/ffprobe via overrides or PATH."""
        # Environment variable override
        env_key = f"VIDEOMORPH_{tool_name.upper()}"
        if env_override := os.environ.get(env_key):
            path = Path(env_override).expanduser()
            if path.exists():
                return str(path)

        # Config file override
        if self._config.has_option("tools", tool_name):
            config_path = Path(self._config.get("tools", tool_name)).expanduser()
            if config_path.exists():
                return str(config_path)

        # System PATH
        if path := shutil.which(tool_name):
            return path

        exe_name = f"{tool_name}.exe" if os.name == "nt" else tool_name
        for directory in self._extra_tool_dirs():
            candidate = directory / exe_name
            if candidate.exists():
                return str(candidate)

        return None

    def resource_path(self, key: str, *parts: str) -> Path:
        """Return resolved resource path (icons, docs, sounds, etc.)."""
        return self._resolve_with_fallback(key, *parts)

    def manual_path(self, locale: str) -> Optional[Path]:
        """Return manual PDF path for locale if available."""
        filename = "manual_es.pdf" if locale == "es_ES" else "manual_en.pdf"
        manual = self.resource_path("help", filename)
        return manual if manual.exists() else None

    def profiles_user_dir(self) -> Path:
        """Return user profile storage directory, creating if needed."""
        profiles = self._user_root / "profiles"
        profiles.mkdir(parents=True, exist_ok=True)
        return profiles

    def packaged_profile(self, name: str) -> Path:
        """Return bundled conversion profile path."""
        return self.resource_path("profiles", name)

    def settings_file(self) -> Path:
        """Return path to Qt settings INI file."""
        return self._user_root / "config.ini"

    @property
    def library_path(self) -> Optional[str]:
        """Return ffmpeg binary path."""
        return self._locate_tool("ffmpeg")

    @property
    def probe_path(self) -> Optional[str]:
        """Return ffprobe binary path."""
        return self._locate_tool("ffprobe")


# Module-level singleton for application-wide use
path_manager = PathManager(
    platform_paths=_PlatformPaths.for_current_platform(), base_dir=_BASE_DIR
)
