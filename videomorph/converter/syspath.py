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
from os.path import join as join_path
from os.path import sep
from sys import platform
from sys import prefix


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


class _WindowsPaths(VMPaths):
    """Class to define the paths to use in Windows systems."""

    def __init__(self):
        super(_WindowsPaths, self).__init__()
        user_path = expanduser('~')
        self.apps = join_path(user_path,'VideoMorph')
        self.config = join_path(user_path, '.videomorph')
        self.icons = join_path(user_path, r'VideoMorph\icons')
        self.i18n = r'C:\Program Files\VideoMorph\translations'
        self.profiles = r'C:\Program Files\VideoMorph\profiles'
        self.doc = r'C:\Program Files\VideoMorph\doc'
        self.man = r'C:\Program Files\VideoMorph\man'
        self.bin = r'C:\Program Files\VideoMorph\bin'


def sys_path_factory():
    """Factory method to create the appropriate path."""
    for path_class in VMPaths.__subclasses__():
        if path_class.__name__.lower().startswith('_' + platform):
            return path_class()
