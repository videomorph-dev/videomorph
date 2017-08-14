# -*- coding: utf-8 -*-
#
# File name: conversionlib.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg and avconv.
#   Copyright 2015-2016 VideoMorph Development Team

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

from PyQt5.QtCore import QProcess

from .utils import which
from .utils import spawn_process
from videomorph import CONV_LIB
from videomorph import PROBER
from videomorph import PLAYERS


class ConversionLib:
    """Conversion Library class."""
    def __init__(self):
        self._name = self.get_system_library_name()
        self.player = _Player()
        self.converter = _Converter(conversion_lib_name=self.name)
        self.library_error = None

    def __getattr__(self, attr):
        try:
            return getattr(self.converter, attr)
        except AttributeError:
            try:
                return getattr(self.player, attr)
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
        """Set the library_name of the conversion library."""
        self._name = library_name

    @property
    def prober(self):
        """Return the probe of the conversion library."""
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
        self.conversion_lib = conversion_lib_name

        self.process = QProcess()

    def setup_converter(self, reader, finisher, process_channel):
        """Set up the QProcess object."""
        self.process.setProcessChannelMode(process_channel)
        self.process.readyRead.connect(reader)
        self.process.finished.connect(finisher)

    def start_converter(self, cmd):
        """Start the encoding process."""
        self.process.start(which(self.conversion_lib), cmd)

    def stop_converter(self):
        """Terminate encoding process."""
        self.process.terminate()
        if self.converter_is_running:
            self.process.kill()

    def converter_finished_disconnect(self, connected):
        """Disconnect the QProcess.finished method."""
        self.process.finished.disconnect(connected)

    def close_converter(self):
        """Calling QProcess.close method."""
        self.process.close()

    def kill_converter(self):
        """Calling QProcess.kill method."""
        self.process.kill()

    def converter_state(self):
        """Calling QProcess.state method."""
        return self.process.state()

    def converter_exit_status(self):
        """Calling QProcess.exit_status method."""
        return self.process.exitStatus()

    @property
    def converter_is_running(self):
        """Return converter running state."""
        return self.process.state() == QProcess.Running

    def read_converter_output(self):
        """Calling QProcess.readAll method."""
        return self.process.readAll()


class _Player:
    """_Player class to provide a video player."""

    def __init__(self):
        self.name = None

    def run_player(self, file_path):
        """Play a video file."""
        if self.name is None:
            self._get_player()

        if self.name is not None:
            spawn_process([which(self.name), file_path])
        else:
            raise AttributeError('No Payer Available')

    def _get_player(self):
        for player in PLAYERS:
            if which(player):
                self.name = player
                break
