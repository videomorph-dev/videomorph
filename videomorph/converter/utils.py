import os
from collections.abc import Callable
from locale import getlocale
from os import pathsep
from pathlib import Path
from typing import Optional, Union

try:
    from os import cpu_count
except ImportError:  # pragma: no cover - fallback for exotic platforms
    cpu_count = None  # type: ignore[assignment]


def get_locale() -> str:
    """Return the default locale string or en_US."""
    try:
        locale_info = getlocale()
        if locale_info and locale_info[1] and locale_info[1].startswith("es_"):
            return "es_ES"
        return "en_US"
    except (TypeError, AttributeError):
        return "en_US"  # Fallback to English


def which(app: str) -> str | None:
    """Detect if an app is installed in your system."""
    if not app or not app.strip():
        return None

    sys_paths = os.environ.get("PATH", os.defpath).split(pathsep)

    for path in sys_paths:
        try:
            app_path = Path(path, app)
            if app_path.exists() and app_path.is_file():
                return app_path.__str__()
        except (OSError, PermissionError):
            # Skip paths that can't be accessed
            continue

    return None


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


def get_cpu_cores(detector: Callable[[], Optional[int]] | None = cpu_count) -> int:
    """Return usable CPU cores (leave one core free)."""
    if detector is None:
        return 1

    cores = detector()
    if cores is None or cores <= 1:
        return 1
    return cores - 1
