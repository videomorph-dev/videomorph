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

from sys import platform

try:
    from setuptools import setup
    use_distutils = False
except ImportError:
    from distutils.core import setup
    use_distutils = True

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

commons = dict(name=APP_NAME.lower(),
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

commons_setuptools = dict(
    entry_points={'gui_scripts': ['videomorph = videomorph.main:main']})


linux_data_files = dict(
    data_files=[  # Desktop entry
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
         [VM_PATHS.man + '/videomorph.1.gz'])])

linux_distutils = dict(scripts=[VM_PATHS.bin + '/videomorph'])


win32_data_files = dict(
    data_files=[  # App icon
        (SYS_PATHS.icons,
         [VM_PATHS.icons + '/videomorph.ico']),
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
          'copyright', 'changelog.gz', 'TODO', 'screenshot.png'])])


setup_params = commons

if platform == 'linux':
    setup_params.update(linux_data_files)
    if use_distutils:
        setup_params.update(linux_distutils)
    else:
        setup_params.update(commons_setuptools)
elif platform == 'win32':
    setup_params.update(win32_data_files)
    if not use_distutils:
        setup_params.update(commons_setuptools)


if __name__ == '__main__':
    setup(**setup_params)

    # if platform == 'win32':
    #     import os
    #     from sys import prefix
    #     from os.path import exists
    #     from os.path import expandvars
    #     from os.path import join as join_path
    #
    #     exe_path = join_path(prefix, 'Scripts', APP_NAME.lower() + '.exe')
    #     if exists(exe_path):
    #         os.link(source=exe_path, link_name=APP_NAME + VERSION)
