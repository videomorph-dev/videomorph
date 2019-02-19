# -*- coding: utf-8 -*-
#
# File name: conversionlib.py
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

"""This module provides the definition of the ConversionLib class."""

import re
from pathlib import Path
from time import time

from PyQt5.QtCore import QProcess

from videomorph import BASE_DIR
from .platformdeps import launcher_factory
from .platformdeps import generic_factory
from .utils import write_time
from .utils import which


class ConversionLib:
    """Conversion Library class."""

    def __init__(self):
        """Class initializer."""
        library = library_path_factory()
        self._library_path = library.library_path
        self.prober_path = library.prober_path
        self._converter = _Converter(library_path=self.library_path)
        self.error = None
        self.reader = _OutputReader()
        self.timer = _ConversionTimer()

    def __getattr__(self, attr):
        """Delegate to use instance member objects."""
        return getattr(self._converter, attr)

    def catch_errors(self):
        """Catch the library error when running."""
        self.error = self.reader.catch_library_error()

    @staticmethod
    def run_player(file_path):
        """Play a video file with user default player."""
        launcher = launcher_factory()
        launcher.open_with_user_app(url=file_path)

    @property
    def library_path(self):
        """Return the name of the conversion library."""
        return self._library_path


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


class _Converter:
    """_Converter class to provide conversion functionality."""

    def __init__(self, library_path):
        """Class initializer."""
        self._library_path = library_path
        self._process = QProcess()

    def setup_converter(self, reader, finisher, process_channel):
        """Set up the QProcess object."""
        self._process.setProcessChannelMode(process_channel)
        self._process.readyRead.connect(reader)
        self._process.finished.connect(finisher)

    def start_converter(self, cmd):
        """Start the encoding process."""
        self._process.start(self._library_path, cmd)

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

    def read_converter_output(self):
        """Call QProcess.readAll method."""
        return str(self._process.readAll())

    @property
    def converter_is_running(self):
        """Return QProcess state."""
        return self._process.state() == QProcess.Running


class _OutputReader:
    """Read the converter output."""

    def __init__(self):
        """Class initializer."""
        self._params_regex = {
            'bitrate': r'bitrate=[ ]*[0-9]*\.[0-9]*[a-z]*./[a-z]*',
            'time': r'time=([0-9.:]+) '}
        self._library_errors = ('Unknown encoder',
                                'Unrecognized option',
                                'Invalid argument')
        self._process_output = None

    def update_read(self, process_output):
        """Update the process output."""
        self._process_output = process_output

    def catch_library_error(self):
        """Process the library errors."""
        for error in self._library_errors:
            if error in self._process_output:
                return error

        return None

    @property
    def has_time_read(self):
        """Return the time read."""
        return self._read_output_param(param='time')

    @property
    def bitrate(self):
        """Return the bitrate read."""
        bitrate_read = self._read_output_param(param='bitrate')

        return bitrate_read[0].split('=')[-1].strip()

    @property
    def time(self):
        """Convert time read to seconds."""
        seconds = 0.0
        for time_part in self.has_time_read[0].split(':'):
            seconds = 60 * seconds + float(time_part)

        return seconds

    def _read_output_param(self, param):
        """Read library output looking for some parameters."""
        pattern = re.compile(self._params_regex[param])

        return pattern.findall(self._process_output)


class _ConversionTimer:
    """Class to process Conversion progress times."""

    def __init__(self):
        """Class initializer."""
        self._time_jump = 0.0
        self._partial_time = 0.0
        self._total_time = 0.0

        self._operation_time_read = 0.0

        self.process_start_time = 0.0
        self.process_cum_time = 0.0
        self.operation_start_time = 0.0
        self.operation_cum_time = 0.0

    def update_time(self, op_time_read_sec):
        """Update ConversionTimer with operation time read from conversion."""
        self._operation_time_read = op_time_read_sec

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

    def operation_progress(self, file_duration):
        """Return the operation progress percentage."""
        return int(self._operation_time_read / file_duration * 100)

    def process_progress(self, list_duration):
        """"Calculate total progress percentage."""
        if self._partial_time > self._operation_time_read:
            self._time_jump += self._partial_time

        self._total_time = self._time_jump + self._operation_time_read
        self._partial_time = self._operation_time_read

        return int(self._total_time / float(list_duration) * 100)

    def operation_remaining_time(self, file_duration):
        """Return the operation remaining time."""
        op_time = self._operation_time(file_duration=file_duration)
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

    def _operation_time(self, file_duration):
        """Estimating operation time."""
        speed = self.operation_cum_time / self._operation_time_read

        return file_duration * speed
