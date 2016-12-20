#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File name: converter.py
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

"""This module provides the definition of the Converter class."""

from collections import namedtuple

from PyQt5.QtCore import QProcess

from .utils import which

ConversionLib = namedtuple('ConversionLib', 'ffmpeg avconv')


CONV_LIB = ConversionLib('ffmpeg', 'avconv')


class Converter:
    """Converter class to provide conversion functionality."""

    def __init__(self, media_list, conversion_lib=CONV_LIB.ffmpeg):
        """Class initializer."""
        self.conversion_lib = conversion_lib
        self.media_list = media_list
        self.process = QProcess()

    def start_encoding(self, cmd):
        """Start the encoding process."""
        self.process.start(which(self.conversion_lib), cmd)

    def stop_encoding(self):
        """Terminate encoding process."""
        self.process.terminate()
        if self.is_running:
            self.process.kill()

    @property
    def is_running(self):
        """Return the individual file encoding process state."""
        return self.process.state() == QProcess.Running

    @property
    def encoding_done(self):
        """Return True if media list is done."""
        return self.media_list.running_index + 1 >= self.media_list.length
