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

from os.path import dirname
from os.path import expanduser
from os.path import expandvars
from os.path import join as join_path
from sys import prefix
from pathlib import Path

from .platformdeps import generic_factory
from .utils import which


BASE_DIR = dirname(dirname(dirname(__file__)))


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


_PATHS = library_path_factory()
LIBRARY_PATH = _PATHS.library_path
PROBE_PATH = _PATHS.prober_path


class VMPaths:
    """Class to define the base class for paths handling."""

    def __init__(self):
        """Class initializer."""
        self.apps = 'share/applications'
        self.config = join_path(expanduser('~'), '.videomorph')
        self.icons = 'share/icons'
        self.i18n = 'share/videomorph/translations'
        self.profiles = 'share/videomorph/profiles'
        self.sounds = 'share/videomorph/sounds'
        self.doc = 'share/doc/videomorph'
        self.help = join_path(self.doc, 'manual')
        self.man = 'share/man/man1'
        self.bin = 'bin'


class _LinuxPaths(VMPaths):
    """Class to define the paths to use in Linux systems."""

    def __init__(self):
        """Class initializer."""
        super(_LinuxPaths, self).__init__()
        for attr in self.__dict__:
            if attr != 'config':
                self.__dict__[attr] = join_path(prefix, self.__dict__[attr])


class _Win32Paths(VMPaths):
    """Class to define the paths to use on Windows32 systems."""

    def __init__(self):
        """Class initializer."""
        super(_Win32Paths, self).__init__()
        program_files = expandvars('%ProgramFiles%')
        self.apps = join_path(program_files, r'VideoMorph')
        self.config = join_path(expanduser('~'), '.videomorph')
        self.icons = join_path(program_files, r'VideoMorph\icons')
        self.i18n = join_path(program_files, r'VideoMorph\translations')
        self.profiles = join_path(program_files, r'VideoMorph\profiles')
        self.sounds = join_path(program_files, r'VideoMorph\sounds')
        self.doc = join_path(program_files, r'VideoMorph\doc')
        self.help = join_path(self.doc, 'manual')
        self.man = join_path(program_files, r'VideoMorph\man')
        self.bin = join_path(program_files, r'VideoMorph\bin')


def sys_path_factory():
    """Factory method to create the appropriate path."""
    return generic_factory(parent_class=VMPaths)


SYS_PATHS = sys_path_factory()
VM_PATHS = VMPaths()
