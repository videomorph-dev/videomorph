#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File name: media.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg
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
        self.medias = []
        # -1 represent no item running, 0, the first item, 1, second...
        self.running_index = -1

    def __iter__(self):
        """Set up an iterator for MediaList."""
        for media in self.medias:
            yield media

    def clear(self):
        self.medias.clear()
        self.running_index = -1

    def _is_added(self, media_file):
        for media in self.medias:
            if media.path == media_file.path:
                return True
        return False

    def add(self, media_file):
        """Add a media file to the media list."""
        if not isinstance(media_file, MediaFile):
            raise MediaError('Not valid MediaFile object')
        elif self._is_added(media_file):
            raise FileAddedError('File is already added')
        else:
            self.medias.append(media_file)

    def delete_file(self, file_index):
        """Delete a media file from the media list."""
        del self.medias[file_index]

    def get_file(self, file_index):
        return self.medias[file_index]

    def get_running_file(self):
        return self.medias[self.running_index]

    def get_status(self, file_index):
        return self.medias[file_index].status

    def set_status(self, file_index, status):
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
    def __init__(self, file_path=None):
        self.path = file_path
        self.status = STATUS.todo
        self.target_quality = None
        self.info = MediaInfo(file_path)

    def get_file_name(self, with_extension=False):
        full_file_name = self.path.split('/')[-1]
        file_name = '.'.join(full_file_name.split('.')[:-1])

        if with_extension:
            return full_file_name
        return file_name

    def get_info(self, info_param):
        """Return an info attribute from a given file: media_file."""
        return self.info.__dict__.get(info_param)


class MediaInfo(object):

    def __init__(self, media_path):
        self.media_path = media_path
        # Video stream info
        self.v_codec_name = None
        self.v_codec_long_name = None
        self.v_width = None
        self.v_height = None
        self.v_duration = None
        self.v_bit_rate = None
        # Audio stream info
        self.a_codec_name = None
        self.a_codec_long_name = None
        self.a_channels = None
        self.a_channel_layout = None
        self.a_duration = None
        self.a_bit_rate = None
        # Subtitle stream info
        self.s_codec_name = None
        self.s_codec_long_name = None
        # Format info
        self.format_name = None
        self.format_long_name = None
        self.format_bit_rate = None
        self.format_duration = None
        self.file_size = None

        self._parse_ffprobe()

    @staticmethod
    def _spawn(cmd):
        return subprocess.Popen(cmd,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True)

    def _probe(self):
        ffprober = self._spawn([which('ffprobe'),
                                '-show_format',
                                '-show_streams',
                                self.media_path])

        return ffprober.stdout

    def _parse_ffprobe(self):
        def _get_value(line_):
            return line_.split('=')[-1].strip()

        def get_format(f):
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
                elif format_line == '[/FORMAT]':
                    break

        with self._probe() as f:
            for video_line in f:
                if video_line.startswith('codec_name'):
                    self.v_codec_name = _get_value(video_line)
                elif video_line.startswith('codec_long_name'):
                    self.v_codec_long_name = _get_value(video_line)
                elif video_line.startswith('codec_type'):
                    self.v_codec_type = _get_value(video_line)
                elif video_line.startswith('width'):
                    self.v_width = _get_value(video_line)
                elif video_line.startswith('height'):
                    self.v_height = _get_value(video_line)
                elif video_line.startswith('duration'):
                    self.v_duration = _get_value(video_line)
                elif video_line.startswith('bit_rate'):
                    self.v_bit_rate = _get_value(video_line)
                elif video_line == '[/STREAM]\n':
                    break

            for audio_line in f:
                if audio_line == '[FORMAT]\n':
                    get_format(f)
                    break
                if audio_line.startswith('codec_name'):
                    self.a_codec_name = _get_value(audio_line)
                elif audio_line.startswith('codec_long_name'):
                    self.a_codec_long_name = _get_value(audio_line)
                elif audio_line.startswith('codec_type'):
                    self.a_codec_type = _get_value(audio_line)
                elif audio_line.startswith('channels'):
                    self.a_channels = _get_value(audio_line)
                elif audio_line.startswith('duration'):
                    self.a_duration = _get_value(audio_line)
                elif audio_line.startswith('bit_rate'):
                    self.a_bit_rate = _get_value(audio_line)
                elif audio_line == '[/STREAM]\n':
                    break

            for subtitle_line in f:
                if subtitle_line == '[FORMAT]\n':
                    get_format(f)
                    break
                if subtitle_line.startswith('codec_name'):
                    self.s_codec_name = _get_value(subtitle_line)
                elif subtitle_line.startswith('codec_long_name'):
                    self.s_codec_long_name = _get_value(subtitle_line)
                elif subtitle_line == '[/STREAM]\n':
                    break
