#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_converter.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg and avconv.
#   Copyright 2016-2017 VideoMorph Development Team

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
from PyQt5.QtCore import QProcess

from videomorph import CONV_LIB
from videomorph import PROBER
from videomorph.converter import media
from videomorph.converter import ConversionLib
from videomorph.converter import ConversionProfile

conv_lib = ConversionLib()

profile = ConversionProfile(quality='DVD Fullscreen (4:3)',
                            prober=conv_lib.prober)

media_list = media.MediaList(profile)


def teardown():
    media_list.clear()
    media_list.populate(('Dad.mpg',))
    media_list.get_file(0).delete_output('.')


# Set of test for converter module
def test_get_system_lib():
    """Test the system library."""
    assert conv_lib.get_system_library_name() == CONV_LIB.ffmpeg


def test_name():
    """Test conversion library name."""
    assert conv_lib.name == CONV_LIB.ffmpeg


def test_prober():
    """Test the prober name."""
    assert conv_lib.prober == PROBER.ffprobe


def test_start_converter():
    """Test start converter."""

    media_list.populate(('Dad.mpg',))

    cmd = media_list.get_file(position=0).build_conversion_cmd(
        output_dir='.',
        target_quality='DVD Fullscreen (4:3)')

    conv_lib.start_converter(cmd)

    assert conv_lib.converter_state() == QProcess.Starting


def test_stop_converter():
    """Test stop converter."""
    conv_lib.stop_converter()
    assert not conv_lib.converter_is_running


if __name__ == '__main__':
    nose.run()
