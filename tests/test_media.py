#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_media.py
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

from videomorph.converter import media
from videomorph.converter import profiles
from videomorph.converter import XMLProfile


# Set of tests for media.MediaFile class
def test_get_name():
    media_file = _get_media_file_obj()
    assert media_file.get_name() == 'Dad'
    # Another way to do this
    nose.tools.assert_equal(media_file.get_name(), 'Dad')

    # With extension
    assert media_file.get_name(with_extension=True) == 'Dad.mpg'


def test_get_info_with_ffprobe():
    media_file = _get_media_file_obj()

    nose.tools.assert_almost_equal(
        float(media_file.get_info('format_duration')),
        120.72)
    # nose.tools.assert_almost_equal(float(media_file.get_info('file_size')),
    #                                21227416.0)
    # nose.tools.assert_equal(media_file.get_info('format_name'),
    #                         'mpeg')
    # nose.tools.assert_equal(media_file.get_info('format_long_name'),
    #                         'MPEG-PS (MPEG-2 Program Stream)')


# def test_get_info_with_avprobe():
#     media_file = _get_media_file_obj(prober='avprobe')
#
#     nose.tools.assert_almost_equal(float(media_file.get_info('format_duration')),
#                                    120.68)
#     nose.tools.assert_almost_equal(float(media_file.get_info('file_size')),
#                                    21227416.0)
#     nose.tools.assert_equal(media_file.get_info('format_name'),
#                             'mpeg')
#     nose.tools.assert_equal(media_file.get_info('format_long_name'),
#                             'MPEG-PS (MPEG-2 Program Stream)')


def test_get_conversion_cmd():
    media_file = _get_media_file_obj()
    assert media_file.get_conversion_cmd('.') == ['-i', 'Dad.mpg', '-f', 'dvd', '-target', 'ntsc-dvd', '-vcodec', 'mpeg2video', '-r', '29.97', '-s', '352x480', '-aspect', '4:3', '-b:v', '4000k', '-mbd', 'rd', '-cmp', '2', '-subcmp', '2', '-acodec', 'mp2', '-b:a', '192k', '-ar', '48000', '-ac', '2', '-threads', '3', '-y', './[DVDF]-Dad.mpg']


def test_profile():
    media_file = _get_media_file_obj()
    assert isinstance(media_file.conversion_profile, profiles._Profile)


# Set of tests for media.MediaList class
def test_add_file():
    media_file = _get_media_file_obj()
    media_list = _get_media_list_obj(empty=True)

    # testing...
    media_list.add_file(media_file)

    assert len(media_list) == 1
    assert isinstance(media_list[0], media.MediaFile)
    assert media_file is media_list[0]


def test_add_file_twice():
    """Testing adding the same file two times."""
    media_file = _get_media_file_obj()
    media_list = _get_media_list_obj(empty=True)

    # test adding the same file twice
    media_list.add_file(media_file)
    media_list.add_file(media_file)
    assert media_list.length == 1


def test_clear():
    media_list = _get_media_list_obj()

    # Be sure there is one element in the list
    nose.tools.assert_equal(len(media_list), 1)

    media_list.clear()
    nose.tools.assert_equal(len(media_list), 0)


def test_delete_file():
    media_list = _get_media_list_obj()

    # Be sure there is one element in the list
    assert len(media_list) == 1

    media_list.delete_file(file_index=0)
    assert len(media_list) == 0


def test_get_file():
    media_list = _get_media_list_obj()

    file = media_list.get_file(file_index=0)
    assert isinstance(file, media.MediaFile)
    assert file is media_list[0]


def test_get_file_name():
    media_list = _get_media_list_obj()

    name = media_list.get_file_name(file_index=0)
    assert name == 'Dad'

    name = media_list.get_file_name(file_index=0, with_extension=True)
    assert name == 'Dad.mpg'


def test_get_file_path():
    media_list = _get_media_list_obj()

    assert media_list.get_file_path(file_index=0) == 'Dad.mpg'


def test_lenght():
    media_list = _get_media_list_obj()

    nose.tools.assert_equal(media_list.length, 1)


def test_duration():
    media_list = _get_media_list_obj()

    # with ffprobe
    nose.tools.assert_almost_equal(media_list.duration, 120.72)


# Helper functions
def _get_media_file_obj(file_path='Dad.mpg', prober='ffprobe'):
    xml_profile = XMLProfile()
    xml_profile.set_xml_root()
    return media.MediaFile(
        file_path,
        conversion_profile=xml_profile.get_conversion_profile(
            profile_name='DVD', target_quality='DVD Fullscreen (4:3)'),
        prober=prober)


def _get_media_list_obj(empty=False):
    media_list = media.MediaList()

    if not empty:
        media_list.add_file(_get_media_file_obj())

    return media_list


if __name__ == '__main__':
    nose.main()
