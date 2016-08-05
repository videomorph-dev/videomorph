#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File name: utils.py
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

"""This module contains some utilities and functions."""

import os


class ConversionLib:
    ffmpeg = 'ffmpeg'
    avconv = 'avconv'


CONV_LIB = ConversionLib()


CPU_CORES = (os.cpu_count() - 1 if
             os.cpu_count() is not None
             else 0)


def which(app):
    """Detect if an app is installed in your system."""
    path = os.environ.get('PATH', os.defpath)
    for directory in path.split(':'):
        app_path = os.path.join(directory, app)
        if os.path.exists(app_path) and os.access(app_path, os.X_OK):
            return app_path
    return None


def write_time(_time):
    """Return time in 00h:00m:00s format."""

    def fix(string):
        """Fix a number so it always contain two characters."""
        string = str(string)
        if len(string) == 1:
            return '0' + string
        else:
            return string

    time = int(round(float(_time)))
    hours = int(time / 3600)
    minutes = int(time / 60) - hours * 60
    secs = time - minutes * 60 - hours * 3600

    if hours:  # @return the time in 00h:00m:00s format
        return ':'.join(['{0}h'.format(fix(hours)),
                         '{0}m'.format(fix(minutes)),
                         '{0}s'.format(fix(secs))])
    elif minutes:  # @return the time in 00m:00s format
        return ':'.join(['{0}m'.format(fix(minutes)),
                         '{0}s'.format(fix(secs))])
    else:  # @return the time in 0s format
        return str(secs) + 's'
