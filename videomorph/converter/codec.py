# -*- coding: utf-8 -*-

# File name: codec.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
#   Copyright 2016-2022 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""This module provides CodecsReader Class."""

from itertools import islice

from .launchers import spawn_process
from .vmpath import LIBRARY_PATH


class CodecsReader:
    """Class to get codecs out of ffmpeg -codecs output."""

    def __init__(self):
        self.vcodecs, self.acodecs, self.scodecs = self._read(
            "-codecs", 12
        )
        self.vencoders, self.aencoders, self.sencoders = self._read(
            "-encoders", 11
        )
        self.vdecoders, self.adecoders, self.sdecoders = self._read(
            "-decoders", 11
        )

    def _read(self, param, start):
        """Read the available encoders from ffmpeg."""
        video = {}
        audio = {}
        subtitle = {}
        with spawn_process([LIBRARY_PATH, param]).stdout as output:
            for line in islice(output, start, None):
                functionality, name, *description = line.split()
                if "V" in functionality:
                    video[name] = (functionality, " ".join(description))
                    continue

                if "A" in functionality:
                    audio[name] = (functionality, " ".join(description))
                    continue

                if "S" in functionality:
                    subtitle[name] = (functionality, " ".join(description))

        return video, audio, subtitle
