"""This module provides codec information reading from ffmpeg."""

from dataclasses import dataclass
from itertools import islice
from typing import Dict

from videomorph.converter.launchers import spawn_process
from videomorph.converter.paths import LIBRARY_PATH


@dataclass(frozen=True, slots=True)
class CodecData:
    """Immutable container for codec information from ffmpeg."""

    vcodecs: Dict[str, tuple[str, str]]
    acodecs: Dict[str, tuple[str, str]]
    scodecs: Dict[str, tuple[str, str]]
    vencoders: Dict[str, tuple[str, str]]
    aencoders: Dict[str, tuple[str, str]]
    sencoders: Dict[str, tuple[str, str]]
    vdecoders: Dict[str, tuple[str, str]]
    adecoders: Dict[str, tuple[str, str]]
    sdecoders: Dict[str, tuple[str, str]]


def read_codecs() -> CodecData:
    """Read codec information from ffmpeg.

    Returns:
        CodecData: Immutable container with all codec information.

    Raises:
        RuntimeError: If codec reading fails or returns no data.
    """
    try:
        vcodecs, acodecs, scodecs = _read_codec_list("-codecs", start_line=12)
        vencoders, aencoders, sencoders = _read_codec_list("-encoders", start_line=11)
        vdecoders, adecoders, sdecoders = _read_codec_list("-decoders", start_line=11)
    except (OSError, FileNotFoundError, ValueError, IndexError, TypeError) as e:
        raise RuntimeError(
            f"Failed to read codec information from ffmpeg. "
            f"This may indicate ffmpeg is corrupted or incompatible. "
            f"Details: {e}"
        ) from e

    # Verify we got some codecs
    if not any([vcodecs, acodecs, vencoders, aencoders]):
        raise RuntimeError(
            "ffmpeg returned no codec information. "
            "This may indicate ffmpeg is corrupted or incompatible."
        )

    return CodecData(
        vcodecs=vcodecs,
        acodecs=acodecs,
        scodecs=scodecs,
        vencoders=vencoders,
        aencoders=aencoders,
        sencoders=sencoders,
        vdecoders=vdecoders,
        adecoders=adecoders,
        sdecoders=sdecoders,
    )


def _read_codec_list(param: str, start_line: int) -> tuple[dict, dict, dict]:
    """Read codec list from ffmpeg output.

    Args:
        param: ffmpeg parameter ('-codecs', '-encoders', '-decoders')
        start_line: Line number to start parsing from

    Returns:
        Tuple of (video_codecs, audio_codecs, subtitle_codecs) dictionaries
    """
    video = {}
    audio = {}
    subtitle = {}

    try:
        with spawn_process([LIBRARY_PATH, param]).stdout as output:
            for line in islice(output, start_line, None):
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
