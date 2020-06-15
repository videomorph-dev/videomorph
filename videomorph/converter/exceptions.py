# -*- coding: utf-8 -*-

# File name: exceptions.py
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

"""This module provides Exceptions."""


class MediaError(Exception):
    """General exception class."""
    pass


class InvalidMetadataError(MediaError):
    """Exception to raise when the file don't have a valid metadata info."""
    pass


class InvalidVideoError(MediaError):
    pass


class ProfileError(Exception):
    """Base Exception."""
    pass


class ProfileBlankNameError(ProfileError):
    """Exception for Profile Blank Name."""
    pass


class ProfileBlankPresetError(ProfileError):
    """Exception form Profile Blank Preset."""
    pass


class ProfileBlankParamsError(ProfileError):
    """Exception form Profile Blank Params."""
    pass


class ProfileExtensionError(ProfileError):
    """Exception form Profile Extension Error."""
    pass


class PlayerNotFoundError(Exception):
    """Exception to handle Player not found error."""
    pass


class ProfileParamsError(ProfileError):
    """Exception form Profile wrong params."""
    pass
