"""This module provides tests for vmpath.py module."""

import os
from pathlib import Path
from sys import prefix

from videomorph.converter.vmpath import darwin_paths, linux_paths, win32_paths


class TestPaths:
    """Class for testing vmpath.py module."""

    def setup_method(self):
        """Setup method for each test."""
        self.posix_path = dict(
            apps=Path(prefix, "share", "applications"),
            config=Path(Path.home(), ".videomorph"),
            icons=Path(prefix, "share", "icons"),
            i18n=Path(prefix, "share", "videomorph", "translations"),
            profiles=Path(prefix, "share", "videomorph", "profiles"),
            sounds=Path(prefix, "share", "videomorph", "sounds"),
            doc=Path(prefix, "share", "doc", "videomorph"),
            help=Path(prefix, "share", "doc", "videomorph", "manual"),
            man=Path(prefix, "share", "man", "man1"),
            bin=Path(prefix, "bin"),
        )

        program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        self.win32_paths = dict(
            apps=Path(program_files, "VideoMorph"),
            config=Path(Path.home(), ".videomorph"),
            icons=Path(program_files, "VideoMorph", "icons"),
            i18n=Path(program_files, "VideoMorph", "translations"),
            profiles=Path(program_files, "VideoMorph", "profiles"),
            sounds=Path(program_files, "VideoMorph", "sounds"),
            doc=Path(program_files, "VideoMorph", "doc"),
            help=Path(program_files, "VideoMorph", "manual"),
            man=Path(program_files, "VideoMorph", "man1"),
            bin=Path(program_files, "VideoMorph", "bin"),
        )

    def test_linux_paths(self):
        """Test linux_path()."""
        assert self.posix_path == linux_paths()

    def test_darwin_paths(self):
        """Test darwin_paths()."""
        assert self.posix_path == darwin_paths()

    def test_win32_paths(self):
        """Test win32_paths()."""
        assert self.win32_paths == win32_paths()
