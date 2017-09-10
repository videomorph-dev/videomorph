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

from collections import namedtuple
from os import cpu_count
from os.path import expanduser
from os.path import dirname
from os.path import join as join_path

from .utils import get_locale

APP_NAME = 'VideoMorph'
VERSION = '1.1'
CODENAME = 'adventurer'
BASE_DIR = dirname(dirname(dirname(__file__)))
LOCALE = get_locale()
PACKAGE_NAME = APP_NAME.lower()
MAINTAINER = APP_NAME + ' ' + 'Development Team'

ConvLib = namedtuple('ConvLib', 'ffmpeg avconv')
CONV_LIB = ConvLib('ffmpeg', 'avconv')

LIBRARY_ERRORS = ('Unknown encoder', 'Unrecognized option', 'Invalid argument')

LIBRARY_PARAM_REGEX = {'bitrate': r'bitrate=[ ]*[0-9]*\.[0-9]*[a-z]*./[a-z]*',
                       'time': r'time=([0-9.:]+) '}

VIDEO_FILTERS = ('*.mov *.f4v *.webm *.dat *.ogg *.mkv *.wv *.wmv'
                 ' *.flv *.vob *.ts *.3gp *.ogv *.mpg *.mp4 *.avi')

VALID_VIDEO_EXT = {ext.lstrip('*') for ext in VIDEO_FILTERS.split()}

Prober = namedtuple('Prober', 'ffprobe avprobe')
PROBER = Prober('ffprobe', 'avprobe')

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

VM_PATHS = {'apps': 'share/applications',
            'icons': 'share/icons',
            'i18n': 'share/videomorph/translations',
            'profiles': 'share/videomorph/profiles',
            'doc': 'share/doc/videomorph',
            'man': 'share/man',
            'bin': 'bin'}

LINUX_PATHS = {'apps': '/usr/share/applications',
               'config': join_path(expanduser('~'), '.videomorph'),
               'icons': '/usr/share/icons',
               'i18n': '/usr/share/videomorph/translations',
               'profiles': '/usr/share/videomorph/profiles',
               'doc': '/usr/share/doc/videomorph',
               'man': '/usr/share/man/man1'}
