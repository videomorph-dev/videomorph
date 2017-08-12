# -*- coding: utf-8 -*-
#
# File name: media.py
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

"""This module provides the definition of MediaList and MediaFile classes."""

import shlex
from os import access
from os import remove
from os import sep
from os import W_OK
from os.path import exists
from os.path import basename
from threading import Thread

from .utils import which
from .utils import spawn_process
from videomorph import CPU_CORES
from videomorph import STATUS


class MediaError(Exception):
    """General exception class."""
    pass


class InvalidMetadataError(MediaError):
    """Exception to raise when the file don't have a valid metadata info."""
    pass


class MediaList(list):
    """Class to store the list of video files to convert."""

    def __init__(self):
        """Class initializer."""
        super(MediaList, self).__init__()
        # -1 represent no item running, 0, the first item, 1, second...
        self.position = -1

    def clear(self):
        """Clear the list of videos."""
        super(MediaList, self).clear()
        self.position = -1

    def add_file(self, media_file):
        """Add a video file to the list."""
        if self._file_is_added(media_file):
            return
        try:
            # Invalid metadata
            duration = float(media_file.get_info('format_duration'))
            if duration > 0:
                self.append(media_file)
            else:
                # 0 duration video file not added
                raise InvalidMetadataError('File is zero length')
        except:
            raise InvalidMetadataError('Invalid file duration')

    def delete_file(self, file_index):
        """Delete a video file from the list."""
        del self[file_index]

    def get_file(self, file_index):
        """Return a file object."""
        return self[file_index]

    def get_file_name(self, file_index, with_extension=False):
        """Return the name of a video file."""
        return self[file_index].get_name(with_extension)

    def get_file_path(self, file_index):
        """Return the input_path to a video file."""
        return self[file_index].input_path

    def get_file_status(self, file_index):
        """Return the video file status."""
        return self[file_index].status

    def set_file_status(self, file_index, status=STATUS.todo):
        """Set the video file status."""
        self[file_index].status = status

    def get_file_info(self, file_index, info_param):
        """Return general streaming info from a video file."""
        return self[file_index].get_info(info_param)

    @property
    def running_file(self):
        """Return the file that is currently running."""
        return self.get_file(file_index=self.position)

    @property
    def is_processed(self):
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
        """Return the duration time of MediaList counting undone files only."""
        return sum(float(media.get_info('format_duration')) for
                   media in self if media.status != STATUS.done and
                   media.status != STATUS.stopped)

    def _file_is_added(self, media_file):
        """Determine if a video file is in the list already."""
        for file in self:
            if file.input_path == media_file.input_path:
                return True
        return False

    @staticmethod
    def media_files_generator(files_paths, conversion_profile):
        """Yield MediaFile objects to be added to MediaList."""
        threads = []
        for file_path in files_paths:
            thread = MediaFileThread(
                media_path=file_path,
                conversion_profile=conversion_profile)
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        for thread in threads:
            yield thread.media_file


class MediaFile:
    """Class representing a video file."""

    __slots__ = ('input_path',
                 'conversion_profile',
                 'status',
                 'info')

    def __init__(self, file_path, conversion_profile):
        """Class initializer."""
        self.input_path = file_path
        self.conversion_profile = conversion_profile
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
        """Return an info attribute from a given file: media_file."""
        return self.info.get(info_param)

    def build_conversion_cmd(self, output_dir, target_quality, subtitle=False):
        """Return the conversion command."""
        if not access(output_dir, W_OK):
            raise PermissionError('Access denied')
        # Ensure the conversion_profile is up to date
        self.conversion_profile.update(new_quality=target_quality)
        # Process subtitles if available
        if subtitle and self._subtitle_path:
            subtitle_opt = ['-vf', "subtitles={0}:force_style='Fontsize=24'"
                                   ":charenc=cp1252".format(
                                       self._subtitle_path)]
        else:
            subtitle_opt = []
        # Get the output path
        output_path = self.get_output_path(output_dir)
        # Build the conversion command
        cmd = ['-i', self.input_path] + subtitle_opt + \
            shlex.split(self.conversion_profile.params) + \
            ['-threads', str(CPU_CORES)] + \
            ['-y', output_path]

        return cmd

    def delete_output(self, output_dir):
        """Delete the output file if conversion is stopped."""
        if exists(self.get_output_path(output_dir)):
            remove(self.get_output_path(output_dir))

    def delete_input(self):
        """Delete the input file when conversion is finished."""
        remove(self.input_path)
        remove(self._subtitle_path)

    def get_output_path(self, output_dir):
        """Return the the output file input_path."""
        output_file_path = (output_dir +
                            sep +  # multi-platform input_path separator
                            self.conversion_profile.quality_tag +
                            '-' +
                            self.get_name() +
                            self.conversion_profile.extension)
        return output_file_path

    @property
    def _subtitle_path(self):
        """Returns the subtitle input_path if exit."""
        extension = self.input_path.split('.')[-1]
        subtitle_path = self.input_path.strip('.' + extension) + '.srt'

        if exists(subtitle_path):
            return subtitle_path

        return None

    def _probe(self):
        """Return the prober output as a file like object."""
        prober_run = spawn_process([which(self.conversion_profile.prober),
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


class MediaFileThread(Thread):
    """Thread class to handle the creation of MediaFile objects."""
    def __init__(self, media_path, conversion_profile):
        super(MediaFileThread, self).__init__()
        self.file_path = media_path
        self.conversion_profile = conversion_profile
        self.media_file = None

    def run(self):
        """Create media files to be added to the list."""
        self.media_file = media_file_factory(self.file_path,
                                             self.conversion_profile)


def media_file_factory(file_path, conversion_profile):
    """Factory function for creating MediaFile objects.

    Args:
        file_path (str): Path to the media file
        conversion_profile (object): profile._Profile object
    Returns:
        media.MediaFile object
    """
    return MediaFile(file_path=file_path,
                     conversion_profile=conversion_profile)
