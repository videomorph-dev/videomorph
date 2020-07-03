# -*- coding: utf-8 -*-
#
# File name: library.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
#   Copyright 2016-2020 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""This module provides the definition of the Library class."""

from .converter import Converter
from .launchers import launcher_factory
from .reader import OutputReader
from .timer import ConversionTimer


class Library:
    """Conversion Library class."""

    def __init__(self):
        """Class initializer."""
        self._converter = Converter()
        self.error = None
        self.reader = OutputReader()
        self.timer = ConversionTimer()

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
