#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_profiles.py
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

"""This module provides tests for profile.py module."""

import xml
from collections import OrderedDict

import nose

from videomorph.converter import ConversionProfile
from videomorph.converter import ConversionLib
from videomorph import PROBER


profile = None
conv = ConversionLib()


def setup():
    """Function to setup the test."""
    global profile
    profile = ConversionProfile(prober=conv.prober)
    profile.update(new_quality='MP4 Fullscreen (4:3)')


# Tests for _XMLProfile class
def test_set_xml_root():
    """Test set_xml_root."""
    profile.set_xml_root()
    assert xml.etree.ElementTree.iselement(profile._xml_root)


def test_get_xml_profile_attr():
    """Test get_xml_profile_attr."""
    attr = profile.get_xml_profile_attr(target_quality='MP4 Fullscreen (4:3)',
                                        attr_name='preset_params')

    assert attr == '-f mp4 -r 29.97 -vcodec libx264 -s 640x480 -b:v 1000k ' \
                   '-aspect 4:3 -flags +loop -cmp +chroma -deblockalpha 0 ' \
                   '-deblockbeta 0 -maxrate 1500k -bufsize 4M -bt 256k ' \
                   '-refs 1 -bf 3 -coder 1 -me_method umh -me_range 16 ' \
                   '-subq 7 -partitions +parti4x4+parti8x8+partp8x8+partb8x8 '\
                   '-g 250 -keyint_min 25 -level 30 -qmin 10 -qmax 51 ' \
                   '-qcomp 0.6 -sc_threshold 40 -i_qfactor 0.71 -acodec aac ' \
                   '-b:a 112k -ar 48000 -ac 2 -strict -2'


def test_get_xml_profile_qualities():
    """Test get_xml_profile_qualities."""
    qualities = profile.get_xml_profile_qualities(locale='es_ES')
    assert qualities == OrderedDict(
        [('AVI',
          ['Compatible MS',
           'XVID Pantalla Completa (4:3)',
           'XVID Pantalla Panorámica (16:9)']),
         ('DVD',
          ['DVD Pantalla Completa (4:3)',
           'DVD Pantalla Panorámica (16:9)',
           'DVD Pantalla Completa (4:3) Alta Calidad',
           'DVD Pantalla Panorámica (16:9) Alta Calidad',
           'DVD Baja Calidad']),
         ('FLV',
          ['FLV Pantalla Completa (4:3)',
           'FLV Pantalla Panorámica (16:9)']),
         ('MP4',
          ['MP4 Alta Calidad',
           'MP4 Muy Alta Calidad',
           'MP4 Súper Alta Calidad',
           'MP4 Pantalla Completa (4:3)',
           'MP4 Pantalla Panorámica (16:9)']),
         ('VCD',
          ['VCD Alta Calidad']),
         ('WEBM',
          ['WEBM Pantalla Completa (4:3)',
           'WEBM Pantalla Panorámica (16:9)']),
         ('WMV',
          ['WMV Genérico']),
         ('MP3',
          ['Extraer Audio mp3'])])


# Tests for _Profile class
def test_quality_tag():
    """Test quality_tag."""
    assert profile.quality_tag == '[MP4F]'


def test_update():
    """Test update."""
    profile.update(new_quality='WMV Generic')
    assert profile.params == '-vcodec wmv2 -acodec wmav2 -b:v 1000k ' \
                             '-b:a 160k -r 25'
    assert profile.extension == '.wmv'


if __name__ == '__main__':
    nose.main()
