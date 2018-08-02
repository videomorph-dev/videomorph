#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_media.py
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

"""This module provides tests for media.py module."""

import nose

from videomorph.converter.conversionlib import ConversionLib
from videomorph.converter.media import MediaList
from videomorph.converter.media import _MediaFile
from videomorph.converter.profile import ConversionProfile
from videomorph.converter import STATUS

conv_lib = ConversionLib()

profile = ConversionProfile(prober=conv_lib.prober_path)
profile.update(new_quality='DVD Fullscreen 352x480 (4:3)')


# Set of tests for media.MediaList class
def test_clear():
    """Test MediaList.clear()."""
    media_list = MediaList(profile=profile)
    media_list.populate('Dad.mpg')
    media_list.clear()
    assert not media_list


def test_populate_files_count():
    """Test MediaList.populate() yield amount of video files."""
    media_list = MediaList(profile=profile)
    gen = media_list.populate(('Dad.mpg',))
    assert next(gen) == 1


def test_populate_first_file_name():
    """Test MediaList.populate() yield first video file name."""
    media_list = MediaList(profile=profile)
    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    assert next(gen) == 'Dad.mpg'


def test_populate():
    """Test MediaList.populate()."""
    media_list = MediaList(profile=profile)
    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    next(gen)
    assert len(media_list) == 1 == media_list.length
    assert media_list[0].input_path == 'Dad.mpg'


def test_delete_file():
    """Test MediaList.delete_file()."""
    media_list = MediaList(profile=profile)
    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    next(gen)
    # Be sure there is one element in the list
    assert len(media_list) == 1
    media_list.delete_file(position=0)
    assert len(media_list) == 0


def test_get_file_object():
    """Test MediaList.get_file()."""
    media_list = MediaList(profile=profile)
    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    next(gen)
    assert isinstance(media_list.get_file(0), _MediaFile)


def test_get_file_name():
    """Test MediaList.get_file_name()."""
    media_list = MediaList(profile=profile)
    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    next(gen)
    assert media_list.get_file_name(position=0) == 'Dad'


def test_get_file_name_with_extension():
    """Test MediaList.get_file_name() with extension."""
    media_list = MediaList(profile=profile)
    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    next(gen)
    assert media_list.get_file_name(position=0,
                                    with_extension=True) == 'Dad.mpg'


def test_get_file_path():
    """Test MediaList.get_file_path()."""
    media_list = MediaList(profile=profile)
    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    next(gen)
    assert media_list.get_file_path(position=0) == 'Dad.mpg'


def test_get_file_status():
    """Test MediaList.get_file_status()."""
    media_list = MediaList(profile=profile)
    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    next(gen)
    assert media_list.get_file_status(position=0) == STATUS.todo


def test_set_file_status():
    """Test MediaList.set_file_status()."""
    media_list = MediaList(profile=profile)
    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    next(gen)
    media_list.set_file_status(0, STATUS.done)
    assert media_list.get_file_status(position=0) == STATUS.done


def test_duration():
    """Test duration."""
    media_list = MediaList(profile=profile)
    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    next(gen)
    nose.tools.assert_almost_equal(media_list.duration, 120.72)


@nose.tools.raises(StopIteration)
def test_add_file_twice():
    """Testing adding the same file twice."""
    media_list = MediaList(profile=profile)
    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    next(gen)
    assert media_list.length == 1
    gen1 = media_list.populate(('Dad.mpg',))
    next(gen1)


def test_build_conversion_cmd():
    """Test build_conversion_cmd."""
    media_list = MediaList(profile=profile)
    gen = media_list.populate(('Dad.mpg',))
    next(gen)
    next(gen)
    assert media_list.get_file(0).build_conversion_cmd(
        output_dir='.',
        tagged_output=True,
        subtitle=True,
        target_quality='DVD Fullscreen 352x480 (4:3)') == ['-i', 'Dad.mpg',
                                                           '-f', 'dvd',
                                                           '-target',
                                                           'ntsc-dvd',
                                                           '-vcodec',
                                                           'mpeg2video', '-r',
                                                           '29.97', '-s',
                                                           '352x480',
                                                           '-aspect', '4:3',
                                                           '-b:v',
                                                           '4000k', '-mbd',
                                                           'rd',
                                                           '-cmp', '2',
                                                           '-subcmp',
                                                           '2', '-acodec',
                                                           'mp2',
                                                           '-b:a', '192k',
                                                           '-ar',
                                                           '48000', '-ac', '2',
                                                           '-threads', '3',
                                                           '-y',
                                                           './[DVDF]-Dad.mpg']


if __name__ == '__main__':
    nose.main()
