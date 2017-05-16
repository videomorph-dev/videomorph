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

import re
from os import sep
from os.path import expanduser, join, exists
from collections import OrderedDict
from distutils.file_util import copy_file
from distutils.errors import DistutilsFileError
from xml.etree import ElementTree

from videomorph import LINUX_PATHS
from videomorph import VM_PATHS
from videomorph import CONV_LIB
from videomorph import PROBER


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


class XMLProfile:
    """Class to manage the profiles.xml file."""

    def __init__(self):
        self._xml_root = None

    def set_xml_root(self):
        """Set the XML root."""
        self._xml_root = self._get_xml_root()

    def add_conversion_profile(self, profile_name, preset, params, extension):
        """Add a conversion profile."""
        if not profile_name:
            raise ProfileBlankNameError

        profile_name = profile_name.upper()

        if not preset:
            raise ProfileBlankPresetError

        if not params:
            raise ProfileBlankParamsError

        if not extension.startswith('.'):
            raise ProfileExtensionError

        extension = extension.lower()

        xml_profile = ElementTree.Element(profile_name)
        regexp = re.compile(r'[A-z][0-9]?')
        preset_tag = ''.join(regexp.findall(preset))
        xml_preset = ElementTree.Element(preset_tag)
        xml_preset_name = ElementTree.Element('preset_name')
        xml_preset_name.text = preset
        xml_params = ElementTree.Element('preset_params')
        xml_params.text = params
        xml_extension = ElementTree.Element('file_extension')
        xml_extension.text = extension
        xml_preset_name_es = ElementTree.Element('preset_name_es')
        xml_preset_name_es.text = preset

        for i, elem in enumerate([xml_preset_name, xml_params,
                                  xml_extension, xml_preset_name_es]):
            xml_preset.insert(i, elem)

        for i, elem in enumerate(self._xml_root[:]):
            if elem.tag == xml_profile.tag:
                self._xml_root[i].insert(0, xml_preset)
                self.save_tree()
                break
            else:
                xml_profile.insert(0, xml_preset)
                self._xml_root.insert(0, xml_profile)
                self.save_tree()
                break

    def export_profile_xml_file(self, dst_dir):
        """Export a file with the conversion profiles."""
        # Raise PermissionError if user don't have write permission
        try:
            copy_file(src=self.profiles_xml_path, dst=dst_dir)
        except DistutilsFileError:
            raise PermissionError

    def import_profile_xml(self, src_file):
        """Import a conversion profile file."""
        try:
            copy_file(src=src_file, dst=self.profiles_xml_path)
        except DistutilsFileError:
            raise PermissionError

    def get_conversion_profile(self, profile_name,
                               target_quality,
                               conv_lib=CONV_LIB.ffmpeg):
        """Return a Profile objects."""
        for element in self._xml_root:
            if element.tag == profile_name:
                for item in element:
                    if (item[0].text == target_quality or
                            item[3].text == target_quality):
                        return _Profile(conv_lib=conv_lib,
                                        quality=target_quality,
                                        extension=item[2].text,
                                        xml_profile=self)

    def get_preset_attr(self, target_quality, attr_index=1):
        """Return a dict of preset/params."""
        for element in self._xml_root:
            for item in element:
                if (item[0].text == target_quality or
                        item[3].text == target_quality):
                    return item[attr_index].text

    def get_qualities_per_profile(self, locale):
        """Return a list of available Qualities per conversion profile."""
        qualities_per_profile = OrderedDict()
        values = []

        for element in self._xml_root:
            for item in element:
                if locale == 'es_ES':
                    # Create the dict with values in spanish
                    values.append(item[3].text)
                else:
                    # Create the dict with values in english
                    values.append(item[0].text)

            qualities_per_profile[element.tag] = values
            # Reinitialize values
            values = []

        return qualities_per_profile

    def save_tree(self):
        """Save xml tree."""
        with open(self.profiles_xml_path, 'wb') as _file:
            ElementTree.ElementTree(self._xml_root).write(_file)

    @property
    def profiles_xml_path(self):
        """Return the path to the profiles file."""
        return join(expanduser("~"), '.videomorph{0}profiles.xml'.format(sep))

    def create_profiles_xml_file(self):
        """Create a xml file with the conversion profiles."""
        profiles_xml = self.profiles_xml_path

        if not exists(profiles_xml):
            if exists(LINUX_PATHS['profiles'] + '/profiles.xml'):
                # if VideoMorph is installed
                copy_file(LINUX_PATHS['profiles'] + '/profiles.xml',
                          profiles_xml)
            else:
                # if not installed
                copy_file('../' + VM_PATHS['profiles'] + '/profiles.xml',
                          profiles_xml)

    def _get_xml_root(self):
        """Returns the profiles.xml root."""
        tree = ElementTree.parse(self.profiles_xml_path)
        return tree.getroot()


class _Profile:
    """Base class for a Video Profile."""

    def __init__(self, conv_lib=CONV_LIB.ffmpeg,
                 quality=None, extension=None, xml_profile=None):
        """Class initializer."""
        self.xml_profile = xml_profile
        self.params = None
        self._quality = None
        self.conv_lib = conv_lib
        # Set self.quality and also self.params
        self.quality = quality
        self.extension = extension
        if self.conv_lib == CONV_LIB.ffmpeg:
            self.prober = PROBER.ffprobe
        else:
            self.prober = PROBER.avprobe

    @property
    def quality(self):
        """Return the target Quality."""
        return self._quality

    @quality.setter
    def quality(self, value):
        """Set the target Quality and other parameters needed to get it."""
        self._quality = value
        # Update the params and extension when the target quality change
        self.params = self.xml_profile.get_preset_attr(self._quality)
        self.extension = self.xml_profile.get_preset_attr(self._quality,
                                                          attr_index=2)

    @property
    def quality_tag(self):
        """Generate a tag from profile quality string."""
        tag_regex = re.compile(r'[A-Z][0-9]?')
        tag = ''.join(tag_regex.findall(self.quality))

        return '[' + tag + ']'
