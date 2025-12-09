"""Shared constants for the converter package."""

from collections import namedtuple

from videomorph.converter.utils import get_locale

LOCALE = get_locale()

VIDEO_FILTERS = " ".join(
    [
        "*.mov",
        "*.f4v",
        "*.webm",
        "*.ogg",
        "*.mkv",
        "*.wv",
        "*.wmv",
        "*.flv",
        "*.vob",
        "*.ts",
        "*.mts",
        "*.3gp",
        "*.ogv",
        "*.mpg",
        "*.mp4",
        "*.avi",
    ]
)

VALID_VIDEO_EXT = {ext.lstrip("*") for ext in VIDEO_FILTERS.split()}

_MediaFileStatus = namedtuple("MediaFileStatus", "todo done stopped")
STATUS = _MediaFileStatus("Todo", "Done", "Stopped")
