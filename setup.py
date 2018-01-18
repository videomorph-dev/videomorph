#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File _name: setup.py
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

"""This module defines the installation script for VideoMorph."""

from distutils.core import setup

from videomorph.converter import VERSION
from videomorph.converter import APP_NAME
from videomorph.converter import VM_PATHS
from videomorph.converter import SYS_PATHS


LONG_DESCRIPTION = """Small Video Converter based on ffmpeg, Python 3 and Qt5.
Unlike other video converters, VideoMorph focuses on a single goal:
make video conversion simple, with an easy to use GUI and allowing
the user to convert to the currently most popular video formats.
.
VideoMorph GUI is simple and clean, focused on usability, eliminating
annoying options rarely used.
VideoMorph is a video converter, just that. If you want a video editor,
VideoMorph isn't for you."""


if __name__ == '__main__':
    setup(name=APP_NAME.lower(),
          version=VERSION,
          description='Small Video Converter based on ffmpeg, '
                      'Python 3 and Qt5, focused on usability.',
          long_description=LONG_DESCRIPTION,

          author='Ozkar L. Garcell',
          author_email='ozkar.garcell@gmail.com',
          maintainer='Leodanis Pozo Ramos',
          maintainer_email='lpozor78@gmail.com',
          url='https://github.com/codeshard/videomorph',
          license='Apache License, Version 2.0',
          packages=['videomorph', 'videomorph.converter', 'videomorph.forms'],
          platforms=['linux', 'win32'],
          keywords='multimedia, video conversion, common video formats',

          data_files=[
              # Desktop entry
              (SYS_PATHS.apps,
               [VM_PATHS.apps + '/videomorph.desktop']),
              # App icon
              (SYS_PATHS.icons,
               [VM_PATHS.icons + '/videomorph.png']),
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
              # Man page
              (SYS_PATHS.man,
               [VM_PATHS.man + '/videomorph.1.gz'])
          ],

          scripts=[VM_PATHS.bin + '/videomorph'])
