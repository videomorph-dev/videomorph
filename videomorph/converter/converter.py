#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File name: converter.py
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

"""This module provides the definition of the Converter class."""

import shlex

from PyQt5.QtCore import QProcess

from videomorph.converter import utils
from videomorph.converter.profiles import PROFILES
from videomorph.converter.utils import CONV_LIB


class Converter(QProcess):
    def __init__(self, media_list, conversion_lib=CONV_LIB.ffmpeg):
        """Class initializer."""
        super(Converter, self).__init__()
        self.conversion_lib = conversion_lib
        self.media_list = media_list

    def start(self, *__args):
        super(Converter, self).start(utils.which(self.conversion_lib), *__args)

    @property
    def is_running(self):
        """Return the individual file encoding process state."""
        return self.state() == QProcess.Running

    def start_encoding(self, file_index, output_dir):
        """Start the encoding process."""
        cmd = self._get_conversion_cmd(file_index, output_dir)
        self.start(cmd)

    @property
    def encoding_ended(self):
        """Return True if media list is done."""
        if self.media_list.running_index + 1 >= self.media_list.length:
            return True
        return False

    def _get_output_file_path(self, file_index, output_dir):
        """Return the the output file path."""
        output_file_path = (output_dir +
                            '/' +
                            self._get_profile(file_index).quality_tag +
                            ' ' +
                            self.media_list.get_file_name(file_index) +
                            self._get_profile(file_index).profile_extension)
        return output_file_path

    def _get_profile(self, file_index):
        """Return a profile object."""
        target_quality = self.media_list.get_target_quality(file_index)
        for profile, profile_class in PROFILES.items():
            if target_quality in profile_class.presets:
                profile_name = profile

        profile = PROFILES[profile_name](
            profile_quality=target_quality,
            profile_params=PROFILES[profile_name].presets[target_quality])

        return profile

    def _get_conversion_cmd(self, file_index, output_dir):
        """Return the conversion command."""
        profile = self._get_profile(file_index)
        output_file_path = self._get_output_file_path(file_index, output_dir)

        cmd = ['-i', self.media_list.get_file_path(file_index)] + \
              shlex.split(profile.profile_params) + ['-y', output_file_path]

        return cmd
