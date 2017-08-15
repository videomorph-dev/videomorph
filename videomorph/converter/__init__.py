# -*- coding: utf-8 -*-
#
# File _name: __init__.py
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

"""This module defines the _converter package and the needed imports."""

from .conversionlib import ConversionLib
from .console import run_on_console
from .console import search_directory_recursively
from .media import MediaList
from .utils import get_locale
from .utils import which
from .utils import write_time
from .profile import ConversionProfile
from .profile import (ProfileBlankNameError,
                      ProfileBlankPresetError,
                      ProfileBlankParamsError,
                      ProfileExtensionError)
