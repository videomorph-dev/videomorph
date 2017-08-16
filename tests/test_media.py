#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_media.py
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

"""This module provides tests for media.py module."""

import nose

from videomorph.converter import MediaList
from videomorph.converter import ConversionProfile
from videomorph import PROBER
from videomorph import STATUS


profile = ConversionProfile(prober=PROBER.ffprobe)
profile.update(new_quality='DVD Fullscreen (4:3)')

media_list = MediaList(profile=profile)


# Set of tests for media.MediaList class
def test_populate():
    """Test populate."""
    media_list.populate(('Dad.mpg',))

    assert len(media_list) == 1
    assert media_list[0].input_path == 'Dad.mpg'


def test_clear():
    """Test clear."""
    media_list.populate(('Dad.mpg',))
    # Be sure there is one element in the list
    nose.tools.assert_equal(len(media_list), 1)
    media_list.clear()
    nose.tools.assert_equal(len(media_list), 0)


def test_delete_file():
    """Test delete_file."""
    media_list.populate(('Dad.mpg',))

    # Be sure there is one element in the list
    assert len(media_list) == 1

    media_list.delete_file(position=0)
    assert len(media_list) == 0


def test_get_file_name():
    """Test get_file_name."""
    media_list.populate(('Dad.mpg',))

    assert media_list.get_file_name(position=0) == 'Dad'
    assert media_list.get_file_name(position=0,
                                    with_extension=True) == 'Dad.mpg'


def test_get_file_path():
    """Test get_file."""
    media_list.clear()
    media_list.populate(('Dad.mpg',))
    assert media_list.get_file_path(position=0) == 'Dad.mpg'


def test_lenght():
    """Test length."""
    media_list.clear()
    media_list.populate(('Dad.mpg',))
    nose.tools.assert_equal(media_list.length, 1)


def test_duration():
    """Test duration."""
    media_list.clear()
    media_list.populate(('Dad.mpg',))
    nose.tools.assert_almost_equal(media_list.duration, 120.72)


def test_add_file_twice():
    """Testing adding the same file twice."""
    media_list.clear()
    media_list.populate(('Dad.mpg',))
    media_list.populate(('Dad.mpg',))
    assert media_list.length == 1


def test_get_file_status():
    """Test get the file status."""
    media_list.clear()
    media_list.populate(('Dad.mpg',))
    assert media_list.get_file_status(position=0) == STATUS.todo


def test_set_file_status():
    """Test set the file status."""
    media_list.clear()
    media_list.populate(('Dad.mpg',))
    media_list.set_file_status(0, STATUS.done)
    assert media_list.get_file_status(position=0) == STATUS.done


def test_build_conversion_cmd():
    """Test build_conversion_cmd."""
    media_list.clear()
    media_list.populate(('Dad.mpg',))
    assert media_list.get_file(0).build_conversion_cmd(
        output_dir='.',
        target_quality='DVD Fullscreen (4:3)') == ['-i', 'Dad.mpg', '-f',
                                                   'dvd', '-target',
                                                   'ntsc-dvd', '-vcodec',
                                                   'mpeg2video', '-r',
                                                   '29.97', '-s', '352x480',
                                                   '-aspect', '4:3', '-b:v',
                                                   '4000k', '-mbd', 'rd',
                                                   '-cmp', '2', '-subcmp',
                                                   '2', '-acodec', 'mp2',
                                                   '-b:a', '192k', '-ar',
                                                   '48000', '-ac', '2',
                                                   '-threads', '3', '-y',
                                                   './[DVDF]-Dad.mpg']


if __name__ == '__main__':
    nose.main()
