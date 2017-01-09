#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File name: profiles.py
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

"""This module contains the PRESETS for encoding different video formats."""

from os import sep
from os.path import expanduser, join, exists
from re import compile
from collections import OrderedDict
from distutils.file_util import copy_file
from xml.etree import ElementTree

from .utils import get_locale


def _get_profiles_xml_path():
    return join(expanduser("~"), '.videomorph{0}profiles.xml'.format(sep))


def _create_profiles_xml_file():
    profiles_xml = _get_profiles_xml_path()

    if not exists(profiles_xml):
        # TODO: This must get the file from '/usr/share/videomorph/stdprofiles'
        copy_file('../videomorph/stdprofiles/profiles.xml', profiles_xml)
        # copy_file('/usr/share/videomorph/stdprofiles/profiles.xml',
        #           profiles_xml)


def _parse_profiles_xml():
    """Returns the profiles.xml root."""
    tree = ElementTree.parse(_get_profiles_xml_path())
    return tree.getroot()


def _get_profiles():
    """Return a dict of Profile objects."""
    profiles = OrderedDict()
    root = _parse_profiles_xml()
    for elem in root:
        profiles[elem.tag] = Profile(extension=elem[0][2].text)

    return profiles


def _get_preset_params(locale):
    preset_params = OrderedDict()
    root = _parse_profiles_xml()
    for elem in root:
        for e in elem:
            if locale == 'es_ES':
                preset_params[e[3].text] = e[1].text
            else:
                preset_params[e[0].text] = e[1].text

    return preset_params


def _get_qualities_per_profile(locale):
    qualities_per_profile = OrderedDict()
    values_list = []
    root = _parse_profiles_xml()
    for elem in root:
        for e in elem:
            if locale == 'es_ES':
                values_list.append(e[3].text)
            else:
                values_list.append(e[0].text)

        qualities_per_profile[elem.tag] = values_list
        values_list = []
    return qualities_per_profile


class Profile:
    """Base class for a Video Profile."""

    def __init__(self,
                 extension=None,
                 quality=None,
                 params=None):
        """Class initializer."""
        self.extension = extension
        self.quality = quality
        self.params = params

    @property
    def quality_tag(self):
        """Generate a tag from profile quality string."""
        tag_regex = compile(r'[A-Z]4?')
        tag = ''.join(tag_regex.findall(self.quality))

        return '[' + tag + ']'


_create_profiles_xml_file()

PRESETS_PARAMS = _get_preset_params(get_locale())

PROFILES = _get_profiles()

QUALITIES_PER_PROFILE = _get_qualities_per_profile(get_locale())
