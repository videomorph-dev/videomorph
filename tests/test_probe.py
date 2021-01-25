#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_probe.py
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

"""This module provides tests for probe.py module."""

from videomorph.converter.video import Probe


class TestProbe:
    """Class for testing probe.py module."""

    def setup(self):
        self.probe = Probe("./Dad.mpg")

    def test_format_info(self):
        assert self.probe.format_info == {
            "filename": "./Dad.mpg",
            "nb_streams": "2",
            "format_name": "mpeg",
            "format_long_name": "MPEG-PS (MPEG-2 Program Stream)",
            "duration": "120.720000",
            "size": "21227416",
            "bit_rate": "1406720",
        }

    def test_video_info(self):
        assert self.probe.video_info == {
            "codec_name": "mpeg1video",
            "codec_long_name": "MPEG-1 video",
            "width": "352",
            "height": "288",
            "bit_rate": "1150000",
        }

    def test_audio_info(self):
        assert self.probe.audio_info == {
            "codec_name": "mp2",
            "codec_long_name": "MP2 (MPEG audio layer 2)",
        }

    def test_subtitle_info(self):
        assert self.probe.subtitle_info == {}
