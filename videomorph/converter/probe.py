"""This module provides Probe Class."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union

from .launchers import spawn_process
from .vmpath import PROBE_PATH


class Probe:
    """Probe Class to get info about a video."""

    def __init__(
        self,
        video_path: Union[str, Path],
        probe_path: Optional[str] = PROBE_PATH,
        probe_runner: Callable = spawn_process,
    ) -> None:
        """Class initializer."""
        self._probe_path = probe_path
        self._video_path = video_path
        self._probe_runner = probe_runner

        self.format_info = self._parse_probe_format()
        self.video_info = self._parse_probe_video_stream()
        self.audio_info = self._parse_probe_audio_stream()
        self.subtitle_info = self._parse_probe_sub_stream()

    def _probe(self, args: List[str]) -> Any:
        """Return the probe output as a file like object."""
        process_args = [self._probe_path, self._video_path.__str__()]
        process_args[1:-1] = args
        process = self._probe_runner(process_args)

        return process.stdout

    def _parse_probe(
        self, selected_params: Set[str], cmd: List[str]
    ) -> Dict[str, str]:
        """Parse the probe output."""
        info = {}

        with self._probe(cmd) as probe_file:
            stream_count = -1

            for format_line in probe_file:
                format_line = format_line.strip()
                param = format_line.split("=")

                if "[STREAM]" in format_line:
                    stream_count += 1

                if "=" in format_line and param[0] in selected_params:
                    if param[0] not in info:
                        info[param[0]] = param[1]
                    else:
                        info[param[0] + "_{0}".format(stream_count)] = param[1]

        return info

    def _parse_probe_format(self) -> Dict[str, str]:
        """Parse the probe output."""
        selected_params = {
            "filename",
            "nb_streams",
            "format_name",
            "format_long_name",
            "duration",
            "size",
            "bit_rate",
        }

        return self._parse_probe(
            selected_params=selected_params, cmd=["-show_format"]
        )

    def _parse_probe_video_stream(self) -> Dict[str, str]:
        """Parse the probe output."""
        selected_params = {
            "codec_name",
            "codec_long_name",
            "bit_rate",
            "width",
            "height",
        }

        return self._parse_probe(
            selected_params=selected_params,
            cmd=["-show_streams", "-select_streams", "v"],
        )

    def _parse_probe_audio_stream(self) -> Dict[str, str]:
        """Parse the probe output."""
        selected_params = {"codec_name", "codec_long_name"}

        return self._parse_probe(
            selected_params=selected_params,
            cmd=["-show_streams", "-select_streams", "a"],
        )

    def _parse_probe_sub_stream(self) -> Dict[str, str]:
        """Parse the probe output."""
        selected_params = {"codec_name", "codec_long_name", "TAG:language"}

        return self._parse_probe(
            selected_params=selected_params,
            cmd=["-show_streams", "-select_streams", "s"],
        )
