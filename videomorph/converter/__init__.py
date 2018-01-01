# -*- coding: utf-8 -*-
#
# File name: __init__.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg and avconv.
#   Copyright 2016-2017 VideoMorph Development Team

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

from sys import platform
from collections import namedtuple
from os import cpu_count
from os.path import dirname
from os.path import exists
from os.path import join as join_path

from .syspath import sys_path_factory
from .syspath import VMPaths
from .utils import get_locale


SYS_PATHS = sys_path_factory()


def get_version():
    """Return app's version number."""
    if exists(join_path(SYS_PATHS.doc, 'VERSION')):
        version_file = join_path(SYS_PATHS.doc, 'VERSION')
    else:
        version_file = '../VERSION'

    with open(version_file, 'r', encoding='UTF-8') as f:
        version = f.readline().strip('\n')

    return version


APP_NAME = 'VideoMorph'
VERSION = get_version()
BASE_DIR = dirname(dirname(dirname(__file__)))
LOCALE = get_locale()
PACKAGE_NAME = APP_NAME.lower()
MAINTAINER = APP_NAME + ' ' + 'Development Team'

ConvLib = namedtuple('ConvLib', 'ffmpeg avconv')
Prober = namedtuple('Prober', 'ffprobe avprobe')

if platform == 'linux':
    CONV_LIB = ConvLib('ffmpeg', 'avconv')
    PROBER = Prober('ffprobe', 'avprobe')
elif platform == 'win32':
    CONV_LIB = ConvLib('ffmpeg.exe', 'avconv.exe')
    PROBER = Prober('ffprobe.exe', 'avprobe.exe')

LIBRARY_ERRORS = ('Unknown encoder', 'Unrecognized option', 'Invalid argument')

LIBRARY_PARAM_REGEX = {'bitrate': r'bitrate=[ ]*[0-9]*\.[0-9]*[a-z]*./[a-z]*',
                       'time': r'time=([0-9.:]+) '}

VIDEO_FILTERS = ('*.mov *.f4v *.webm *.dat *.ogg *.mkv *.wv *.wmv'
                 ' *.flv *.vob *.ts *.3gp *.ogv *.mpg *.mp4 *.avi')

VALID_VIDEO_EXT = {ext.lstrip('*') for ext in VIDEO_FILTERS.split()}

MediaFileStatus = namedtuple('MediaFileStatus', 'todo done stopped')
STATUS = MediaFileStatus('To convert', 'Done!', 'Stopped!')

XMLFiles = namedtuple('XMLFiles', 'default customized')
XML_FILES = XMLFiles('default.xml', 'customized.xml')

CPU_CORES = (cpu_count() - 1 if
             cpu_count() is not None
             else 0)

PLAYERS = ['vlc',
           'xplayer',
           'totem',
           'kmplayer',
           'smplayer',
           'mplayer',
           'banshee',
           'mpv',
           'gxine',
           'xine-ui',
           'gmlive',
           'dragon',
           'ffplay']

VM_PATHS = VMPaths()
