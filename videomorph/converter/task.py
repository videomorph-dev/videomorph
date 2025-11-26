"""This module provides Conversion Task Class."""

import shlex
import time
from os import W_OK, access
from pathlib import Path
from typing import List, Optional, Union

from videomorph.converter import CPU_CORES, STATUS
from videomorph.converter.profile import Profile
from videomorph.converter.video import Video

_DELETE_RETRY_ATTEMPTS = 3
_DELETE_RETRY_DELAY = 0.2  # seconds


class OutputPathCollisionError(Exception):
    """Raised when input and output paths refer to the same file without replacement."""


class Task:
    """Class to represent a conversion task."""

    def __init__(
        self, video: Video, profile: Profile, output_dir: Union[str, Path]
    ) -> None:
        self.video = video
        self.profile = profile
        self.output_dir = Path(output_dir)
        self.status = STATUS.todo
        self._active_output_path: Optional[Path] = None
        self._final_output_path: Optional[Path] = None
        self._temp_output_path: Optional[Path] = None
        self._skip_video_delete: bool = False

    def build_conversion_cmd(
        self,
        target_quality: str,
        tagged: bool,
        subtitle: bool,
        replace_source: bool = False,
    ) -> List[str]:
        """Return the conversion command."""
        if not access(self.output_dir, W_OK):
            raise PermissionError("Access denied")

        if not self.video.path.exists():
            raise FileNotFoundError("Input video not found")

        # Ensure the conversion_profile is up to date
        self.profile.update(new_quality=target_quality)

        # Process subtitles if available
        subtitle_opt = self._process_subtitles(subtitle)

        # Get the output path
        desired_output = self._get_output_path(tagged)
        self._final_output_path = desired_output
        self._temp_output_path = None
        self._active_output_path = desired_output
        self._skip_video_delete = False

        if self._paths_conflict_with_input(desired_output):
            if replace_source:
                self._temp_output_path = self._build_temp_output_path(desired_output)
                self._active_output_path = self._temp_output_path
                self._skip_video_delete = True
            else:
                raise OutputPathCollisionError(desired_output.__str__())

        # Build the conversion command
        params = self.profile.params or ""
        cmd = (
            ["-i", self.video.path.__str__()]
            + subtitle_opt
            + shlex.split(params)
            + ["-threads", str(CPU_CORES)]
            + ["-y", self._active_output_path.__str__()]
        )

        return cmd

    def finalize_output(self) -> None:
        """Finalize output file when temporary output was used."""
        if self._temp_output_path is None:
            return

        if not self._temp_output_path.exists():
            raise FileNotFoundError(
                f"Temporary output {self._temp_output_path} is missing."
            )

        self._temp_output_path.replace(self._final_output_path)
        self._active_output_path = self._final_output_path
        self._temp_output_path = None

    def delete_output(self, tagged: bool) -> bool:
        """Delete the output file if conversion is stopped.

        Returns:
            True if file was deleted or didn't exist, False if deletion failed.
        """
        output_path = (
            self._active_output_path
            if self._active_output_path is not None
            else self._get_output_path(tagged)
        )

        for attempt in range(_DELETE_RETRY_ATTEMPTS):
            try:
                output_path.unlink()
                return True
            except FileNotFoundError:
                return True  # File doesn't exist, consider it "deleted"
            except PermissionError:
                if attempt + 1 == _DELETE_RETRY_ATTEMPTS:
                    # File is locked/in use - failed after all retries
                    return False
                time.sleep(_DELETE_RETRY_DELAY)

        return False  # Should never reach here, but safety fallback

    def delete_input(self) -> None:
        """Delete the input file (and subtitle) when conversion is finished."""
        if not self._skip_video_delete:
            try:
                self.video.path.unlink()
            except FileNotFoundError:
                pass

        try:
            self.subtitle_path.unlink()
        except FileNotFoundError:
            pass

    def get_output_file_name(self, tagged: bool) -> str:
        """Return the name of the output video file."""
        output_file = (
            self._final_output_path
            if self._final_output_path is not None
            else self._get_output_path(tagged)
        )
        return output_file.name

    def get_output_path(self, tagged: bool) -> str:
        """Return the the output file path as str."""
        path = (
            self._final_output_path
            if self._final_output_path is not None
            else self._get_output_path(tagged)
        )
        return str(path)

    def _get_output_path(self, tagged: bool) -> Path:
        """Return the the output file path as pathlib.Path."""
        tag = self.profile.quality_tag if tagged else ""
        extension = self.profile.extension or ".mp4"
        output_file_name = "".join((tag, self.video.get_name(False), extension))
        return Path(self.output_dir, output_file_name)

    def _paths_conflict_with_input(self, desired_output: Path) -> bool:
        """Return True when desired output refers to the same file as the input."""
        input_path = self.video.path
        try:
            return input_path.samefile(desired_output)
        except FileNotFoundError:
            # If either path doesn't exist yet, fall back to normalized comparison
            return (
                input_path.resolve().as_posix().casefold()
                == desired_output.resolve().as_posix().casefold()
            )

    def _build_temp_output_path(self, desired_output: Path) -> Path:
        """Create a unique temporary output path next to the final file."""
        base_name = desired_output.name
        candidate = desired_output.with_name(f".tmp_videomorph_{base_name}")
        counter = 1

        while candidate.exists():
            candidate = desired_output.with_name(
                f".tmp_videomorph_{counter}_{base_name}"
            )
            counter += 1

        return candidate

    @property
    def subtitle_path(self) -> Path:
        """Return the subtitle path as pathlib.Path if it exits."""
        extensions = [".srt", ".ssa", ".stl"]

        # Add uppercase extensions to check if subtitle file exists
        for ext in extensions[:]:
            extensions.append(ext.upper())

        for ext in extensions:
            subtitle_path = self.video.path.with_suffix(ext)
            if subtitle_path.exists():
                return subtitle_path

        raise FileNotFoundError("Subtitle file not found")

    def _process_subtitles(self, subtitle: bool) -> List[str]:
        """Process subtitles if available."""
        if subtitle:
            try:
                subtitle_opt = [
                    "-vf",
                    "subtitles='{0}':force_style='Fontsize=24'"
                    ":charenc=cp1252".format(self.subtitle_path.__str__()),
                ]
                return subtitle_opt
            except FileNotFoundError:
                pass

        return []
