# -*- coding: utf-8 -*-
#
# File name: conversionlib.py
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

"""This module provides the definition of the ConversionLib class."""

import re

from PyQt5.QtCore import QProcess

from .utils import which
from .utils import spawn_process
from videomorph import CONV_LIB
from videomorph import PROBER
from videomorph import PLAYERS


class ConversionLib:
    """Conversion Library class."""

    def __init__(self):
        """Class initializer."""
        self._name = self.get_system_library_name()
        self._player = _Player()
        self._converter = _Converter(conversion_lib_name=self.name)

    def __getattr__(self, attr):
        """Delegate to manage _Player and _Converter objects."""
        try:
            return getattr(self._converter, attr)
        except AttributeError:
            try:
                return getattr(self._player, attr)
            except AttributeError:
                raise AttributeError('Attribute not found')

    @staticmethod
    def get_system_library_name():
        """Return the name of the conversion library installed on system."""
        if which(CONV_LIB.ffmpeg):
            return CONV_LIB.ffmpeg  # Default library
        elif which(CONV_LIB.avconv):
            return CONV_LIB.avconv  # Alternative library
        return None  # Not available library

    @property
    def name(self):
        """Return the name of the conversion library."""
        return self._name

    @name.setter
    def name(self, library_name):
        """Set the name of the conversion library."""
        self._name = library_name

    @property
    def prober(self):
        """Return the prober of the conversion library."""
        if self._name == CONV_LIB.ffmpeg:
            return PROBER.ffprobe
        elif self._name == CONV_LIB.avconv:
            return PROBER.avprobe
        else:
            return None


class _Converter:
    """_Converter class to provide conversion functionality."""

    def __init__(self, conversion_lib_name):
        """Class initializer."""
        self._conversion_lib = conversion_lib_name
        self._process = QProcess()
        self._library_errors = ('Unknown encoder', 'Unrecognized option')
        self.current_library_error = None
        self._params_regex = {'bitrate':
                                  r'bitrate=[ ]*[0-9]*\.[0-9]*[a-z]*./[a-z]*',
                              'time':
                                  r'time=([0-9.:]+) '}

    def setup_converter(self, reader, finisher, process_channel):
        """Set up the QProcess object."""
        self._process.setProcessChannelMode(process_channel)
        self._process.readyRead.connect(reader)
        self._process.finished.connect(finisher)

    def start_converter(self, cmd):
        """Start the encoding process."""
        self._process.start(which(self._conversion_lib), cmd)

    def stop_converter(self):
        """Terminate the encoding process."""
        self._process.terminate()
        if self.converter_is_running:
            self._process.kill()

    def converter_finished_disconnect(self, connected):
        """Disconnect the QProcess.finished method."""
        self._process.finished.disconnect(connected)

    def close_converter(self):
        """Call QProcess.close method."""
        self._process.close()

    def kill_converter(self):
        """Call QProcess.kill method."""
        self._process.kill()

    def converter_state(self):
        """Call QProcess.state method."""
        return self._process.state()

    def converter_exit_status(self):
        """Call QProcess.exit_status method."""
        return self._process.exitStatus()

    def process_conversion_errors(self, process_output):
        """Process the library errors."""
        for error in self._library_errors:
            if error in process_output:
                self.current_library_error = error

    def read_conversion_param(self, param, process_output):
        """Read library output looking for some parameters."""
        pattern = re.compile(self._params_regex[param])

        return pattern.findall(process_output)

    @staticmethod
    def time_read_to_seconds(time_read):
        """Convert time read to seconds."""
        seconds = 0.0
        for time_part in time_read[0].split(':'):
            seconds = 60 * seconds + float(time_part)

        return seconds

    @property
    def converter_is_running(self):
        """Return QProcess state."""
        return self._process.state() == QProcess.Running

    def read_converter_output(self):
        """Call QProcess.readAll method."""
        return str(self._process.readAll())


class _Player:
    """_Player class to provide a video player."""

    def __init__(self):
        self._name = None

    def run_player(self, file_path):
        """Play a video file."""
        if self._name is None:
            self._get_player()

        if self._name is not None:
            spawn_process([which(self._name), file_path])
        else:
            raise AttributeError('No Payer Available')

    def _get_player(self):
        for player in PLAYERS:
            if which(player):
                self._name = player
                break
