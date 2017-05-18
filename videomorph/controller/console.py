#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: console.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg and avconv.
#   Copyright 2015-2016 VideoMorph Development Team

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
from os.path import exists
from os.path import isdir
from os.path import sep

from videomorph import APPNAME
from videomorph import VERSION
from videomorph import VIDEO_FILTERS


def run_on_console(app, main_win):
    """Provides option to run VideoMorph from the command line."""

    # Add a parser for command line
    parser = argparse.ArgumentParser(description=APPNAME + ' ' + VERSION)

    # Add options for command line
    parser.add_argument('-i', '--input_file',
                        help='take the path to a video file(s) as input',
                        action='store',
                        nargs='*',
                        dest='input_file')

    parser.add_argument('-d', '--input_dir',
                        help='take a directory as input and find video '
                             'files recursively',
                        action='store',
                        dest='input_dir')

    # Process the command line input
    args = parser.parse_args()

    files = []

    if args.input_file:
        for file in args.input_file:
            if exists(file):
                files.append(file)
            else:
                print("Video File: {0}, doesn't exit".format(file),
                      file=sys.stderr)

    if args.input_dir:
        if isdir(args.input_dir):
            for dir_path, _, file_names in walk(args.input_dir):
                for file in file_names:
                    if file.split('.')[-1] in VIDEO_FILTERS:
                        files.append('{0}'.join([dir_path, file]).format(sep))
        else:
            print("Directory: {0}, doesn't exist".format(args.input_dir),
                  file=sys.stderr)

    if files:
        main_win.add_media_files(*files)
        main_win.show()
        sys.exit(app.exec_())
