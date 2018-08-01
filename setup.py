#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File _name: setup.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
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

"""This module defines the installation script for VideoMorph."""

from sys import platform

try:
    from setuptools import setup
    USE_DISTUTILS = False
except ImportError:
    from distutils.core import setup
    USE_DISTUTILS = True

from videomorph.converter import VERSION
from videomorph.converter import APP_NAME
from videomorph.converter import VM_PATHS
from videomorph.converter import SYS_PATHS

LONG_DESCRIPTION = """Video Converter based on ffmpeg, Python 3 and PyQt5.
Unlike other video converters, VideoMorph focuses on a single goal:
make video conversion simple, with an easy to use GUI and allowing
the user to convert to the currently most popular video formats.
.
VideoMorph GUI is simple and clean, focused on usability, eliminating
annoying options rarely used.
VideoMorph is a video converter, just that. If you want a video editor,
VideoMorph isn't for you."""

COMMONS = dict(name=APP_NAME.lower(),
               version=VERSION,
               description='Video Converter based on ffmpeg, '
                           'Python 3 and Qt5, focused on usability.',
               long_description=LONG_DESCRIPTION,
               author='Ozkar L. Garcell',
               author_email='ozkar.garcell@gmail.com',
               maintainer='Leodanis Pozo Ramos',
               maintainer_email='lpozor78@gmail.com',
               url='https://github.com/videomorph-dev/videomorph',
               license='Apache License, Version 2.0',
               packages=['videomorph',
                         'videomorph.converter',
                         'videomorph.forms'],
               platforms=['linux', 'win32'],
               keywords='multimedia, video conversion, common video formats')

COMMONS_SETUPTOOLS = dict(
    entry_points={'gui_scripts': ['videomorph = videomorph.main:main']})


LINUX_DATA_FILES = dict(
    data_files=[  # Desktop entry
        (SYS_PATHS.apps,
         [VM_PATHS.apps + '/videomorph.desktop']),
        # App icon
        (SYS_PATHS.icons,
         [VM_PATHS.icons + '/videomorph.png']),
        # App sounds
        (SYS_PATHS.sounds,
         [VM_PATHS.sounds + '/successful.wav']),
        # App translation file
        (SYS_PATHS.i18n,
         [VM_PATHS.i18n + '/videomorph_es.qm']),
        # Default conversion profiles
        (SYS_PATHS.profiles,
         [VM_PATHS.profiles + '/default.xml',
          VM_PATHS.profiles + '/customized.xml']),
        # Documentation files
        (SYS_PATHS.doc,
         ['README.md', 'LICENSE', 'AUTHORS', 'INSTALL', 'VERSION',
          'copyright', 'changelog.gz', 'TODO', 'screenshot.png']),
        # User's manual
        (SYS_PATHS.help,
         [VM_PATHS.help + '/manual_es.pdf',
          VM_PATHS.help + '/manual_en.pdf']),
        # Man page
        (SYS_PATHS.man,
         [VM_PATHS.man + '/videomorph.1.gz'])])

LINUX_DISTUTILS = dict(scripts=[VM_PATHS.bin + '/videomorph'])


WIN32_DATA_FILES = dict(
    data_files=[  # App icon
        (SYS_PATHS.icons,
         [VM_PATHS.icons + '/videomorph.ico']),
        # App sounds
        (SYS_PATHS.sounds,
         [VM_PATHS.sounds + '/successful.wav']),
        # App translation file
        (SYS_PATHS.i18n,
         [VM_PATHS.i18n + '/videomorph_es.qm']),
        # Default conversion profiles
        (SYS_PATHS.profiles,
         [VM_PATHS.profiles + '/default.xml',
          VM_PATHS.profiles + '/customized.xml']),
        # Documentation files
        (SYS_PATHS.doc,
         ['README.md', 'LICENSE', 'AUTHORS', 'INSTALL', 'VERSION',
          'copyright', 'changelog.gz', 'TODO', 'screenshot.png']),
        # User's manual
        (SYS_PATHS.help,
         [VM_PATHS.help + '/manual_es.pdf',
          VM_PATHS.help + '/manual_en.pdf'])])


SETUP_PARAMS = COMMONS

if platform == 'linux':
    SETUP_PARAMS.update(LINUX_DATA_FILES)
    if USE_DISTUTILS:
        SETUP_PARAMS.update(LINUX_DISTUTILS)
    else:
        SETUP_PARAMS.update(COMMONS_SETUPTOOLS)
elif platform == 'win32':
    SETUP_PARAMS.update(WIN32_DATA_FILES)
    if not USE_DISTUTILS:
        SETUP_PARAMS.update(COMMONS_SETUPTOOLS)


if __name__ == '__main__':
    setup(**SETUP_PARAMS)
