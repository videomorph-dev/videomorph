# -*- coding: utf-8 -*-

# File name: vmpath.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
#   Copyright 2016-2018 VideoMorph Development Team

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

from pathlib import Path
from . import BASE_DIR
from .platformdeps import generic_factory
from .utils import which


class _LibraryPath:
    """Class to define platform dependent conversion tools."""

    def _get_system_path(self, app):
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
    def library_path(self):
        """Get conversion library path."""
        return self._get_system_path('ffmpeg')

    @property
    def prober_path(self):
        """Get prober path."""
        return self._get_system_path('ffprobe')

    def _get_local_dir(self):
        """Return the local directory for ffmpeg library."""
        raise NotImplementedError('Must be implemented in subclasses')


class _LinuxLibraryPath(_LibraryPath):
    """Class to define platform dependent conversion lib for Linux."""

    def _get_local_dir(self):
        """Return the local directory for ffmpeg library."""
        return Path(BASE_DIR, 'ffmpeg')


class _Win32LibraryPath(_LibraryPath):
    """Class to define platform dependent conversion lib for Win32."""

    def _get_local_dir(self):
        """Return the local directory for ffmpeg library."""
        return Path(BASE_DIR, 'ffmpeg', 'bin')

    def _get_path(self, attr):
        path = getattr(super(_Win32LibraryPath, self), attr)
        if path is not None:
            return path + '.exe'

    @property
    def library_path(self):
        return self._get_path('library_path')

    @property
    def prober_path(self):
        return self._get_path('prober_path')


def library_path_factory():
    """Factory method to create the appropriate lib name."""
    return generic_factory(parent_class=_LibraryPath)