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
from time import time
from mimetypes import guess_type
from os.path import exists

from PyQt5.QtCore import QProcess

from . import CONV_LIB
from . import PLAYERS
from . import PROBER
from .utils import write_time
from .utils import spawn_process
from .utils import which
from videomorph import LINUX_PATHS


class PlayerNotFoundError(Exception):
    """Exception to handle Player not found error."""
    pass


class ConversionLib:
    """Conversion Library class."""

    def __init__(self):
        """Class initializer."""
        self._name = self.get_system_library_name()
        self._player = _Player()
        self._converter = _Converter(conversion_lib_name=self.name)
        self.library_error = None
        self.reader = _OutputReader()
        self.timer = _ConversionTimer()
        self._delegates = (self._converter, self._player)

    def __getattr__(self, attr):
        """Delegate to use instance member objects."""
        for delegate in self._delegates:
            try:
                return getattr(delegate, attr)
            except AttributeError:
                pass
        else:
            raise AttributeError('Attribute not found')

    def catch_errors(self):
        """Catch the library error when running."""
        self.library_error = self.reader.catch_library_error()

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
            self._set_player(file_path)

        if self._name is not None:
            spawn_process([which(self._name), file_path])
        else:
            raise AttributeError('No Payer Available')

    def _set_player(self, file_path):
        """Return the video player to be used."""
        try:
            self._name = self._gnome_player_finder(file_path)
        except (FileNotFoundError, PlayerNotFoundError):
            pass

        if self._name is None:
            self._name = self._list_base_player_finder()

    @staticmethod
    def _list_base_player_finder():
        """Return a player from a list of popular players."""
        for player in PLAYERS:
            if which(player):
                return player
        else:
            raise PlayerNotFoundError('Player not found')

    def _gnome_player_finder(self, file_path):
        """Return the default Gnome player."""
        if exists(LINUX_PATHS['gnome_mime']):
            mime_type = self._guess_mime_type(file_path)
            if mime_type is None:
                return None

            with open('/etc/gnome/defaults.list', 'r', encoding='UTF-8') as dl:
                for line in dl:
                    if mime_type in line:
                        player = line.split('=')[-1].split('.')[0]
                        return player
                else:
                    raise PlayerNotFoundError('Player not found')
        else:
            raise FileNotFoundError('Gnome default.list not found')

    @staticmethod
    def _guess_mime_type(file_path):
        """Return the file mine type."""
        return guess_type(file_path)[0]


class _OutputReader:
    """Read the converter output."""

    def __init__(self):
        self._params_regex = {'bitrate':
                              r'bitrate=[ ]*[0-9]*\.[0-9]*[a-z]*./[a-z]*',
                              'time':
                              r'time=([0-9.:]+) '}
        self._library_errors = ('Unknown encoder', 'Unrecognized option')
        self._process_output = None

    def read(self):
        """Return the process output."""
        return self._process_output

    def update(self, process_output):
        """Update the process output."""
        self._process_output = process_output

    @property
    def time_read(self):
        """Return the time read."""
        return self._read_output_param(param='time')

    @property
    def bitrate_read(self):
        """Return the bitrate read."""
        bitrate_read = self._read_output_param(param='bitrate')

        return bitrate_read[0].split('=')[-1].strip()

    @property
    def time_read_in_seconds(self):
        """Convert time read to seconds."""
        seconds = 0.0
        for time_part in self.time_read[0].split(':'):
            seconds = 60 * seconds + float(time_part)

        return seconds

    def catch_library_error(self):
        """Process the library errors."""
        for error in self._library_errors:
            if error in self._process_output:
                return error
            else:
                return None

    def _read_output_param(self, param):
        """Read library output looking for some parameters."""
        pattern = re.compile(self._params_regex[param])

        return pattern.findall(self._process_output)


class _ConversionTimer:
    """Class to process Conversion progress times."""

    def __init__(self):
        self._time_jump = 0.0
        self._partial_time = 0.0
        self._total_time = 0.0

        self._op_time_read_sec = 0.0

        self.process_start_time = 0.0
        self.process_cum_time = 0.0

        self.operation_start_time = 0.0
        self.operation_cum_time = 0.0

    def update(self, op_time_read_sec):
        self._op_time_read_sec = op_time_read_sec

    def init_process_start_time(self):
        """Initialize process start time."""
        self.process_start_time = time()

    def init_operation_start_time(self):
        """Initialize the operation time"""
        self.operation_start_time = time()

    def reset_progress_times(self):
        """Reset the variables used to calculate progress."""
        self._time_jump = 0.0
        self._partial_time = 0.0
        self._total_time = 0.0
        self.operation_start_time = 0.0

    def calculate_operation_progress(self, file_duration):
        """Return the operation progress percentage."""
        return int(self._op_time_read_sec / file_duration * 100)

    def calculate_process_progress(self, list_duration):
        """"Calculate total progress percentage."""
        if self._partial_time > self._op_time_read_sec:
            self._time_jump += self._partial_time
            self._total_time = self._time_jump + self._op_time_read_sec
            self._partial_time = self._op_time_read_sec
        else:
            self._total_time = self._time_jump + self._op_time_read_sec
            self._partial_time = self._op_time_read_sec

        return int(self._total_time / float(list_duration) * 100)

    def _calculate_operation_time(self, file_duration):
        """Estimating operation time."""
        speed = self.operation_cum_time / self._op_time_read_sec

        return file_duration * speed

    def calculate_operation_remaining_time(self, file_duration):
        """Return the operation remaining time."""
        op_time = self._calculate_operation_time(file_duration=file_duration)
        # Avoid negative time
        try:
            op_remaining_time = write_time(op_time - self.operation_cum_time)
        except ValueError:
            op_remaining_time = write_time(0)

        return op_remaining_time

    def update_cum_times(self):
        """Real time computation."""
        sys_time = time()
        self.operation_cum_time = sys_time - self.operation_start_time
        self.process_cum_time = sys_time - self.process_start_time
