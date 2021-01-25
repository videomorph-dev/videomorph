#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_profiles.py
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

"""This module provides tests for profile.py module."""

import nose
from videomorph.converter.library import Library
from videomorph.converter.profile import Profile

profile = None
conv = Library()


def setup():
    """Function to setup the test."""
    global profile
    profile = Profile()
    profile.update(new_quality="MP4 Fullscreen (4:3)")


def test_get_xml_profile_attr():
    """Test get_xml_profile_attr."""
    attr = profile.get_xml_profile_attr(
        target_quality="MP4 Fullscreen (4:3)", attr_name="preset_params"
    )

    assert (
        attr == "-f mp4 -r 29.97 -vcodec libx264 -s 640x480 -b:v 1000k -aspect 4:3 -flags +loop -cmp +chroma -maxrate 1500k -bufsize 4M -bt 256k -refs 1 -bf 3 -coder 1 -me_method umh -me_range 16 -subq 7 -partitions +parti4x4+parti8x8+partp8x8+partb8x8 -g 250 -keyint_min 25 -level 30 -qmin 10 -qmax 51 -qcomp 0.6 -sc_threshold 40 -i_qfactor 0.71 -acodec aac -b:a 112k -ar 48000 -ac 2 -strict -2"
    )


def test_get_xml_profile_qualities_en():
    """Test get_xml_profile_qualities -> english."""
    qualities = profile.get_xml_profile_qualities("en_US")
    assert qualities["AVI"] == [
        "MS Compatible 640x480",
        "MS Compatible 720x480",
        "XVID Fullscreen 640x480 (4:3)",
        "XVID Widescreen 704x384 (16:9)",
        "AVI Optimized for YouTube",
    ]


def test_get_xml_profile_qualities_es():
    """Test get_xml_profile_qualities -> spanish."""
    qualities = profile.get_xml_profile_qualities("es_ES")
    assert qualities["AVI"] == [
        "Compatible MS 640x480",
        "Compatible MS 720x480",
        "XVID Pantalla Completa 640x480 (4:3)",
        "XVID Pantalla Panorámica 704x384 (16:9)",
        "AVI Optimizado para YouTube",
    ]


def test_quality_tag():
    """Test Profile.quality_tag."""
    assert profile.quality_tag == "[MP4F]-"


@nose.tools.raises(ValueError)
def test_quality_tag_no_regex_tag():
    """Test Profile.quality_tag if not regex tag."""
    global profile
    profile.update(new_quality="wmv generic")
    assert profile.quality_tag == "[WG]-"


def test_update():
    """Test update."""
    profile.update(new_quality="WMV Generic")
    assert (
        profile.params == "-vcodec wmv2 -acodec wmav2 -b:v 1000k "
        "-b:a 160k -r 25"
    )
    assert profile.extension == ".wmv"


if __name__ == "__main__":
    nose.main()
