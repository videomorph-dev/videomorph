#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_vmpath.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
#   Copyright 2016-2020 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""This module provides tests for vmpath.py module."""

from os.path import expandvars
from pathlib import Path
from sys import prefix

from videomorph.converter.vmpath import darwin_paths, linux_paths, win32_paths


class TestPaths:
    """Class for testing vmpath.py module."""

    def setup(self):
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

        program_files = expandvars("%ProgramFiles%")
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
        print(self.win32_paths)
        print(win32_paths())
        assert self.win32_paths == win32_paths()
