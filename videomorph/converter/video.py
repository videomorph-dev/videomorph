# -*- coding: utf-8 -*-

# File name: video.py
#
# Copyright (C) 2019 Leodanis Pozo Ramos <lpozor78@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""This module provides Video Class."""

import shlex
from os import W_OK
from os import access
from pathlib import Path

from . import CPU_CORES
from . import STATUS
from .probe import Probe


class Video:
    """Class representing a video file."""

    __slots__ = ('input_path',
                 '_profile',
                 'status',
                 '_info')

    def __init__(self, file_path, profile):
        """Class initializer."""
        self._profile = profile
        self.input_path = Path(file_path)
        self.status = STATUS.todo
        self._info = Probe(self.input_path)

    def __getattr__(self, attr):
        """Delegate to get info about the video."""
        return getattr(self._info, attr)

    def get_name(self, with_extension=False):
        """Return the file name."""
        if with_extension:
            return self.input_path.name
        return self.input_path.stem

    def build_conversion_cmd(self, output_dir, target_quality,
                             tagged_output, subtitle):
        """Return the conversion command."""
        if not access(output_dir, W_OK):
            raise PermissionError('Access denied')

        if not self.input_path.exists():
            raise FileNotFoundError('Input video file not found')

        # Ensure the conversion_profile is up to date
        self._profile.update(new_quality=target_quality)

        # Process subtitles if available
        subtitle_opt = self._process_subtitles(subtitle)

        # Get the output path
        output_path = self._get_output_path(output_dir, tagged_output)

        # if output_path.exists():
        #     raise FileExistsError('Video file already exits')

        # Build the conversion command
        cmd = ['-i', self.input_path.__str__()] + subtitle_opt + \
            shlex.split(self._profile.params) + \
            ['-threads', str(CPU_CORES)] + \
            ['-y', output_path.__str__()]

        return cmd

    def delete_output(self, output_dir, tagged_output):
        """Delete the output file if conversion is stopped."""
        while True:
            try:
                output_path = self._get_output_path(output_dir, tagged_output)
                output_path.unlink()
                break
            except FileNotFoundError:
                break
            except PermissionError:
                continue

    def delete_input(self):
        """Delete the input file (and subtitle) when conversion is finished."""
        try:
            self.input_path.unlink()
        except FileNotFoundError:
            pass

        try:
            self.subtitle_path.unlink()
        except FileNotFoundError:
            pass

    def get_output_file_name(self, output_dir, tagged_output):
        """Return the name of the output video file."""
        output_file = self._get_output_path(output_dir, tagged_output)
        return output_file.name

    def get_output_path(self, output_dir, tagged_output):
        """Return the the output file path as str."""
        return str(self._get_output_path(output_dir, tagged_output))

    def _get_output_path(self, output_dir, tagged_output):
        """Return the the output file path as pathlib.Path."""
        tag = self._profile.quality_tag if tagged_output else ''
        output_file_name = tag + self.get_name() + self._profile.extension
        return Path(output_dir, output_file_name)

    @property
    def subtitle_path(self):
        """Return the subtitle path as pathlib.Path if it exits."""
        extensions = ['.srt', '.ssa', '.stl']

        # Add uppercase extensions to check if subtitle file exists
        [extensions.append(ext.upper()) for ext in extensions[:]]

        for ext in extensions:
            subtitle_path = self.input_path.with_suffix(ext)
            if subtitle_path.exists():
                return subtitle_path

        raise FileNotFoundError('Subtitle file not found')

    def _process_subtitles(self, subtitle):
        """Process subtitles if available."""
        if subtitle:
            try:
                subtitle_opt = ['-vf',
                                "subtitles='{0}':force_style='Fontsize=24'"
                                ":charenc=cp1252".format(
                                    self.subtitle_path.__str__())]
                return subtitle_opt
            except FileNotFoundError:
                pass

        return []
