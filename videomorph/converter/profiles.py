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
from os.path import expanduser, join, exists, isdir
from re import compile
from collections import OrderedDict
from distutils.file_util import copy_file
from distutils.errors import DistutilsFileError
from xml.etree import ElementTree


class ProfileError(Exception):
    pass


class ProfileNameBlankError(ProfileError):
    pass


class ProfilePresetBlankError(ProfileError):
    pass


class ProfileParamsBlankError(ProfileError):
    pass


class ProfileExtensionError(ProfileError):
    pass


class _XMLProfile:
    """Class to manage the profiles.xml file."""

    def __init__(self):
        self._xml_root = None

    def set_xml_root(self):
        self._xml_root = self._get_xml_root()

    # TODO: delete_conversion_profile and exit_conversion_profile methods
    def add_conversion_profile(self, profile_name, preset, params, extension):

        if not profile_name:
            raise ProfileNameBlankError

        profile_name = profile_name.upper()

        if not preset:
            raise ProfilePresetBlankError

        if not params:
            raise ProfileParamsBlankError

        if not extension.startswith('.'):
            raise ProfileExtensionError

        extension = extension.lower()

        xml_profile = ElementTree.Element(profile_name)
        rx = compile(r'[A-z][0-9]?')
        preset_tag = ''.join(rx.findall(preset))
        xml_preset = ElementTree.Element(preset_tag)
        xml_preset_name = ElementTree.Element('preset_name')
        xml_preset_name.text = preset
        xml_params = ElementTree.Element('preset_params')
        xml_params.text = params
        xml_extension = ElementTree.Element('file_extension')
        xml_extension.text = extension
        xml_preset_name_es = ElementTree.Element('preset_name_es')
        xml_preset_name_es.text = preset

        for num, elem in enumerate([xml_preset_name, xml_params,
                                    xml_extension, xml_preset_name_es]):
            xml_preset.insert(num, elem)

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
        if isdir(dst_dir):
            # Raise PermissionError if user don't have write permission
            try:
                copy_file(src=self._profiles_xml_path, dst=dst_dir)
            except DistutilsFileError:
                raise PermissionError

    def get_conversion_profile(self, profile_name, target_quality):
        """Return a Profile objects."""
        for elem in self._xml_root:
            if elem.tag == profile_name:
                for e in elem:
                    if (e[0].text == target_quality or
                            e[3].text == target_quality):
                        return _Profile(quality=target_quality,
                                        params=e[1].text,
                                        extension=e[2].text)

    def get_preset_attr(self, target_quality, attr_index=1):
        """Return a dict of preset/params."""
        for elem in self._xml_root:
            for e in elem:
                if e[0].text == target_quality or e[3].text == target_quality:
                    return e[attr_index].text

    def get_qualities_per_profile(self, locale):
        qualities_per_profile = OrderedDict()
        values = []

        for elem in self._xml_root:
            for e in elem:
                if locale == 'es_ES':
                    # Create the dict with values in spanish
                    values.append(e[3].text)
                else:
                    # Create the dict with values in english
                    values.append(e[0].text)

            qualities_per_profile[elem.tag] = values
            # Reinitialize values
            values = []

        return qualities_per_profile

    def save_tree(self):
        """Save xml tree."""
        with open(self._profiles_xml_path, 'wb') as _file:
            try:
                ElementTree.ElementTree(self._xml_root).write(_file)
            except Exception:
                pass

    @property
    def _profiles_xml_path(self):
        return join(expanduser("~"), '.videomorph{0}profiles.xml'.format(sep))

    def create_profiles_xml_file(self):
        profiles_xml = self._profiles_xml_path

        if not exists(profiles_xml):
            if exists('/usr/share/videomorph/stdprofiles/profiles.xml'):
                # if VideoMorph is installed
                copy_file('/usr/share/videomorph/stdprofiles/profiles.xml',
                          profiles_xml)
            else:
                # if not installed
                copy_file('../videomorph/stdprofiles/profiles.xml',
                          profiles_xml)

    def _get_xml_root(self):
        """Returns the profiles.xml root."""
        tree = ElementTree.parse(self._profiles_xml_path)
        return tree.getroot()


XMLProfile = _XMLProfile()


class _Profile:
    """Base class for a Video Profile."""

    def __init__(self,
                 quality=None,
                 params=None,
                 extension=None):
        """Class initializer."""
        self._quality = quality
        self.params = params
        self.extension = extension

    @property
    def quality(self):
        return self._quality

    @quality.setter
    def quality(self, value):
        self._quality = value
        # Update the params and extension when the target quality change
        self.params = XMLProfile.get_preset_attr(self._quality)
        self.extension = XMLProfile.get_preset_attr(self._quality,
                                                    attr_index=2)

    @property
    def quality_tag(self):
        """Generate a tag from profile quality string."""
        tag_regex = compile(r'[A-Z][0-9]?')
        tag = ''.join(tag_regex.findall(self.quality))

        return '[' + tag + ']'
