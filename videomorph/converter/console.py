# -*- coding: utf-8 -*-

# File name: console.py
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

"""This module defines the VideoMorph terminal options."""

import argparse
import sys
from os import walk
from os.path import isdir
from pathlib import Path

from . import APP_NAME, VALID_VIDEO_EXT, VERSION


def run_on_console(app, main_win):
    """Provide options to run VideoMorph from the command line."""

    # Add a parser for command line
    parser = argparse.ArgumentParser(description=APP_NAME + " " + VERSION)

    # Add options for command line
    parser.add_argument(
        "-i",
        "--input-file",
        help="take the input_path to a video file(s) as input",
        action="store",
        nargs="*",
        dest="input_file",
    )

    parser.add_argument(
        "-d",
        "--input-dir",
        help="take a directory as input and find video " "files recursively",
        action="store",
        dest="input_dir",
    )

    # Process the command line input
    args = parser.parse_args()

    files = []

    if args.input_file:
        for file in args.input_file:
            path = Path(file)
            if path.exists():
                files.append(path.__str__())
            else:
                print(
                    "Video file: {0}, doesn't exit".format(file),
                    file=sys.stderr,
                )

    if args.input_dir:
        try:
            files = search_directory_recursively(
                directory=args.input_dir, files=files
            )
        except IsADirectoryError as error:
            print(error, file=sys.stderr)
        except FileNotFoundError as error:
            print(error, file=sys.stderr)

    if files:
        # Avoid duplicated files
        files_to_add = set(files)
        # Add files
        main_win.add_tasks(*files_to_add)
        main_win.show()
        main_win.start_encoding()
        sys.exit(app.exec_())


def search_directory_recursively(directory, files=None):
    """Search a directory for video files."""
    if files is None:
        files = []

    if isdir(directory):
        for dir_path, _, files_names in walk(directory):
            for file_name in files_names:
                path = Path(dir_path, file_name)
                if path.suffix.lower() in VALID_VIDEO_EXT:
                    files.append(path.__str__())
    else:
        raise IsADirectoryError(
            "Directory: {0}, doesn't exist".format(directory)
        )

    if not files:
        raise FileNotFoundError(
            "No Video Files Found in: {0}".format(directory)
        )

    return files
