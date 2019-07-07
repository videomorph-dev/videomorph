# -*- coding: utf-8 -*-
#
# File name: tasklist.py
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

"""This module provides the definition of TaskList and Video classes."""

from collections import deque

from . import STATUS
from .video import Video
from .task import Task


class MediaError(Exception):
    """General exception class."""
    pass


class InvalidMetadataError(MediaError):
    """Exception to raise when the file don't have a valid metadata info."""
    pass


class TaskList(list):
    """Class to store the list of video files to convert."""

    def __init__(self, profile):
        """Class initializer."""
        super(TaskList, self).__init__()
        self._profile = profile
        self._position = None  # None, no item running, 0, the first item,...
        self.not_added_files = deque()

    def clear(self):
        """Clear the list of videos."""
        super(TaskList, self).clear()
        self.position = None

    def populate(self, files_paths, output_dir):
        """Populate TaskList object with Video objects.

        Args:
            files_paths (iterable): list of files paths
            output_dir (str): output directory
        Yield:
            Element 1: Total number of video files to process
            Element 2,...: file path for the processed video file
        """
        files_paths_to_add = self._filter_by_path(files_paths)

        if files_paths_to_add is None:
            return

        self.not_added_files.clear()

        # First, it yields the total number of video files to process
        yield len(files_paths_to_add)

        for task in self._task_generator(files_paths_to_add, output_dir):
            try:
                self._add_task(task)
                yield task.video.get_name()
            except InvalidMetadataError:
                self.not_added_files.append(task.video.get_name())
                yield task.video.get_name()

    def delete_file(self, position):
        """Delete a video file from the list."""
        del self[position]

    def get_file(self, position):
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
        return self._running_task.build_conversion_cmd(target_quality,
                                                       tagged,
                                                       subtitle)

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
    def length(self):
        """Return the number of elements in the list."""
        return self.__len__()

    @property
    def duration(self):
        """Return the duration time of TaskList counting files to do only."""
        return sum(float(task.video.format_info['duration']) for
                   task in self if task.status == STATUS.todo)

    @property
    def _running_task(self):
        """Return the task that is currently running."""
        return self[self.position]

    def _add_task(self, task):
        """Add a video file to the list."""
        # Invalid metadata
        try:
            # Duration is not a valid float() argument
            duration = float(task.video.format_info['duration'])
        except (TypeError, ValueError):
            raise InvalidMetadataError('Invalid video duration')

        # Duration = 0
        if duration > 0:
            self.append(task)
        else:
            raise InvalidMetadataError('Video is zero size')

    def _task_generator(self, files_paths, output_dir):
        """Yield Video objects to be added to TaskList."""
        for file_path in files_paths:
            video = Video(file_path)
            yield Task(video, self._profile, output_dir)

    def _filter_by_path(self, files_paths):
        """Return a list with files to add to media list."""
        if self.length:
            filtered_paths = [file_path for file_path in files_paths if
                              self._file_not_added(file_path)]
            if not filtered_paths:
                return None

            return filtered_paths

        return files_paths

    def _file_not_added(self, file_path):
        """Determine if a video file is already in the list."""
        for file in self:
            if file.input_path == file_path:
                return False
        return True
