# -*- coding: utf-8 -*-

# File name: vmpath.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
#   Copyright 2016-2020 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""This module provides Path."""

from os.path import expandvars
from pathlib import Path
from sys import platform, prefix

from .launchers import generic_factory
from .utils import which

BASE_DIR = Path(__file__).parent.parent.parent
LIBRARY = "ffmpeg"
PROBE = "ffprobe"


class _LibraryPath:
    """Class to define platform dependent paths."""

    def _get_system_path(self, app) -> Path:
        """Return the name of the conversion library installed on system."""
        local_dir = self._get_local_dir()
        if local_dir.is_dir():
            app_path = local_dir.joinpath(app)
            if app_path.exists():
                return app_path
        app_path = which(app)
        if app_path:
            return Path(app_path)
        raise ValueError(f"{app} not available")

    @property
    def ffmpeg_path(self) -> Path:
        """Get the FFmpeg path."""
        return self._get_system_path(LIBRARY)

    @property
    def ffprobe_path(self) -> Path:
        """Get the FFprobe path."""
        return self._get_system_path(PROBE)

    def _get_local_dir(self) -> Path:
        """Return the FFmpeg local directory."""
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
    def ffmpeg_path(self) -> Path:
        return Path(self._get_local_dir(), LIBRARY + ".exe")

    @property
    def ffprobe_path(self) -> Path:
        return Path(self._get_local_dir(), PROBE + ".exe")


def library_path_factory():
    """Factory method to create the appropriate lib name."""
    return generic_factory(parent_class=_LibraryPath)


try:
    _PATHS = library_path_factory()
    LIBRARY_PATH = _PATHS.ffmpeg_path
    PROBE_PATH = _PATHS.ffprobe_path
except ValueError:
    LIBRARY_PATH = None
    PROBE_PATH = None


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


def _unix_paths(base_paths=VM_PATHS):
    """Return the system paths used by VideoMorph."""
    paths = {}
    for key, path in base_paths.items():
        if key != "config":
            paths[key] = Path(prefix, path)
        else:
            paths[key] = path
    return paths


def linux_paths(base_paths=VM_PATHS):
    return _unix_paths(base_paths)


def darwin_paths(base_paths=VM_PATHS):
    return _unix_paths(base_paths)


def win32_paths(base_paths=VM_PATHS):
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
