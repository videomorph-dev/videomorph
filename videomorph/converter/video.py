"""This module provides Video Class."""

from pathlib import Path
from typing import Any, Union

from videomorph.converter.probe import Probe


class Video:
    """Class representing a video file."""

    def __init__(self, video_path: Union[str, Path]) -> None:
        """Class initializer."""
        self.path = Path(video_path)
        self._info = Probe(self.path)

    def __getattr__(self, attr: str) -> Any:
        """Delegate to get info about the video."""
        return getattr(self._info, attr)

    def get_name(self, with_extension: bool = False) -> str:
        """Return the file name."""
        if with_extension:
            return self.path.name
        return self.path.stem

    def is_valid(self) -> bool:
        """Check if a video is valid."""
        try:
            # Video has a valid duration?
            # Duration is > 0
            return float(self.format_info["duration"]) > 0
        except (TypeError, ValueError, KeyError):
            return False
