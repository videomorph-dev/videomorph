# -*- coding: utf-8 -*-
#
# File name: __init__.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
#   Copyright 2016-2018 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""This module defines the converter package."""

from collections import namedtuple
try:
    from os import cpu_count
except ImportError:
    cpu_count = None
from os.path import join as join_path

from .platformdeps import sys_path_factory
from .platformdeps import VMPaths
from .vmpath import BASE_DIR
from .utils import get_locale


SYS_PATHS = sys_path_factory()


def get_version():
    """Return app's version number."""
    try:
        version_file = open(join_path(SYS_PATHS.doc, 'VERSION'),
                            'r', encoding='UTF-8')
    except FileNotFoundError:
        version_file = open(join_path(BASE_DIR, 'VERSION'),
                            'r', encoding='UTF-8')

    with version_file:
        version = version_file.readline().strip('\n')

    return version


APP_NAME = 'VideoMorph'
VERSION = get_version()
LOCALE = get_locale()

VIDEO_FILTERS = ('*.mov *.f4v *.webm *.dat *.ogg *.mkv *.wv *.wmv'
                 ' *.flv *.vob *.ts *.mts *.3gp *.ogv *.mpg *.mp4 *.avi')

VALID_VIDEO_EXT = {ext.lstrip('*') for ext in VIDEO_FILTERS.split()}

MediaFileStatus = namedtuple('MediaFileStatus', 'todo done stopped')
STATUS = MediaFileStatus('Todo', 'Done', 'Stopped')

XMLFiles = namedtuple('XMLFiles', 'default customized')
XML_FILES = XMLFiles('default.xml', 'customized.xml')

CPU_CORES = (cpu_count() - 1 if
             cpu_count() is not None
             else 0)

VM_PATHS = VMPaths()
