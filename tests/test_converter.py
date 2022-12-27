#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_converter.py
#
#   VideoMorph - A PyQt6 frontend to ffmpeg.
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

"""This module provides tests for conversionlib.py module."""

import nose
from PyQt6.QtCore import QProcess

from videomorph.converter import tasklist
from videomorph.converter.library import Library
from videomorph.converter.profile import Profile


class TestConversionLib:
    """Class for testing Library."""
    conv_lib = Library()

    profile = Profile(prober=conv_lib.prober_path)
    profile.update(new_quality='FLV Fullscreen 320x240 (4:3)')

    media_list = tasklist.TaskList(profile)

    @classmethod
    def setup_class(cls):
        """Setup method to run before all test."""
        gen = cls.media_list.populate(('Dad.mpg',))
        next(gen)
        next(gen)

    @classmethod
    def teardown_class(cls):
        """Teardown method to run after all test."""
        cls.media_list.get_task(0).delete_output('.', tagged=True)

    def get_conversion_cmd(self):
        """Return a conversion command."""
        cmd = self.media_list.get_task(position=0).build_conversion_cmd(
            output_dir='.',
            subtitle=False,
            tagged=True,
            target_quality='FLV Fullscreen 320x240 (4:3)')
        return cmd

    def test_get_library_path(self):
        """Test Library.library_path."""
        assert self.conv_lib.path in {'/usr/bin/ffmpeg',
                                              '/usr/local/bin/ffmpeg'}

    def test_prober_path(self):
        """Test the Library.prober_path."""
        assert self.conv_lib.prober_path.__str__() in {'/usr/bin/ffprobe',
                                                       '/usr/local/bin/ffprbe'}

    def test_start_converter(self):
        """Test Library.start_converter()."""
        self.conv_lib.start_converter(cmd=self.get_conversion_cmd())

        assert self.conv_lib.converter_state() == QProcess.Starting
        self.conv_lib.stop_converter()

    def test_read_converter_output(self):
        """Test Library.read_converter_output()."""
        self.conv_lib.start_converter(cmd=self.get_conversion_cmd())
        assert self.conv_lib.read_converter_output()
        self.conv_lib.stop_converter()

    def test_catch_library_error_true(self):
        """Test _OutputReader.catch_library_error() -> true."""
        self.conv_lib.reader.update_read('Some random output with '
                                         'Unknown encoder error')
        assert self.conv_lib.reader.catch_library_error() == 'Unknown encoder'

    def test_catch_library_error_false(self):
        """Test _OutputReader.catch_library_error() -> false."""
        self.conv_lib.reader.update_read('Some random output with '
                                         'no error')
        assert self.conv_lib.reader.catch_library_error() is None

    def test_stop_converter(self):
        """Test Library.stop_converter()."""
        self.conv_lib.stop_converter()
        assert not self.conv_lib.converter_is_running


if __name__ == '__main__':
    nose.run()
