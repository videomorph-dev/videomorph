"""This module provides Path."""

from os.path import dirname, expandvars
from pathlib import Path
from sys import platform, prefix
from typing import Dict, Optional

from .launchers import generic_factory
from .utils import which

BASE_DIR = dirname(dirname(dirname(__file__)))
LIBRARY = "ffmpeg"
PROBE = "ffprobe"


class _LibraryPath:
    """Class to define platform dependent conversion tools."""

    def _get_system_path(self, app: str) -> Optional[str]:
        """Return the name of the conversion library installed on system."""
        local_dir = self._get_local_dir()
        if local_dir.is_dir():
            app_path = local_dir.joinpath(app)
            if app_path.exists():
                return app_path.__str__()

        app_path = which(app)
        if app_path:
            return app_path
        return None  # Not available library

    @property
    def library_path(self) -> Optional[str]:
        """Get conversion library path."""
        return self._get_system_path(LIBRARY)

    @property
    def prober_path(self) -> Optional[str]:
        """Get prober path."""
        return self._get_system_path(PROBE)

    def _get_local_dir(self) -> Path:
        """Return the local directory for ffmpeg library."""
        return Path(BASE_DIR, LIBRARY)


class _LinuxLibraryPath(_LibraryPath):
    """Class to define platform dependent conversion lib for Linux."""

    pass


class _DarwinLibraryPath(_LibraryPath):
    """Class to define platform dependent conversion lib for MacOS."""

    pass


class _Win32LibraryPath(_LibraryPath):
    """Class to define platform dependent conversion lib for Win32."""

    def _get_local_dir(self) -> Path:
        """Return the local directory for ffmpeg library."""
        return Path(super(_Win32LibraryPath, self)._get_local_dir(), "bin")

    @property
    def library_path(self) -> str:
        return Path(self._get_local_dir(), LIBRARY + ".exe").__str__()

    @property
    def prober_path(self) -> str:
        return Path(self._get_local_dir(), PROBE + ".exe").__str__()


def library_path_factory() -> _LibraryPath:
    """Factory method to create the appropriate lib name."""
    return generic_factory(parent_class=_LibraryPath)


_PATHS = library_path_factory()
LIBRARY_PATH = _PATHS.library_path
PROBE_PATH = _PATHS.prober_path


VM_PATHS = dict(
    apps=Path("share", "applications"),
    config=Path(Path.home(), ".videomorph"),
    icons=Path("share", "icons"),
    i18n=Path("share", "videomorph", "translations"),
    profiles=Path("share", "videomorph", "profiles"),
    sounds=Path("share", "videomorph", "sounds"),
    doc=Path("share", "doc", "videomorph"),
    help=Path("share", "doc", "videomorph", "manual"),
    man=Path("share", "man", "man1"),
    bin=Path("bin"),
)


def _unix_paths(base_paths: Dict[str, Path] = VM_PATHS) -> Dict[str, Path]:
    """Return the system paths used by VideoMorph."""
    paths = {}
    for key, path in base_paths.items():
        if key != "config":
            paths[key] = Path(prefix, path)
        else:
            paths[key] = path
    return paths


def linux_paths(base_paths: Dict[str, Path] = VM_PATHS) -> Dict[str, Path]:
    return _unix_paths(base_paths)


def darwin_paths(base_paths: Dict[str, Path] = VM_PATHS) -> Dict[str, Path]:
    return _unix_paths(base_paths)


def win32_paths(base_paths: Dict[str, Path] = VM_PATHS) -> Dict[str, Path]:
    program_files = expandvars("%ProgramFiles%")
    paths = {}
    for key, path in base_paths.items():
        if key == "config":
            paths[key] = path
        elif key == "apps":
            paths[key] = Path(program_files, "VideoMorph")
        elif key == "doc":
            paths[key] = Path(program_files, "VideoMorph", path.parts[-2])
        else:
            paths[key] = Path(program_files, "VideoMorph", path.parts[-1])
    return paths


SYS_PATHS = globals()[platform + "_paths"]()
