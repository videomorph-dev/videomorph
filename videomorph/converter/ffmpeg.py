#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#   MediaMorph - A PyQt5 frontend to ffmpeg
#   Copyright 2015-2016 VideoMorph Development Team

#   This file is part of python-video-converter (https://github.com/senko/python-video-converter)
#   and has been modified to fit the VideoMorph requirements

import os.path
import os
import re
import signal
from subprocess import Popen, PIPE
import logging
import locale

from videomorph.converter.media import MediaInfo

logger = logging.getLogger(__name__)

console_encoding = 'UTF-8'


class FFMpegError(Exception):
    pass


class FFMpegConvertError(Exception):

    def __init__(self, message, cmd, output, details=None, pid=0):
        super(FFMpegConvertError, self).__init__(message)

        self.cmd = cmd
        self.output = output
        self.details = details
        self.pid = pid

    def __repr__(self):
        error = self.details if self.details else self.message
        return ('<FFMpegConvertError error="%s", pid=%s, cmd="%s">' %
                (error, self.pid, self.cmd))

    def __str__(self):
        return self.__repr__()


class FFMpeg(object):
    DEFAULT_JPEG_QUALITY = 4

    def __init__(self, ffmpeg_path=None, ffprobe_path=None):

        def which(name):
            path = os.environ.get('PATH', os.defpath)
            for d in path.split(':'):
                fpath = os.path.join(d, name)
                if os.path.exists(fpath) and os.access(fpath, os.X_OK):
                    return fpath
            return None

        if ffmpeg_path is None:
            ffmpeg_path = 'ffmpeg'

        if ffprobe_path is None:
            ffprobe_path = 'ffprobe'

        if '/' not in ffmpeg_path:
            ffmpeg_path = which(ffmpeg_path) or ffmpeg_path
        if '/' not in ffprobe_path:
            ffprobe_path = which(ffprobe_path) or ffprobe_path

        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path

        if not os.path.exists(self.ffmpeg_path):
            raise FFMpegError("ffmpeg binary not found: " + self.ffmpeg_path)

        if not os.path.exists(self.ffprobe_path):
            raise FFMpegError("ffprobe binary not found: " + self.ffprobe_path)

    @staticmethod
    def _spawn(cmds):
        logger.debug('Spawning ffmpeg with command: ' + ' '.join(cmds))
        return Popen(cmds, shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                     close_fds=True)

    def probe(self, fname, posters_as_video=True):
        if not os.path.exists(fname):
            return None

        info = MediaInfo(posters_as_video)

        p = self._spawn([self.ffprobe_path,
                         '-show_format', '-show_streams', fname])
        stdout_data, _ = p.communicate()
        stdout_data = stdout_data.decode(console_encoding)
        info.parse_ffprobe(stdout_data)

        if not info.format.format and len(info.streams) == 0:
            return None

        return info
