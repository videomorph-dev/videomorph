# -*- coding: utf-8 -*-

# File name: model.py
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

"""This module provides Model Class."""

from .library import Library
from .profile import Profile
from .media import MediaList
from .library import OutputReader
from .library import ConversionTimer


class VMModel:
    """Model class for VideoMorph."""

    def __init__(self):
        self.library = Library()
        self.reader = OutputReader()
        self.timer = ConversionTimer()
        self.profile = Profile()
        self.media_list = MediaList()

    def __getattr__(self, attr):
        """Delegate."""
        try:
            return getattr(self.library, attr)
        except AttributeError:
            pass

        try:
            return getattr(self.reader, attr)
        except AttributeError:
            pass

        try:
            return getattr(self.timer, attr)
        except AttributeError:
            pass

        try:
            return getattr(self.profile, attr)
        except AttributeError:
            pass

        try:
            return getattr(self.media_list, attr)
        except AttributeError:
            pass

        raise AttributeError()
