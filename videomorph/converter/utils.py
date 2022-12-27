# -*- coding: utf-8 -*-
#
# File name: utils.py
#
#   VideoMorph - A PyQt6 frontend to ffmpeg.
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

"""This module contains some utilities and functions."""

import os
from os.path import pathsep
from pathlib import Path
from locale import getdefaultlocale


def get_locale():
    """Return the default locale string."""
    return ('es_ES' if getdefaultlocale()[0] == 'es_CU' else
            getdefaultlocale()[0])
    # return 'es_ES'


def which(app):
    """Detect if an app is installed in your system."""
    if app == '':
        raise ValueError('Invalid app name')

    sys_paths = os.environ.get('PATH', os.defpath).split(pathsep)

    for path in sys_paths:
        app_path = Path(path, app)
        if app_path.exists():
            return app_path.__str__()

    raise ValueError('Command {0} not found'.format(app))


def write_time(time_in_secs):
    """Return time in 00h:00m:00s format."""
    try:
        time = round(float(time_in_secs))
    except (TypeError, ValueError):
        raise ValueError('Invalid time measure.')

    if time < 0:
        raise ValueError('Time must be positive.')

    hours = time // 3600
    minutes = time // 60 - hours * 60
    secs = time - minutes * 60 - hours * 3600

    if hours:  # return the time in 00h:00m:00s format
        return '{hours:02d}h:{minutes:02d}m:{secs:02d}s'.format(
            hours=hours, minutes=minutes, secs=secs)

    if minutes:  # return the time in 00m:00s format
        return '{minutes:02d}m:{secs:02d}s'.format(minutes=minutes,
                                                   secs=secs)

    # return the time in 00s format
    return '{secs:02d}s'.format(secs=secs)


def write_size(size_in_bytes):
    """Return size in appropriate measure."""
    try:
        size = round(float(size_in_bytes))
    except (TypeError, ValueError):
        raise ValueError('Invalid size measure.')

    if size < 0:
        raise ValueError('Size must be positive.')

    kib = size / 1024
    if kib <= 1024:
        return str(round(kib, 1)) + 'KiB'
    mib = kib / 1024
    if mib <= 1024:
        return str(round(mib, 1)) + 'MiB'
    gib = mib / 1024
    return str(round(gib, 1)) + 'GiB'
