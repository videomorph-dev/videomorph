"""This module provides tests for vmpath.py module."""

import os
from pathlib import Path
from sys import platform, prefix
from unittest.mock import patch

from videomorph.converter.paths import _PlatformPaths


class TestPaths:
    """Class for testing vmpath.py module."""

    def setup_method(self):
        """Setup method for each test."""
        self.posix_path = {
            "apps": Path(prefix, "share", "applications"),
            "config": Path(Path.home(), ".videomorph"),
            "icons": Path(prefix, "share", "icons"),
            "i18n": Path(prefix, "share", "videomorph", "translations"),
            "profiles": Path(prefix, "share", "videomorph", "profiles"),
            "sounds": Path(prefix, "share", "videomorph", "sounds"),
            "doc": Path(prefix, "share", "doc", "videomorph"),
            "help": Path(prefix, "share", "doc", "videomorph", "manual"),
            "man": Path(prefix, "share", "man", "man1"),
            "bin": Path(prefix, "bin"),
        }

        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        self.win32_paths = {
            "apps": Path(program_files, "VideoMorph"),
            "config": Path(Path.home(), ".videomorph"),
            "icons": Path(program_files, "VideoMorph", "icons"),
            "i18n": Path(program_files, "VideoMorph", "translations"),
            "profiles": Path(program_files, "VideoMorph", "profiles"),
            "sounds": Path(program_files, "VideoMorph", "sounds"),
            "doc": Path(program_files, "VideoMorph", "videomorph"),
            "help": Path(program_files, "VideoMorph", "videomorph", "manual"),
            "man": Path(program_files, "VideoMorph", "man1"),
            "bin": Path(program_files, "VideoMorph", "bin"),
        }

    def test_linux_paths(self):
        """Test Linux platform paths."""
        with patch("videomorph.converter.paths.platform", "linux"):
            paths = _PlatformPaths.for_current_platform()
            for key, expected in self.posix_path.items():
                assert getattr(paths, key) == expected

    def test_darwin_paths(self):
        """Test macOS platform paths."""
        with patch("videomorph.converter.paths.platform", "darwin"):
            paths = _PlatformPaths.for_current_platform()
            for key, expected in self.posix_path.items():
                assert getattr(paths, key) == expected

    def test_win32_paths(self):
        """Test Windows platform paths."""
        with patch("videomorph.converter.paths.platform", "win32"):
            paths = _PlatformPaths.for_current_platform()
            for key, expected in self.win32_paths.items():
                assert getattr(paths, key) == expected
