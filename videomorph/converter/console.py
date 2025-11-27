"""Helpers for locating media files."""

from pathlib import Path
from typing import List, Optional

from videomorph.converter.constants import VALID_VIDEO_EXT


def search_directory_recursively(
    directory: str, files: Optional[List[str]] = None
) -> List[str]:
    """Return a list of video files found recursively under ``directory``."""
    if files is None:
        files = []

    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise IsADirectoryError(f"Directory: {directory}, doesn't exist")

    for path in dir_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in VALID_VIDEO_EXT:
            files.append(path.__str__())

    if not files:
        raise FileNotFoundError(f"No Video Files Found in: {directory}")

    return files
