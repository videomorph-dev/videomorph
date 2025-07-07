"""This module provides CodecsReader Class."""

from itertools import islice

from .launchers import spawn_process
from .vmpath import LIBRARY_PATH


class CodecsReader:
    """Class to get codecs out of ffmpeg -codecs output."""

    def __init__(self):
        self.vcodecs, self.acodecs, self.scodecs = self._read(
            "-codecs", 12
        )
        self.vencoders, self.aencoders, self.sencoders = self._read(
            "-encoders", 11
        )
        self.vdecoders, self.adecoders, self.sdecoders = self._read(
            "-decoders", 11
        )

    def _read(self, param, start):
        """Read the available encoders from ffmpeg."""
        video = {}
        audio = {}
        subtitle = {}
        with spawn_process([LIBRARY_PATH, param]).stdout as output:
            for line in islice(output, start, None):
                functionality, name, *description = line.split()
                if "V" in functionality:
                    video[name] = (functionality, " ".join(description))
                    continue

                if "A" in functionality:
                    audio[name] = (functionality, " ".join(description))
                    continue

                if "S" in functionality:
                    subtitle[name] = (functionality, " ".join(description))

        return video, audio, subtitle
