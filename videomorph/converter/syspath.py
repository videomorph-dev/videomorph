# -*- coding: utf-8 -*-

# File name: syspath.py
#
# Copyright (C) 2017 Leodanis Pozo Ramos <lpozor78@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

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


class LinuxPaths(VMPaths):
    """Class to define the paths to use in Linux systems."""

    def __init__(self):
        """Class initializer."""
        super(LinuxPaths, self).__init__()
        self.__dict__ = {attr: prefix + sep + self.__dict__[attr] for
                         attr in self.__dict__}


class WindowsPaths(VMPaths):
    """Class to define the paths to use in Windows systems."""

    def __init__(self):
        super(WindowsPaths, self).__init__()


def sys_path_factory():
    """Factory method to create the appropriate path."""
    for path_class in VMPaths.__subclasses__():
        if path_class.__name__.lower().startswith(platform):
            return path_class()
