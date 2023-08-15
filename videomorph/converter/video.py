# -*- coding: utf-8 -*-

# File name: video.py
#
#   VideoMorph - A PyQt6 frontend to ffmpeg.
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

"""This module provides Video Class."""

from pathlib import Path

from .probe import Probe


class Video:
    """Class representing a video file."""

    def __init__(self, video_path):
        """Class initializer."""
        self.path = Path(video_path)
        self._info = Probe(self.path)

    def __getattr__(self, attr):
        """Delegate to get info about the video."""
        return getattr(self._info, attr)

    def get_name(self, with_extension=False):
        """Return the file name."""
        if with_extension:
            return self.path.name
        return self.path.stem

    def is_valid(self):
        """Check if a video is valid."""
        try:
            # Video has a valid duration?
            # Duration is > 0
            return float(self.format_info["duration"]) > 0
        except (TypeError, ValueError, KeyError):
            return False
