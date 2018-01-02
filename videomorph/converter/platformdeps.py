# -*- coding: utf-8 -*-

# File name: syspath.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg and avconv.
#   Copyright 2016-2017 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""This module provides System Paths creation classes."""

from os.path import expanduser
from os.path import expandvars
from os.path import join as join_path
from os.path import sep
from sys import platform
from sys import prefix


# PATHS

class VMPaths:
    """Class to define the base class for paths handling."""

    def __init__(self):
        """Class initializer."""
        self.apps = 'share/applications'
        self.config = join_path(expanduser('~'), '.videomorph')
        self.icons = 'share/icons'
        self.i18n = 'share/videomorph/translations'
        self.profiles = 'share/videomorph/profiles'
        self.doc = 'share/doc/videomorph'
        self.man = 'share/man'
        self.bin = 'bin'


class _LinuxPaths(VMPaths):
    """Class to define the paths to use in Linux systems."""

    def __init__(self):
        """Class initializer."""
        super(_LinuxPaths, self).__init__()
        for attr in self.__dict__:
            if attr != 'config':
                self.__dict__[attr] = prefix + sep + self.__dict__[attr]


class _Win32Paths(VMPaths):
    """Class to define the paths to use in Windows32 systems."""

    def __init__(self):
        """Class initializer."""
        super(_Win32Paths, self).__init__()
        program_files = expandvars('%ProgramFiles%')
        self.apps = join_path(program_files, r'VideoMorph')
        self.config = join_path(expanduser('~'), '.videomorph')
        self.icons = join_path(program_files, r'VideoMorph\icons')
        self.i18n = join_path(program_files, r'VideoMorph\translations')
        self.profiles = join_path(program_files, r'VideoMorph\profiles')
        self.doc = join_path(program_files, r'VideoMorph\doc')
        self.man = join_path(program_files, r'VideoMorph\man')
        self.bin = join_path(program_files, r'VideoMorph\bin')


class _Win64Paths(_Win32Paths, VMPaths):
    """Class to define the paths to use in Windows64 systems."""
    pass


def sys_path_factory():
    """Factory method to create the appropriate path."""
    for path_class in VMPaths.__subclasses__():
        if path_class.__name__.lower().startswith('_' + platform):
            return path_class()


# CONVERSION LIBRARY

class _ConversionLib:
    """Class to define platform dependent conversion tools."""

    def __init__(self):
        """Class initializer."""
        self.ffmpeg = 'ffmpeg'
        self.avconv = 'avconv'


class _LinuxConversionLib(_ConversionLib):
    """Class to define platform dependent conversion lib for Linux."""
    pass


class _Win32ConversionLib(_ConversionLib):
    """Class to define platform dependent conversion lib for Win32."""

    def __init__(self):
        """Class initializer."""
        super(_Win32ConversionLib, self).__init__()
        for attr in self.__dict__:
            self.__dict__[attr] += '.exe'


def conversion_lib_factory():
    """Factory method to create the appropriate lib name."""
    for conversion_lib_class in _ConversionLib.__subclasses__():
        if conversion_lib_class.__name__.lower().startswith('_' + platform):
            return conversion_lib_class()


# LIBRARY PROBE TOOL

class _Prober:
    """Class to define platform dependent conversion tools."""

    def __init__(self):
        """Class initializer."""
        self.ffprobe = 'ffprobe'
        self.avprobe = 'avprobe'


class _LinuxProber(_Prober):
    """Class to define platform dependent conversion tools for Linux."""
    pass


class _Win32Prober(_Prober):
    """Class to define platform dependent conversion tools for Win32."""

    def __init__(self):
        """Class initializer."""
        super(_Win32Prober, self).__init__()
        for attr in self.__dict__:
            self.__dict__[attr] += '.exe'


def prober_factory():
    """Factory method to create the appropriate path."""
    for prober_class in _Prober.__subclasses__():
        if prober_class.__name__.lower().startswith('_' + platform):
            return prober_class()
