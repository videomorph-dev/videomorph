# -*- coding: utf-8 -*-

# File name: platformdeps.py
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

"""This module provides classes for handing platform dependent stuffs."""

import os
from os.path import expanduser
from os.path import expandvars
from os.path import join as join_path
import subprocess
from subprocess import PIPE
from subprocess import Popen
from sys import platform
from sys import prefix
import webbrowser

from .utils import which


def generic_factory(parent_class):
    """Generic factory function."""
    for concrete_class in parent_class.__subclasses__():
        if concrete_class.__name__.lower().startswith('_' + platform):
            return concrete_class()


class PlayerNotFoundError(Exception):
    """Exception to handle Player not found error."""
    pass


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


# EXTERNAL APP LAUNCHER

class _Launcher:
    """Abstract class to implement external apps launcher."""
    def __init__(self):
        self.players = None

    def open_with_user_app(self, url):
        """Open a file or url with user's preferred app."""
        raise NotImplementedError('Must be implemented in subclasses')

    @staticmethod
    def open_with_user_browser(url):
        """Open a web page with default browser."""
        webbrowser.open(url)

    def shutdown_machine(self):
        """Shutdown computer."""
        raise NotImplementedError('Must be implemented in subclasses')

    def sound_notify(self, sound=None):
        """Show system notification."""
        raise NotImplementedError('Must be implemented in subclasses')


class _LinuxLauncher(_Launcher):
    """Concrete class to implement external apps launcher in Linux."""

    def __init__(self):
        super(_LinuxLauncher, self).__init__()
        self.players = ['vlc',
                        'xplayer',
                        'totem',
                        'kmplayer',
                        'smplayer',
                        'mplayer',
                        'banshee',
                        'mpv',
                        'gxine',
                        'xine-ui',
                        'gmlive',
                        'dragon',
                        'ffplay']

    def open_with_user_app(self, url):
        """Open a file or url with user's preferred app."""
        if which('xdg-open') is not None:
            spawn_process([which('xdg-open'), url])
        else:
            player = self._get_player()
            spawn_process([which(player), url])

    def _get_player(self):
        """Return a player from a list of popular players."""
        for player in self.players:
            if which(player):
                return player

        raise PlayerNotFoundError('Player not found')

    def shutdown_machine(self):
        """Shutdown computer."""
        spawn_process(['shutdown', 'now'])

    def sound_notify(self, sound=None):
        """Show system notification on Linux."""
        players = ('paplay', 'aplay', 'play')
        for player in (which(p) for p in players):
            if player is not None:
                spawn_process([player, sound])
                break


class _Win32Launcher(_Launcher):
    """Concrete class to implement external apps launcher in Linux."""

    def open_with_user_app(self, url):
        """Open a file or url with user's preferred app."""
        os.startfile(url)

    def shutdown_machine(self):
        """Shutdown computer."""
        spawn_process(['shutdown', '/s'])

    def sound_notify(self, sound=None):
        """Show system notification."""
        from winsound import PlaySound, MB_OK
        PlaySound(sound, MB_OK)


def launcher_factory():
    """Factory method to create the appropriate launcher."""
    return generic_factory(parent_class=_Launcher)


# PROCESSES

class _Process:
    """Abstract class to implement external subprocess."""

    def spawn_process(self, cmd):
        """Class to implement external subprocess on different platforms."""
        raise NotImplementedError('Must be implemented in subclasses')


class _LinuxProcess(_Process):
    """Concrete class to implement external subprocess on Linux."""

    def spawn_process(self, cmd):
        """Return a Popen object."""

        return Popen(cmd,
                     stdin=PIPE,
                     stdout=PIPE,
                     stderr=PIPE,
                     universal_newlines=True)


class _Win32Process(_Process):
    """Concrete class to implement external subprocess on Windows."""

    def spawn_process(self, cmd):
        """Return a Popen object."""
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        return Popen(cmd,
                     stdin=PIPE,
                     stdout=PIPE,
                     stderr=PIPE,
                     shell=True,
                     startupinfo=startupinfo,
                     universal_newlines=True)


def spawn_process(cmd):
    """Launch processes on different platforms."""
    return generic_factory(parent_class=_Process).spawn_process(cmd=cmd)
