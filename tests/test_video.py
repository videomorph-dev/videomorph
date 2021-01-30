#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_video.py
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

"""This module provides tests for video.py module."""

from videomorph.converter.video import Video


class TestVideo:
    """Class for testing video.py module."""

    def test_get_name(self):
        """Test TaskList.get_file_name()."""
        assert Video("sample-video.mp4").get_name() == "sample-video"

    def test_get_name_with_extension(self):
        """Test TaskList.get_file_name() with extension."""
        assert (
            Video("sample-video.mp4").get_name(with_extension=True)
            == "sample-video.mp4"
        )

    def test_video_is_valid_right_duration(self):
        assert Video("sample-video.mp4").is_valid()

    def test_video_is_valid_zero_duration(self):
        video = Video("sample-video.mp4")
        video._info.format_info["duration"] = 0
        assert not video.is_valid()

    def test_video_is_valid_wrong_type(self):
        video = Video("sample-video.mp4")
        video._info.format_info["duration"] = []
        assert not video.is_valid()

    def test_video_is_valid_wrong_value(self):
        video = Video("sample-video.mp4")
        video._info.format_info["duration"] = "N/A"
        assert not video.is_valid()
