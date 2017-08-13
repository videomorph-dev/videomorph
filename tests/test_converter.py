#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_converter.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg and avconv.
#   Copyright 2015-2016 VideoMorph Development Team

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
from videomorph.converter import XMLProfile
from videomorph.converter import ConversionLib
from videomorph.converter.conversionlib import get_conversion_lib

conv_lib = ConversionLib()


# Set of test for Converter class
def setup():
    """Function to setup the test."""
    xml_profile = XMLProfile()
    xml_profile.create_xml_profiles_file()
    xml_profile.set_xml_root()

    media_list = media.MediaList()

    media_file = media.MediaFile(
        file_path='Dad.mpg',
        conversion_profile=xml_profile.get_xml_profile(
            profile_name='DVD',
            target_quality='DVD Fullscreen (4:3)',
            prober=conv_lib.prober))

    media_list.add_file(media_file)

    conv_lib.start_converter(cmd=media_file.build_conversion_cmd(
        output_dir='.', target_quality='DVD Fullscreen (4:3)'))


def teardown():
    """Function to clean after tests are done."""
    conv_lib.close_converter()
    conv_lib.kill_converter()


def test_conversion_lib():
    """Test the conversion library name."""
    assert conv_lib.name == CONV_LIB.ffmpeg


def test_prober():
    """Test the prober name."""
    assert conv_lib.prober == PROBER.ffprobe


def test_is_running():
    """Test is_running."""
    assert conv_lib.converter_state() == QProcess.Starting


def test_get_conversion_lib():
    """Test the conversion library installed on the system."""
    assert get_conversion_lib() == CONV_LIB.ffmpeg


if __name__ == '__main__':
    nose.run()
