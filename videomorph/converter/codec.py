"""This module provides CodecsReader Class."""

from itertools import islice

from videomorph.converter.launchers import spawn_process
from videomorph.converter.paths import LIBRARY_PATH


class CodecsReader:
    """Class to get codecs out of ffmpeg -codecs output."""

    def __init__(self):
        if not LIBRARY_PATH:
            # If ffmpeg is not available, initialize with empty dicts
            self.vcodecs = self.acodecs = self.scodecs = {}
            self.vencoders = self.aencoders = self.sencoders = {}
            self.vdecoders = self.adecoders = self.sdecoders = {}
            return
        
        try:
            self.vcodecs, self.acodecs, self.scodecs = self._read(
                "-codecs", 12
            )
            self.vencoders, self.aencoders, self.sencoders = self._read(
                "-encoders", 11
            )
            self.vdecoders, self.adecoders, self.sdecoders = self._read(
                "-decoders", 11
            )
        except (OSError, FileNotFoundError, ValueError, IndexError):
            # If codec reading fails, initialize with empty dicts
            # This allows the app to continue even if ffmpeg is misconfigured
            self.vcodecs = self.acodecs = self.scodecs = {}
            self.vencoders = self.aencoders = self.sencoders = {}
            self.vdecoders = self.adecoders = self.sdecoders = {}

    def _read(self, param, start):
        """Read the available encoders from ffmpeg."""
        video = {}
        audio = {}
        subtitle = {}
        try:
            with spawn_process([LIBRARY_PATH, param]).stdout as output:
                for line in islice(output, start, None):
                    if not line.strip():
                        continue
                    try:
                        functionality, name, *description = line.split()
                        if "V" in functionality:
                            video[name] = (functionality, " ".join(description))
                            continue

                        if "A" in functionality:
                            audio[name] = (functionality, " ".join(description))
                            continue

                        if "S" in functionality:
                            subtitle[name] = (functionality, " ".join(description))
                    except (ValueError, IndexError):
                        # Skip malformed lines
                        continue
        except (OSError, FileNotFoundError):
            # Process failed to start or read
            pass

        return video, audio, subtitle
