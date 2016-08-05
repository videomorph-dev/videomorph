#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# File name: utils.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg
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

"""This module contains the PRESETS for encoding different video formats."""

from collections import OrderedDict


class BaseProfile(object):
    """Base class for a profile."""

    def __init__(self,
                 profile_name=None,
                 profile_tag=None,
                 profile_extension=None,
                 profile_quality=None,
                 profile_params=None):
        """Class initializer."""
        self.profile_name = profile_name
        self.profile_extension = profile_extension
        self.profile_quality = profile_quality
        self.profile_params = profile_params

    def generate_tag(self):
        tag = ''
        for letter in self.profile_quality:
            if letter.isupper() or letter.isdigit():
                tag += letter
        return '[' + tag + ']'


class MP4Profile(BaseProfile):
    """Base class for the MP4 profile."""

    presets = ['MP4 High Quality',
               'MP4 Very High Quality',
               'MP4 Super High Quality',
               'MP4 Fullscreen',
               'MP4 Widescreen']

    def __init__(self, **kwargs):
        """Class initializer."""
        super(MP4Profile, self).__init__(profile_name='MP4',
                                         profile_extension='.mp4',
                                         **kwargs)


class DVDProfile(BaseProfile):
    """Base class for the DVD profile."""

    presets = ['DVD Fullscreen',
               'DVD Widescreen',
               'DVD Fullscreen High Quality',
               'DVD Widescreen High Quality',
               'DVD Low Quality']

    def __init__(self, **kwargs):
        """Class initializer."""
        super(DVDProfile, self).__init__(profile_name='DVD',
                                         profile_extension='.mpg',
                                         **kwargs)


class VCDProfile(BaseProfile):
    """Base class for the VCD profile."""

    presets = ['VCD High Quality']

    def __init__(self, **kwargs):
        """Class initializer."""
        super(VCDProfile, self).__init__(profile_name='VCD',
                                         profile_extension='.mpg',
                                         **kwargs)


class AVIProfile(BaseProfile):
    """Base class for the AVI profile."""

    presets = ['MS Compatible AVI',
               'XVID Fullscreen',
               'XVID Widescreen']

    def __init__(self, **kwargs):
        """Class initializer."""
        super(AVIProfile, self).__init__(profile_name='AVI',
                                         profile_extension='.avi',
                                         **kwargs)


class FLVProfile(BaseProfile):
    """Base class for the FLV profile."""

    presets = ['FLV Fullscreen',
               'FLV Widescreen']

    def __init__(self, **kwargs):
        """Class initializer."""
        super(FLVProfile, self).__init__(profile_name='FLV',
                                         profile_extension='.flv',
                                         **kwargs)


class WMVProfile(BaseProfile):
    """Base class for the WMV profile."""

    presets = ['WMV Generic']

    def __init__(self, **kwargs):
        """Class initializer."""
        super(WMVProfile, self).__init__(profile_name='WMV',
                                         profile_extension='.wmv',
                                         **kwargs)

# Encoding PROFILES
PROFILES = OrderedDict([('MP4', MP4Profile),
                        ('DVD', DVDProfile),
                        ('VCD', VCDProfile),
                        ('AVI', AVIProfile),
                        ('FLV', FLVProfile),
                        ('WMV', WMVProfile)])
