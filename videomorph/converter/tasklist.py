# -*- coding: utf-8 -*-
#
# File name: tasklist.py
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

"""This module provides the definition of TaskList and Video classes."""

from collections import deque
from pathlib import Path

from . import STATUS
from .task import Task
from .video import Video


class TaskList(list):
    """Class to store the list of video files to convert."""

    def __init__(self, profile, output_dir=Path.home()):
        """Class initializer."""
        super(TaskList, self).__init__()
        self._profile = profile
        self._position = None  # None, no item running, 0, the first item,...
        self.not_added_files = deque()
        self._output_dir = output_dir

    @property
    def output_dir(self):
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value):
        self._output_dir = value
        for task in self:
            task.output_dir = value

    def clear(self):
        """Clear the list of videos."""
        super(TaskList, self).clear()
        self.position = None

    def add_task(self, video_path):
        """Add a task to the task list."""
        video = Video(video_path=video_path)
        if video.is_valid():
            self.append(Task(video, self._profile, self.output_dir))
            return True

        self.not_added_files.append(video_path)
        return False

    def delete_file(self, position):
        """Delete a video file from the list."""
        del self[position]

    def get_task(self, position):
        """Return a file object."""
        return self[position]

    def get_file_name(self, position, with_extension=True):
        """Return the name of a video file."""
        return self[position].video.get_name(with_extension)

    def get_file_path(self, position):
        """Return the input_path to a video file."""
        return self[position].video.path

    def get_task_status(self, position):
        """Return the video file conversion status."""
        return self[position].status

    def set_task_status(self, position, status):
        """Set the video file conversion status."""
        self[position].status = status

    def get_file_info(self, position, info_param):
        """Return general streaming info from a video file."""
        return self[position].video.format_info[info_param]

    def running_file_name(self, with_extension=True):
        """Return the running file name."""
        return self._running_task.video.get_name(with_extension)

    def running_file_info(self, info_param):
        """Return running file info."""
        return self._running_task.video.format_info[info_param]

    @property
    def running_task_status(self):
        """Return file status."""
        return self._running_task.status

    @running_task_status.setter
    def running_task_status(self, status):
        """Set file status."""
        self._running_task.status = status

    def running_task_conversion_cmd(self, target_quality, tagged, subtitle):
        """Return the conversion command."""
        return self._running_task.build_conversion_cmd(
            target_quality, tagged, subtitle
        )

    def running_file_output_name(self, tagged):
        """Return the output name."""
        return self._running_task.get_output_file_name(tagged)

    def delete_running_file_output(self, tagged):
        """Delete output file."""
        self._running_task.delete_output(tagged)

    def delete_running_file_input(self):
        """Delete input file."""
        self._running_task.delete_input()

    @property
    def position(self):
        """self._position getter."""
        if self._position is None:
            return -1

        return self._position

    @position.setter
    def position(self, value):
        """self._position setter."""
        self._position = value

    @property
    def is_exhausted(self):
        """Return True if all file in media list are processed."""
        return self.position + 1 >= self.length

    @property
    def all_stopped(self):
        """Check if all files in the lists have been stopped."""
        for task in self:
            if task.status != STATUS.stopped:
                return False
        return True

    @property
    def all_done(self):
        """Check if all files in the lists have been done."""
        for task in self:
            if task.status != STATUS.done:
                return False
        return True

    @property
    def length(self):
        """Return the number of elements in the list."""
        return self.__len__()

    @property
    def duration(self):
        """Return the duration time of TaskList counting files to do only."""
        if self.position >= 0:
            tasks = self[self.position + 1:]
            return sum(
                float(task.video.format_info["duration"])
                for task in tasks
                if task.status != STATUS.done
            )

        return sum(
            float(task.video.format_info["duration"])
            for task in self
            if task.status != STATUS.done
        )

    @property
    def _running_task(self):
        """Return the task that is currently running."""
        return self[self.position]

    def task_is_added(self, file_path):
        """Determine if a video file is already in the list."""
        for task in self:
            if task.video.path.__str__() == file_path:
                return True
        return False
