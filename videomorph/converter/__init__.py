"""This module defines the converter package."""

from collections import namedtuple
from typing import Callable, Optional

from .utils import get_locale
from .vmpath import BASE_DIR, SYS_PATHS, VM_PATHS

try:
    from os import cpu_count
except ImportError:
    cpu_count: Optional[Callable[[], Optional[int]]] = None


def get_cpu_cores() -> int:
    """Get the number of CPU cores available for processing.

    Returns:
        Number of CPU cores minus 1 (to leave one core free), or 1 as minimum.
    """
    if cpu_count is None:
        return 1

    cores = cpu_count()
    if cores is None or cores <= 1:
        return 1
    return cores - 1


APP_NAME = "VideoMorph"
VERSION = "1.6.0"
LOCALE = get_locale()

VIDEO_FILTERS = (
    "*.mov *.f4v *.webm *.dat *.ogg *.mkv *.wv *.wmv"
    " *.flv *.vob *.ts *.mts *.3gp *.ogv *.mpg *.mp4 *.avi"
)

VALID_VIDEO_EXT = {ext.lstrip("*") for ext in VIDEO_FILTERS.split()}

MediaFileStatus = namedtuple("MediaFileStatus", "todo done stopped")
STATUS = MediaFileStatus("Todo", "Done", "Stopped")

CPU_CORES = get_cpu_cores()

# Export these for use by other modules
__all__ = [
    "APP_NAME",
    "VERSION",
    "LOCALE",
    "VIDEO_FILTERS",
    "VALID_VIDEO_EXT",
    "MediaFileStatus",
    "STATUS",
    "CPU_CORES",
    "get_cpu_cores",
    "BASE_DIR",
    "SYS_PATHS",
    "VM_PATHS",
]
