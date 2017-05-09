#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_profiles.py
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

import nose
import xml
from collections import OrderedDict

from videomorph.converter import XMLProfile
from videomorph.converter.profiles import _Profile


xml_profile = XMLProfile()
xml_profile.create_profiles_xml_file()
xml_profile.set_xml_root()

profile = None


def setup():
    global profile
    profile = xml_profile.get_conversion_profile(
        profile_name='MP4',
        target_quality='MP4 Widescreen (16:9)')


def teardown():
    pass


# Tests for XMLProfile class
def test_set_xml_root():
    profile = XMLProfile()
    profile.set_xml_root()
    assert xml.etree.ElementTree.iselement(profile._xml_root)


def test_get_conversion_profile():
    profile = xml_profile.get_conversion_profile(
        profile_name='MP4',
        target_quality='MP4 Fullscreen (4:3)')

    assert isinstance(profile, _Profile)
    assert profile.params == '-f mp4 -r 29.97 -vcodec libx264 -s 640x480 -b:v 1000k -aspect 4:3 -flags +loop -cmp +chroma -deblockalpha 0 -deblockbeta 0 -maxrate 1500k -bufsize 4M -bt 256k -refs 1 -bf 3 -coder 1 -me_method umh -me_range 16 -subq 7 -partitions +parti4x4+parti8x8+partp8x8+partb8x8 -g 250 -keyint_min 25 -level 30 -qmin 10 -qmax 51 -qcomp 0.6 -sc_threshold 40 -i_qfactor 0.71 -acodec aac -b:a 112k -ar 48000 -ac 2 -strict -2'


def test_get_preset_attr():
    attr = xml_profile.get_preset_attr(target_quality='MP4 Fullscreen (4:3)',
                                       attr_index=1)

    assert attr == '-f mp4 -r 29.97 -vcodec libx264 -s 640x480 -b:v 1000k -aspect 4:3 -flags +loop -cmp +chroma -deblockalpha 0 -deblockbeta 0 -maxrate 1500k -bufsize 4M -bt 256k -refs 1 -bf 3 -coder 1 -me_method umh -me_range 16 -subq 7 -partitions +parti4x4+parti8x8+partp8x8+partb8x8 -g 250 -keyint_min 25 -level 30 -qmin 10 -qmax 51 -qcomp 0.6 -sc_threshold 40 -i_qfactor 0.71 -acodec aac -b:a 112k -ar 48000 -ac 2 -strict -2'


def test_get_qualities_per_profile():
    qualities = xml_profile.get_qualities_per_profile(locale='es_ES')
    print(qualities)
    assert qualities == OrderedDict([('MP4', ['MP4 Alta Calidad', 'MP4 Muy Alta Calidad', 'MP4 Súper Alta Calidad', 'MP4 Pantalla Completa (4:3)', 'MP4 Pantalla Panorámica (19:9)']), ('DVD', ['DVD Pantalla Completa (4:3)', 'DVD Pantalla Panorámica (16:9)', 'DVD Pantalla Completa (4:3) Alta Calidad', 'DVD Pantalla Panorámica (16:9) Alta Calidad', 'DVD Baja Calidad']), ('VCD', ['VCD Alta Calidad']), ('AVI', ['Compatible MS', 'XVID Pantalla Completa (4:3)', 'XVID Pantalla Panorámica (16:9)']), ('FLV', ['FLV Pantalla Completa (4:3)', 'FLV Pantalla Panorámica (16:9)']), ('WMV', ['WMV Genérico']), ('WEBM', ['WEBM Pantalla Completa (4:3)', 'WEBM Pantalla Panorámica (16:9)'])])


# Tests for _Profile class
def test_quality_tag():
    assert profile.quality_tag == '[MP4W]'


def test_get_quality():
    assert profile.quality == 'MP4 Widescreen (16:9)'


def test_quality():
    profile.quality = 'WMV Generic'
    assert profile.params == '-vcodec wmv2 -acodec wmav2 -b:v 1000k -b:a 160k -r 25'
    assert profile.extension == '.wmv'



if __name__ == '__main__':
    nose.main()
