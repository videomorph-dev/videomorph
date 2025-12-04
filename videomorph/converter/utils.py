from locale import getlocale
from typing import Union


def get_locale() -> str:
    """Return the default locale string or en_US."""
    try:
        locale_info = getlocale()
        if locale_info and locale_info[1] and locale_info[1].startswith("es_"):
            return "es_ES"
        return "en_US"
    except (TypeError, AttributeError):
        return "en_US"  # Fallback to English


def write_time(time_in_secs: Union[int, float, str]) -> str:
    """Return time in 00h:00m:00s format."""
    try:
        time = round(float(time_in_secs))
    except (TypeError, ValueError):
        raise ValueError("Invalid time measure.")

    if time < 0:
        raise ValueError("Time must be positive.")

    hours = time // 3600
    minutes = time // 60 - hours * 60
    secs = time - minutes * 60 - hours * 3600

    if hours:  # return the time in 00h:00m:00s format
        return "{hours:02d}h:{minutes:02d}m:{secs:02d}s".format(
            hours=hours, minutes=minutes, secs=secs
        )

    if minutes:  # return the time in 00m:00s format
        return "{minutes:02d}m:{secs:02d}s".format(minutes=minutes, secs=secs)

    # return the time in 00s format
    return "{secs:02d}s".format(secs=secs)


def write_size(size_in_bytes: Union[int, float, str]) -> str:
    """Return size in appropriate measure."""
    try:
        size = round(float(size_in_bytes))
    except (TypeError, ValueError):
        raise ValueError("Invalid size measure.")

    if size < 0:
        raise ValueError("Size must be positive.")

    kib = size / 1024
    if kib <= 1024:
        return str(round(kib, 1)) + "KiB"
    mib = kib / 1024
    if mib <= 1024:
        return str(round(mib, 1)) + "MiB"
    gib = mib / 1024
    return str(round(gib, 1)) + "GiB"


def search_directory_recursively(
    directory: str, files: list[str] | None = None
) -> list[str]:
    """Return a list of video files found recursively under ``directory``."""
    from pathlib import Path
    from videomorph.converter.constants import VALID_VIDEO_EXT

    if files is None:
        files = []

    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise IsADirectoryError(f"Directory: {directory}, doesn't exist")

    for path in dir_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in VALID_VIDEO_EXT:
            files.append(str(path))

    if not files:
        raise FileNotFoundError(f"No Video Files Found in: {directory}")

    return files
