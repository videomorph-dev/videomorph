#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_converter.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
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

from videomorph.converter import CONV_LIB
from videomorph.converter import PROBER
from videomorph.converter import media
from videomorph.converter.conversionlib import ConversionLib
from videomorph.converter.profile import ConversionProfile

conv_lib = ConversionLib()

profile = ConversionProfile(prober=conv_lib.prober_path)
profile.update(new_quality='DVD Fullscreen (4:3)')

media_list = media.MediaList(profile)


def teardown():
    """Clean up when finished."""
    media_list.clear()
    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    next(gen)
    media_list.get_file(0).delete_output('.', tagged_output=True)


# Set of test for converter module
def test_get_system_lib():
    """Test the system library."""
    assert conv_lib.get_system_library_name() == CONV_LIB.ffmpeg


def test_name():
    """Test conversion library name."""
    assert conv_lib.name == CONV_LIB.ffmpeg


def test_prober():
    """Test the prober name."""
    assert conv_lib.prober_path == PROBER.ffprobe


def test_start_converter():
    """Test start converter."""

    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    next(gen)

    cmd = media_list.get_file(position=0).build_conversion_cmd(
        output_dir='.',
        subtitle=False,
        tagged_output=True,
        target_quality='DVD Fullscreen (4:3)')

    conv_lib.start_converter(cmd)

    assert conv_lib.converter_state() == QProcess.Starting


def test_stop_converter():
    """Test stop converter."""
    conv_lib.stop_converter()
    assert not conv_lib.converter_is_running


if __name__ == '__main__':
    nose.run()
