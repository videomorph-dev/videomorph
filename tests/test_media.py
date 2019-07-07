#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_media.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
#   Copyright 2016-2018 VideoMorph Development Team

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

from videomorph.converter.library import Library
from videomorph.converter.media import TaskList
from videomorph.converter.media import Video
from videomorph.converter.profile import Profile
from videomorph.converter import STATUS


class TestMedia:
    """Class for testing media.py module."""

    conv_lib = Library()
    profile = Profile(prober=conv_lib.prober_path)
    profile.update(new_quality='DVD Fullscreen 352x480 (4:3)')

    def setup(self):
        """Setup method."""
        self.media_list = TaskList(profile=self.profile)
        self.gen = self.media_list.populate(('Dad.mpg',))
        next(self.gen)
        next(self.gen)

    def test_populate(self):
        """Test TaskList.populate()."""
        assert len(self.media_list) == 1 == self.media_list.length
        assert self.media_list[0].input_path.__str__() == 'Dad.mpg'

    def test_delete_file(self):
        """Test TaskList.delete_file()."""
        # Be sure there is one element in the list
        assert self.media_list
        self.media_list.delete_file(position=0)
        assert not self.media_list

    def test_get_file_object(self):
        """Test TaskList.get_file()."""
        assert isinstance(self.media_list.get_file(0), Video)

    def test_get_file_name(self):
        """Test TaskList.get_file_name()."""
        assert self.media_list.get_file_name(position=0) == 'Dad'

    def test_get_file_name_with_extension(self):
        """Test TaskList.get_file_name() with extension."""
        assert self.media_list.get_file_name(position=0,
                                             with_extension=True) == 'Dad.mpg'

    def test_get_file_path(self):
        """Test TaskList.get_file_path()."""
        assert self.media_list.get_file_path(position=0).__str__() == 'Dad.mpg'

    def test_get_file_status(self):
        """Test TaskList.get_file_status()."""
        assert self.media_list.get_task_status(position=0) == STATUS.todo

    def test_set_file_status(self):
        """Test TaskList.set_file_status()."""
        self.media_list.set_task_status(0, STATUS.done)
        assert self.media_list.get_task_status(position=0) == STATUS.done

    def test_get_file_info(self):
        """Test TaskList.get_file_info()."""
        assert self.media_list.get_file_info(0, 'filename') == 'Dad.mpg'

    def test_running_file_name(self):
        """Test TaskList.running_file_name()."""
        self.media_list.position = 0
        assert self.media_list.running_file_name() == 'Dad'

    def test_running_file_info(self):
        """Test TaskList.running_file_info()."""
        self.media_list.position = 0
        assert self.media_list.running_file_info('filename') == 'Dad.mpg'

    def test_running_file_status(self):
        """Test TaskList.running_file_status()."""
        assert self.media_list.running_task_status == STATUS.todo

    def test_set_running_file_status(self):
        """Test TaskList.running_file_status."""
        self.media_list.running_task_status = STATUS.done
        assert self.media_list.running_task_status == STATUS.done

    def test_running_file_output_name(self):
        """Test TaskList.running_file_output_name()."""
        assert self.media_list.running_file_output_name('.', False) == 'Dad.mpg'

    def test_is_exhausted_true(self):
        """Test TaskList.is_exhausted == True."""
        self.media_list.position = 0
        assert self.media_list.is_exhausted

    def test_is_exhausted_false(self):
        """Test TaskList.is_exhausted == False."""
        self.media_list.position = -1
        assert not self.media_list.is_exhausted

    def test_all_stopped_true(self):
        """Test TaskList.all_stopped == True."""
        self.media_list.set_task_status(0, 'Stopped')
        assert self.media_list.all_stopped

    def test_all_stopped_false(self):
        """Test TaskList.all_stopped == False."""
        self.media_list.set_task_status(0, 'Todo')
        assert not self.media_list.all_stopped

    def test_length(self):
        """Test TaskList.length."""
        assert self.media_list.length == 1

    def test_duration(self):
        """Test TaskList.duration()."""
        nose.tools.assert_almost_equal(self.media_list.duration, 120.72)

    def test_add_file_twice(self):
        """Testing adding the same file twice."""
        assert self.media_list.length == 1
        self.media_list.populate(('Dad.mpg',))
        assert self.media_list.length == 1

    def test_build_conversion_cmd(self):
        """Test Video.build_conversion_cmd."""
        assert self.media_list.get_file(0).build_conversion_cmd(
            output_dir='.',
            tagged=True,
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
                                                               '[DVDF]-Dad.mpg']

    def test_running_file_conversion_cmd(self):
        """Test TaskList.running_file_conversion_cmd()."""
        assert self.media_list.running_task_conversion_cmd(
            output_dir='.',
            tagged=True,
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
                                                               '[DVDF]-Dad.mpg']

    @nose.tools.raises(PermissionError)
    def test_running_file_conversion_cmd_permission_error(self):
        """Test TaskList.running_file_conversion_cmd() -> PermissionError."""
        self.media_list.running_task_conversion_cmd(
            output_dir='/',
            tagged=True,
            subtitle=True,
            target_quality='DVD Fullscreen 352x480 (4:3)')

    def test_clear(self):
        """Test TaskList.clear()."""
        self.media_list.clear()
        assert not self.media_list

    def test_populate_files_count(self):
        """Test TaskList.populate() yield amount of video files."""
        media_list = TaskList(profile=self.profile)
        gen = media_list.populate(('Dad.mpg',))
        assert next(gen) == 1

    def test_populate_first_file_name(self):
        """Test TaskList.populate() yield first video file name."""
        media_list = TaskList(profile=self.profile)
        gen = media_list.populate(('Dad.mpg',))
        next(gen)
        assert next(gen) == 'Dad.mpg'


if __name__ == '__main__':
    nose.main()
