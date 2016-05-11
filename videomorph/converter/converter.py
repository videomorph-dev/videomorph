#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File name: converter.py
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

from PyQt5.QtCore import QProcess
from videomorph.converter import utils


class FFmpegConverter(QProcess):
    def start(self, *__args):
        super(FFmpegConverter, self).start(utils.which('ffmpeg'), *__args)

    def is_running(self):
        return self.state() == QProcess.Running
