# -*- coding: utf-8 -*-

# File name: codec.py
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

"""This module provides CodecsReader Class."""

from itertools import islice

from .vmpath import LIBRARY_PATH
from .launchers import spawn_process


class CodecsReader:
    """Class to get codecs out of ffmpeg -codecs output."""

    def __init__(self):
        self.video_codecs = {}
        self.audio_codecs = {}
        self.subtitle_codecs = {}

        self._read_codecs()

    @property
    def _codecs_output(self):
        return spawn_process([LIBRARY_PATH, '-codecs']).stdout

    def _read_codecs(self):
        """Read the available codecs form ffmpeg."""
        with self._codecs_output as codecs_output:
            for line in islice(codecs_output, 10, None):
                functionality, codec_name, *codec_desc = line.split()
                if 'V' in functionality:
                    self.video_codecs[codec_name] = (functionality,
                                                     ' '.join(codec_desc))
                    continue

                if 'A' in functionality:
                    self.audio_codecs[codec_name] = (functionality,
                                                     ' '.join(codec_desc))
                    continue

                if 'S' in functionality:
                    self.subtitle_codecs[codec_name] = (functionality,
                                                        ' '.join(codec_desc))
                    continue
