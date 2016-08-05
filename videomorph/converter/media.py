#!/usr/bin/env python3
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

import subprocess

from videomorph.converter.utils import which


class MediaError(Exception):
    pass


class FileAddedError(MediaError):
    pass


class MediaFileStatus:
    todo = 'To do'
    done = 'Done!'
    stopped = 'Stopped!'


STATUS = MediaFileStatus()


class MediaList:
    def __init__(self):
        """Class initializer."""
        self.medias = []
        # -1 represent no item running, 0, the first item, 1, second...
        self.running_index = -1

    def __getitem__(self, file_index):
        return self.medias[file_index]

    def clear(self):
        self.medias.clear()
        self.running_index = -1

    def _file_is_added(self, media_file):
        for media in self.medias:
            if media.path == media_file.path:
                return True
        return False

    def add_file(self, media_file):
        """Add a media file to the media list."""
        if not isinstance(media_file, MediaFile):
            raise MediaError('Not valid MediaFile object')
        elif self._file_is_added(media_file):
            raise FileAddedError('File is already added')
        else:
            self.medias.append(media_file)

    def delete_file(self, file_index):
        """Delete a media file from the media list."""
        del self.medias[file_index]

    def get_file(self, file_index):
        return self.medias[file_index]

    def get_file_name(self, file_index, with_extension=False):
        return self.medias[file_index].get_name(with_extension)

    def get_file_path(self, file_index):
        return self.medias[file_index].path

    def get_target_quality(self, file_index):
        return self.medias[file_index].target_quality

    def get_running_file(self):
        return self.get_file(file_index=self.running_index)

    def get_file_status(self, file_index):
        return self.medias[file_index].status

    def set_file_status(self, file_index, status):
        self.medias[file_index].status = status

    def get_file_info(self, file_index, info_param):
        return self.medias[file_index].get_info(info_param)

    @property
    def length(self):
        """Return the number of elements in the list."""
        return len(self.medias)

    @property
    def duration(self):
        """Return the duration time of MediaList counting undone files only."""
        return sum(float(media.info.format_duration) for
                   media in
                   self.medias if not
                   media.status == STATUS.done and not
                   media.status == STATUS.stopped)


class MediaFile:
    def __init__(self, file_path, prober):
        """Class initializer."""
        self.path = file_path
        self.prober = prober
        self.status = STATUS.todo
        self.target_quality = None
        self.info = MediaInfo(self.path, self.prober)

    def get_name(self, with_extension=False):
        full_file_name = self.path.split('/')[-1]
        file_name = '.'.join(full_file_name.split('.')[:-1])

        if with_extension:
            return full_file_name
        return file_name

    def get_info(self, info_param):
        """Return an info attribute from a given file: media_file."""
        return self.info.__dict__.get(info_param)


class MediaInfo:
    def __init__(self, media_path, prober):
        self.media_path = media_path
        self.prober = prober
        # Format info
        self.format_name = None
        self.format_long_name = None
        self.format_bit_rate = None
        self.format_duration = None
        self.file_size = None

        self._parse_probe()

    @staticmethod
    def _spawn(cmd):
        return subprocess.Popen(cmd,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True)

    def _probe(self):
        prober = self._spawn([which(self.prober),
                              '-show_format',
                              self.media_path])

        return prober.stdout

    def _parse_probe(self):
        def _get_value(line_):
            return line_.split('=')[-1].strip()

        with self._probe() as f:
            for format_line in f:
                format_line = format_line.strip()
                if format_line.startswith('format_name'):
                    self.format_name = _get_value(format_line)
                elif format_line.startswith('format_long_name'):
                    self.format_long_name = _get_value(format_line)
                elif format_line.startswith('duration'):
                    self.format_duration = _get_value(format_line)
                elif format_line.startswith('bit_rate'):
                    self.f_bit_rate = _get_value(format_line)
                elif format_line.startswith('size'):
                    self.file_size = _get_value(format_line)