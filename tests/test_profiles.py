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
from videomorph.converter import XMLProfile

XMLProfile.create_profiles_xml_file()
XMLProfile.set_xml_root()

profile = None


def setup():
    global profile
    profile = XMLProfile.get_conversion_profile(
        profile_name='MP4',
        target_quality='MP4 Widescreen (16:9)')


def teardown():
    pass


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
