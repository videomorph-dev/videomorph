# -*- coding: utf-8 -*-

# File name: probe.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
#   Copyright 2016-2020 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""This module provides FFprobe Class."""

from .launchers import spawn_process
from .vmpath import PROBE_PATH


class FFprobe:
    """FFprobe Class to get info about a video."""

    def __init__(
        self, video_path, probe_path=PROBE_PATH, probe_runner=spawn_process
    ):
        """Class initializer."""
        self._probe_path = probe_path
        self._video_path = video_path
        self._probe_runner = probe_runner
        # Set format_info as an attr instead of as a property for efficiency
        self.format_info = self._format_info()

    def _probe(self, args):
        """Return the probe output as a file like object."""
        process_args = [self._probe_path, self._video_path.__str__()]
        process_args[1:-1] = args
        process = self._probe_runner(process_args)
        return process.stdout

    def _parse_probe(self, params, cmd):
        """Parse the probe output."""
        info = dict.fromkeys(params, "Unknown")
        with self._probe(cmd) as probe_file:
            stream_count = -1
            for format_line in probe_file:
                format_line = format_line.strip()
                if "[STREAM]" in format_line:
                    stream_count += 1
                if "=" in format_line:
                    param, value = format_line.split("=")
                    if param in info:
                        info[param] = value
        return info

    def _format_info(self):
        """Parse the probe output."""
        params = {
            "filename",
            "nb_streams",
            "format_name",
            "format_long_name",
            "duration",
            "size",
            "bit_rate",
        }
        return self._parse_probe(
            params=params, cmd=["-show_format"]
        )

    @property
    def video_info(self):
        """Parse the probe output."""
        params = {
            "codec_name",
            "codec_long_name",
            "bit_rate",
            "width",
            "height",
        }
        return self._parse_probe(
            params=params,
            cmd=["-show_streams", "-select_streams", "v"],
        )

    @property
    def audio_info(self):
        """Parse the probe output."""
        params = {"codec_name", "codec_long_name"}
        return self._parse_probe(
            params=params,
            cmd=["-show_streams", "-select_streams", "a"],
        )

    @property
    def subtitle_info(self):
        """Parse the probe output."""
        params = {"codec_name", "codec_long_name", "TAG:language"}
        return self._parse_probe(
            params=params,
            cmd=["-show_streams", "-select_streams", "s"],
        )
