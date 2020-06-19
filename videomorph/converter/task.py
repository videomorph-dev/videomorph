# -*- coding: utf-8 -*-

# File name: task.py
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

"""This module provides Conversion Task Class."""

import shlex
from os import W_OK, access
from pathlib import Path

from . import CPU_CORES, STATUS


class Task:
    """Class to represent a conversion task."""

    def __init__(self, video, profile, output_dir):
        self.video = video
        self.profile = profile
        self.output_dir = output_dir
        self.status = STATUS.todo

    def build_conversion_cmd(self, target_quality, tagged, subtitle):
        """Return the conversion command."""
        if not access(self.output_dir, W_OK):
            raise PermissionError("Access denied")

        if not self.video.path.exists():
            raise FileNotFoundError("Input video not found")

        # Ensure the conversion_profile is up to date
        self.profile.update(new_quality=target_quality)

        # Process subtitles if available
        subtitle_opt = self._process_subtitles(subtitle)

        # Get the output path
        output_path = self._get_output_path(tagged)

        # if output_path.exists():
        #     raise FileExistsError('Video file already exits')

        # Build the conversion command
        cmd = (
            ["-i", self.video.path.__str__()]
            + subtitle_opt
            + shlex.split(self.profile.params)
            + ["-threads", str(CPU_CORES)]
            + ["-y", output_path.__str__()]
        )

        return cmd

    def delete_output(self, tagged):
        """Delete the output file if conversion is stopped."""
        while True:
            try:
                output_path = self._get_output_path(tagged)
                output_path.unlink()
                break
            except FileNotFoundError:
                break
            except PermissionError:
                continue

    def delete_input(self):
        """Delete the input file (and subtitle) when conversion is finished."""
        try:
            self.video.path.unlink()
        except FileNotFoundError:
            pass

        try:
            self.subtitle_path.unlink()
        except FileNotFoundError:
            pass

    def get_output_file_name(self, tagged):
        """Return the name of the output video file."""
        output_file = self._get_output_path(tagged)
        return output_file.name

    def get_output_path(self, tagged):
        """Return the the output file path as str."""
        return str(self._get_output_path(tagged))

    def _get_output_path(self, tagged):
        """Return the the output file path as pathlib.Path."""
        tag = self.profile.quality_tag if tagged else ""
        output_file_name = "".join(
            (tag, self.video.get_name(False), self.profile.extension)
        )
        return Path(self.output_dir, output_file_name)

    @property
    def subtitle_path(self):
        """Return the subtitle path as pathlib.Path if it exits."""
        extensions = [".srt", ".ssa", ".stl"]

        # Add uppercase extensions to check if subtitle file exists
        for ext in extensions[:]:
            extensions.append(ext.upper())

        for ext in extensions:
            subtitle_path = self.video.path.with_suffix(ext)
            if subtitle_path.exists():
                return subtitle_path

        raise FileNotFoundError("Subtitle file not found")

    def _process_subtitles(self, subtitle):
        """Process subtitles if available."""
        if subtitle:
            try:
                subtitle_opt = [
                    "-vf",
                    "subtitles='{0}':force_style='Fontsize=24'"
                    ":charenc=cp1252".format(self.subtitle_path.__str__()),
                ]
                return subtitle_opt
            except FileNotFoundError:
                pass

        return []
