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

    def test_format_info(self):
        assert Probe("sample-video.mp4").format_info == {
            "filename": "sample-video.mp4",
            "nb_streams": "2",
            "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
            "format_long_name": "QuickTime / MOV",
            "duration": "57.563000",
            "size": "5329356",
            "bit_rate": "740664",
        }

    def test_video_info(self):
        assert Probe("sample-video.mp4").video_info == {
            "codec_name": "h264",
            "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
            "width": "854",
            "height": "480",
            "bit_rate": "669499",
        }

    def test_audio_info(self):
        assert Probe("sample-video.mp4").audio_info == {
            "codec_name": "aac",
            "codec_long_name": "AAC (Advanced Audio Coding)",
        }

    def test_subtitle_info(self):
        assert Probe("sample-video.mp4").subtitle_info == {}
