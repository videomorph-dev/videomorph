"""Centralized path helpers for VideoMorph."""

import configparser
import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from sys import platform, prefix
from typing import Dict, Iterator, Optional

_BASE_DIR = Path(__file__).resolve().parents[2]
_LIBRARY = "ffmpeg"
_PROBE = "ffprobe"

_SHARE = Path("share")
_VM_SHARE = _SHARE / "videomorph"
_DOC_SHARE = _SHARE / "doc" / "videomorph"

VM_PATHS = dict(
    apps=_SHARE / "applications",
    config=Path.home() / ".videomorph",
    icons=_SHARE / "icons",
    i18n=_VM_SHARE / "translations",
    profiles=_VM_SHARE / "profiles",
    sounds=_VM_SHARE / "sounds",
    doc=_DOC_SHARE,
    help=_DOC_SHARE / "manual",
    man=_SHARE / "man" / "man1",
    bin=Path("bin"),
)


def _unix_paths(base_paths: Dict[str, Path] = VM_PATHS) -> Dict[str, Path]:
    """Return the system paths used by VideoMorph for POSIX platforms."""
    resolved = {}
    for key, relative in base_paths.items():
        if key == "config":
            resolved[key] = relative
        else:
            resolved[key] = Path(prefix, relative)
    return resolved


def linux_paths(base_paths: Dict[str, Path] = VM_PATHS) -> Dict[str, Path]:
    return _unix_paths(base_paths)


def darwin_paths(base_paths: Dict[str, Path] = VM_PATHS) -> Dict[str, Path]:
    return _unix_paths(base_paths)


def win32_paths(base_paths: Dict[str, Path] = VM_PATHS) -> Dict[str, Path]:
    program_files = Path(os.environ.get("ProgramFiles", "C:\\Program Files"))
    resolved = {}
    for key, relative in base_paths.items():
        if key == "config":
            resolved[key] = relative
        elif key == "apps":
            resolved[key] = Path(program_files, "VideoMorph")
        elif key == "doc":
            resolved[key] = Path(program_files, "VideoMorph", relative.parts[-2])
        else:
            resolved[key] = Path(program_files, "VideoMorph", relative.parts[-1])
    return resolved


SYS_PATHS = globals()[platform + "_paths"]()


@dataclass(slots=True)
class _PathResolver:
    """Resolve runtime, data, and user paths with optional overrides."""

    sys_paths: Dict[str, Path]
    base_paths: Dict[str, Path]
    base_dir: Path
    user_root: Path = field(init=False)
    _paths_ini: Path = field(init=False)
    _config: configparser.ConfigParser = field(init=False)

    def __post_init__(self) -> None:
        self.user_root = Path(self.sys_paths["config"])
        self.user_root.mkdir(parents=True, exist_ok=True)
        self._paths_ini = self.user_root / "paths.ini"
        self._config = configparser.ConfigParser()
        if self._paths_ini.exists():
            self._config.read(self._paths_ini)

    @property
    def overrides(self) -> configparser.ConfigParser:
        return self._config

    @property
    def paths_ini(self) -> Path:
        return self._paths_ini

    @property
    def settings_file(self) -> Path:
        return self.user_root / "config.ini"

    @property
    def profiles_dir(self) -> Path:
        return self._ensure_user_subdir("profiles")

    def _ensure_user_subdir(self, name: str) -> Path:
        target = self.user_root / name
        target.mkdir(parents=True, exist_ok=True)
        return target

    def _override_path(self, key: str) -> Optional[Path]:
        if self._config.has_option("paths", key):
            candidate = Path(self._config.get("paths", key)).expanduser()
            if candidate.exists():
                return candidate
        return None

    @staticmethod
    def _join(base: Path, parts: tuple[str, ...]) -> Path:
        return base.joinpath(*parts) if parts else base

    def resource_path(self, key: str, *parts: str) -> Path:
        """Return a resolved path for the given resource key."""
        suffix = parts
        candidates = []
        override = self._override_path(key)
        if override:
            candidates.append(override)

        sys_path = self.sys_paths.get(key)
        if sys_path:
            candidates.append(sys_path)

        candidates.append(self.base_dir / self.base_paths[key])

        for base in candidates:
            candidate = self._join(base, suffix)
            if candidate.exists():
                return candidate

        # Nothing exists yet; return the last candidate so callers can create it.
        return self._join(candidates[-1], suffix)

    def packaged_resource(self, key: str, *parts: str) -> Path:
        """Return a path inside the repository checkout."""
        return self._join(self.base_dir / self.base_paths[key], parts)

    def tool_override(self, tool_name: str) -> Optional[Path]:
        """Return user-configured tool override if available."""
        if self._config.has_option("tools", tool_name):
            candidate = Path(self._config.get("tools", tool_name)).expanduser()
            if candidate.exists():
                return candidate
        return None

    def manual_path(self, locale: str) -> Optional[Path]:
        """Return the manual PDF path matching locale, if available."""
        file_name = "manual_es.pdf" if locale == "es_ES" else "manual_en.pdf"
        manual = self.resource_path("help", file_name)
        return manual if manual.exists() else None


_PATHS = _PathResolver(sys_paths=SYS_PATHS, base_paths=VM_PATHS, base_dir=_BASE_DIR)


class _FFmpegLocator:
    """Locate ffmpeg/ffprobe binaries via overrides, bundles, or PATH."""

    def __init__(self, resolver: _PathResolver) -> None:
        self._resolver = resolver

    @staticmethod
    def _exe_name(binary: str) -> str:
        return f"{binary}.exe" if os.name == "nt" else binary

    def _bundle_dirs(self) -> Iterator[Path]:
        bundle_names = ("ffmpeg", "ffmpeg-linux64", "ffmpeg-mac", "ffmpeg-win64")
        for bundle in bundle_names:
            base = self._resolver.base_dir / bundle
            if base.is_dir():
                yield base
            bin_dir = base / "bin"
            if bin_dir.is_dir():
                yield bin_dir

    def _candidate_binaries(self, binary: str) -> Iterator[Path]:
        env_key = f"VIDEOMORPH_{binary.upper()}"
        env_override = os.environ.get(env_key)
        if env_override:
            path = Path(env_override).expanduser()
            if path.exists():
                yield path

        config_override = self._resolver.tool_override(binary)
        if config_override:
            yield config_override

        for directory in self._bundle_dirs():
            candidate = directory / self._exe_name(binary)
            if candidate.exists():
                yield candidate

        system_binary = shutil.which(binary)
        if system_binary:
            yield Path(system_binary)

    def locate(self, binary: str) -> Optional[str]:
        for candidate in self._candidate_binaries(binary):
            return str(candidate)
        return None

    @property
    def library_path(self) -> Optional[str]:
        return self.locate(_LIBRARY)

    @property
    def probe_path(self) -> Optional[str]:
        return self.locate(_PROBE)


_FFMPEG = _FFmpegLocator(_PATHS)


# Public API
LIBRARY_PATH = _FFMPEG.library_path
PROBE_PATH = _FFMPEG.probe_path


def resource_path(key: str, *parts: str) -> Path:
    """Return a resolved resource path (icons, docs, etc.)."""
    return _PATHS.resource_path(key, *parts)


def manual_path(locale: str) -> Optional[Path]:
    """Return the manual for the requested locale if present."""
    return _PATHS.manual_path(locale)


def profiles_user_dir() -> Path:
    """Return the user profile storage directory, creating it if needed."""
    return _PATHS.profiles_dir


def packaged_profile(name: str) -> Path:
    """Return the bundled conversion profile path."""
    return _PATHS.packaged_resource("profiles", name)


def settings_file() -> Path:
    """Return the path to the Qt settings INI file."""
    return _PATHS.settings_file

