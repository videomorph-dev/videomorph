# -*- coding: utf-8 -*-
#
# File name: media.py
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

"""This module provides the definition of MediaList and _MediaFile classes."""

import shlex
from collections import deque
from os import W_OK
from os import access
from os import remove
from os import sep
from os.path import basename
from os.path import exists

from . import CPU_CORES
from . import STATUS
from .utils import spawn_process
from .utils import which


class MediaError(Exception):
    """General exception class."""
    pass


class InvalidMetadataError(MediaError):
    """Exception to raise when the file don't have a valid metadata info."""
    pass


class MediaList(list):
    """Class to store the list of video files to convert."""

    def __init__(self, profile):
        """Class initializer."""
        super(MediaList, self).__init__()
        self._profile = profile
        self._position = None  # None, no item running, 0, the first item,...
        self.not_added_files = deque()

    def clear(self):
        """Clear the list of videos."""
        super(MediaList, self).clear()
        self.position = None

    def populate(self, files_paths):
        """Populate MediaList object with _MediaFile objects.

        Args:
            files_paths (iterable): list of files paths
        Yield:
            Element 1: Total number of video files to process
            Element 2,...: file path for the video file processed
        """
        files_paths_to_add = self._filter_by_path(files_paths)

        if files_paths_to_add is None:
            return

        self.not_added_files.clear()

        # First, it yields the total number of video files to process
        yield len(files_paths_to_add)

        for file in self._media_files_generator(files_paths_to_add):
            try:
                self._add_file(file)
                yield file.get_name(with_extension=True)
            except InvalidMetadataError:
                self.not_added_files.append(file.get_name(with_extension=True))
                yield file.get_name(with_extension=True)

    def delete_file(self, position):
        """Delete a video file from the list."""
        del self[position]

    def get_file(self, position):
        """Return a file object."""
        return self[position]

    def get_file_name(self, position, with_extension=False):
        """Return the name of a video file."""
        return self[position].get_name(with_extension)

    def get_file_path(self, position):
        """Return the input_path to a video file."""
        return self[position].input_path

    def get_file_status(self, position):
        """Return the video file status."""
        return self[position].status

    def set_file_status(self, position, status):
        """Set the video file status."""
        self[position].status = status

    def get_file_info(self, position, info_param):
        """Return general streaming info from a video file."""
        return self[position].get_info(info_param)

    def running_file_name(self, with_extension=False):
        """Return the running file name."""
        return self._running_file.get_name(with_extension)

    def running_file_info(self, info_param):
        """Return running file info."""
        return self._running_file.get_info(info_param)

    @property
    def running_file_status(self):
        """Return file status."""
        return self._running_file.status

    @running_file_status.setter
    def running_file_status(self, status):
        """Set file status."""
        self._running_file.status = status

    def running_file_conversion_cmd(self, output_dir, target_quality,
                                    tagged_output, subtitle):
        """Return the conversion command."""
        return self._running_file.build_conversion_cmd(output_dir,
                                                       target_quality,
                                                       tagged_output,
                                                       subtitle)

    def running_file_output_name(self, output_dir, tagged_output):
        """Return the output name."""
        return self._running_file.get_output_file_name(output_dir,
                                                       tagged_output)

    def delete_running_file_output(self, output_dir, tagged_output):
        """Delete output file."""
        self._running_file.delete_output(output_dir, tagged_output)

    def delete_running_file_input(self):
        """Delete input file."""
        self._running_file.delete_input()

    @property
    def position(self):
        """self._position getter."""
        if self._position is None:
            return -1
        else:
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
        for file in self:
            if file.status != STATUS.stopped:
                return False

        return True

    @property
    def length(self):
        """Return the number of elements in the list."""
        return len(self)

    @property
    def duration(self):
        """Return the duration time of MediaList counting files todo only."""
        return sum(float(media.get_info('format_duration')) for
                   media in self if media.status == STATUS.todo)

    @property
    def _running_file(self):
        """Return the file that is currently running."""
        return self[self.position]

    def _add_file(self, media_file):
        """Add a video file to the list."""
        # Invalid metadata
        try:
            # Duration is not a valid float() argument
            duration = float(media_file.get_info('format_duration'))
        except (TypeError, ValueError):
            raise InvalidMetadataError('Invalid file duration')

        # Duration = 0
        if duration > 0:
            self.append(media_file)
        else:
            raise InvalidMetadataError('File is zero length')

    def _media_files_generator(self, files_paths):
        """Yield _MediaFile objects to be added to MediaList."""
        for file_path in files_paths:
            yield _MediaFile(file_path, self._profile)

    def _filter_by_path(self, files_paths):
        """Return a list with files to add to media list."""
        if self.length:
            filtered_paths = [file_path for file_path in files_paths if
                              self._file_not_added(file_path)]
            if not filtered_paths:
                return None
        else:
            filtered_paths = files_paths

        return filtered_paths

    def _file_not_added(self, file_path):
        """Determine if a video file is in the list already."""
        for file in self:
            if file.input_path == file_path:
                return False
        return True


class _MediaFile:
    """Class representing a video file."""

    __slots__ = ('input_path',
                 '_profile',
                 'status',
                 'info')

    def __init__(self, file_path, profile):
        """Class initializer."""
        self._profile = profile
        self.input_path = file_path
        self.status = STATUS.todo
        self.info = self._parse_probe()

    def get_name(self, with_extension=False):
        """Return the file name."""
        full_file_name = basename(self.input_path)
        file_name = full_file_name.split('.')[0]

        if with_extension:
            return full_file_name
        return file_name

    def get_info(self, info_param):
        """Return an info attribute from a given video file."""
        return self.info.get(info_param)

    def build_conversion_cmd(self, output_dir, target_quality,
                             tagged_output, subtitle):
        """Return the conversion command."""
        if not access(output_dir, W_OK):
            raise PermissionError('Access denied')

        if not exists(self.input_path):
            raise FileNotFoundError('Input video file not found')

        # Ensure the conversion_profile is up to date
        self._profile.update(new_quality=target_quality)

        # Process subtitles if available
        subtitle_opt = self._process_subtitles(subtitle)

        # Get the output path
        output_path = self.get_output_path(output_dir, tagged_output)

        if exists(output_path):
            raise FileExistsError('Video file already exits')

        # Build the conversion command
        cmd = ['-i', self.input_path] + subtitle_opt + \
            shlex.split(self._profile.params) + \
              ['-threads', str(CPU_CORES)] + \
            ['-y', output_path]

        return cmd

    def delete_output(self, output_dir, tagged_output):
        """Delete the output file if conversion is stopped."""
        try:
            remove(self.get_output_path(output_dir, tagged_output))
        except FileNotFoundError:
            pass

    def delete_input(self):
        """Delete the input file (and subtitle) when conversion is finished."""
        try:
            remove(self.input_path)
        except FileNotFoundError:
            pass

        try:
            remove(self._subtitle_path)
        except FileNotFoundError:
            pass

    def get_output_file_name(self, output_dir, tagged_output):
        """Return the name of the output video file."""
        file_name = basename(self.get_output_path(output_dir, tagged_output))

        return file_name

    def get_output_path(self, output_dir, tagged_output):
        """Return the the output file input_path."""
        tag = self._profile.quality_tag if tagged_output else ''

        output_file_path = (output_dir +
                            sep +  # multi-platform input_path separator
                            tag +
                            self.get_name() +
                            self._profile.extension)
        return output_file_path

    @property
    def _subtitle_path(self):
        """Returns the subtitle input_path if exit."""
        extension = self.input_path.split('.')[-1]
        subtitle_path = self.input_path.strip('.' + extension) + '.srt'

        if exists(subtitle_path):
            return subtitle_path
        else:
            raise FileNotFoundError('Subtitle file not found')

    def _process_subtitles(self, subtitle):
        # Process subtitles if available
        if subtitle:
            try:
                subtitle_opt = ['-vf',
                                "subtitles='{0}':force_style='Fontsize=24'"
                                ":charenc=cp1252".format(
                                    self._subtitle_path)]
                return subtitle_opt
            except FileNotFoundError:
                pass

        return []

    def _probe(self):
        """Return the prober output as a file like object."""
        prober_run = spawn_process([which(self._profile.prober),
                                    '-show_format',
                                    self.input_path])

        return prober_run.stdout

    def _parse_probe(self):
        """Parse the prober output."""
        info = {}

        def __get_value(line_):
            """Prepare the data for parsing."""
            return line_.split('=')[-1].strip()

        with self._probe() as probe_file:
            for format_line in probe_file:
                format_line = format_line.strip()
                if format_line.startswith('duration'):
                    info['format_duration'] = __get_value(format_line)
                    break
        return info
