"""Shared constants for the converter package."""

from collections import namedtuple

from videomorph.converter.utils import get_cpu_cores, get_locale

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
]
