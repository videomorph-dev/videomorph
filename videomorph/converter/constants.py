"""Shared constants for the converter package."""

from collections import namedtuple

from videomorph.converter.utils import get_cpu_cores, get_locale

__app_name__ = "VideoMorph"
__version__ = "1.6.0"

LOCALE = get_locale()
CPU_CORES = get_cpu_cores()

VIDEO_FILTERS = (
    "*.mov *.f4v *.webm *.dat *.ogg *.mkv *.wv *.wmv"
    " *.flv *.vob *.ts *.mts *.3gp *.ogv *.mpg *.mp4 *.avi"
)

VALID_VIDEO_EXT = {ext.lstrip("*") for ext in VIDEO_FILTERS.split()}

_MediaFileStatus = namedtuple("MediaFileStatus", "todo done stopped")
STATUS = _MediaFileStatus("Todo", "Done", "Stopped")


__all__ = [
    "__app_name__",
    "__version__",
    "LOCALE",
    "VIDEO_FILTERS",
    "VALID_VIDEO_EXT",
    "_MediaFileStatus",
    "STATUS",
    "CPU_CORES",
    "get_cpu_cores",
]
