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


class XMLProfile:
    """Class to manage the profiles.xml file."""

    def __init__(self):
        self._create_profiles_xml_file()

    def add_conversion_profile(self, profile_name, preset, params, extension):
        xml_profile = ElementTree.Element(profile_name)
        rx = compile(r'[A-z]')
        preset_tag = ''.join(rx.findall(preset))
        xml_preset = ElementTree.Element(preset_tag)
        xml_preset_name = ElementTree.Element('preset_name')
        xml_preset_name.text = preset
        xml_params = ElementTree.Element('preset_params')
        xml_params.text = params
        xml_extension = ElementTree.Element('file_extension')
        xml_extension.text = extension

        for num, elem in enumerate([xml_preset_name, xml_params,
                                    xml_extension, xml_preset_name]):
            xml_preset.insert(num, elem)

        xml_profile.insert(-1, xml_preset)
        # self.save_tree()
        print(xml_profile)

    def get_conversion_profile(self, profile_name, target_quality):
        """Return a Profile objects."""
        for elem in self._xml_root:
            if elem.tag == profile_name:
                for e in elem:
                    if (e[0].text == target_quality or
                            e[3].text == target_quality):
                        return _Profile(name=profile_name,
                                        extension=e[2].text,
                                        quality=target_quality,
                                        params=e[1].text)

    def get_preset_params(self, target_quality):
        """Return a dict of preset/params."""

        for elem in self._xml_root:
            for e in elem:
                if e[0].text == target_quality or e[3].text == target_quality:
                    return e[1].text


    # def get_preset_params(self, locale):
    #     """Return a dict of preset/params."""
    #     preset_params = OrderedDict()
    #
    #     for elem in self._xml_root:
    #         for e in elem:
    #             if locale == 'es_ES':
    #                 # Create the dict with keys in spanish
    #                 preset_params[e[3].text] = e[1].text
    #             else:
    #                 # Create the dict with keys in english
    #                 preset_params[e[0].text] = e[1].text
    #
    #     return preset_params

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

    def _create_profiles_xml_file(self):
        profiles_xml = self._profiles_xml_path

        if not exists(profiles_xml):
            if exists('/usr/share/videomorph/stdprofiles/profiles.xml'):
                # if VideoMorph is installed
                copy_file('/usr/share/videomorph/stdprofiles/profiles.xml',
                          profiles_xml)
            else:
                # if not installed
                copy_file('../videomorph/stdprofiles/profiles.xml', profiles_xml)

    @property
    def _xml_root(self):
        """Returns the profiles.xml root."""
        tree = ElementTree.parse(self._profiles_xml_path)
        return tree.getroot()


class _Profile:
    """Base class for a Video Profile."""

    def __init__(self,
                 name=None,
                 extension=None,
                 quality=None,
                 params=None):
        """Class initializer."""
        self.name = name
        self.extension = extension
        self._quality = quality
        self.params = params

    @property
    def quality(self):
        return self._quality

    @quality.setter
    def quality(self, value):
        self._quality = value
        # TODO: Modify self.params when self._quality change

    @property
    def quality_tag(self):
        """Generate a tag from profile quality string."""
        tag_regex = compile(r'[A-Z]4?')
        tag = ''.join(tag_regex.findall(self.quality))

        return '[' + tag + ']'
