# -*- coding: utf-8 -*-
#
# File name: profile.py
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

"""This module provides the Profile class."""

import re
import xml.etree.ElementTree as ET
from collections import OrderedDict
from collections import namedtuple
from shutil import copy2
from os import makedirs
from os.path import exists, getsize
from os.path import getmtime
from os.path import join as join_path

from . import BASE_DIR
from . import LOCALE
from . import SYS_PATHS
from . import VM_PATHS
from . import VALID_VIDEO_EXT
from .codec import CodecsReader
from .exceptions import ProfileBlankNameError
from .exceptions import ProfileBlankParamsError
from .exceptions import ProfileBlankPresetError
from .exceptions import ProfileExtensionError

XMLFiles = namedtuple('XMLFiles', 'default customized')
XML_FILES = XMLFiles('default.xml', 'customized.xml')


class Profile:
    """Base class for a Conversion Profile."""

    def __init__(self):
        """Class initializer."""
        self._xml_profile = _XMLProfile()
        self._quality = None
        self.extension = None
        self.params = None

    def __getattr__(self, attr):
        """Delegate to manage the _XMLProfile object."""
        return getattr(self._xml_profile, attr)

    def update(self, new_quality):
        """Set the target Quality and other parameters needed to get it."""
        self._quality = new_quality
        # Update the params and extension when the target quality change
        self.params = self.get_xml_profile_attr(
            target_quality=self._quality,
            attr_name='preset_params')
        self.extension = self.get_xml_profile_attr(
            target_quality=self._quality,
            attr_name='file_extension')

    @property
    def quality_tag(self):
        """Generate a tag from profile quality string."""
        tag_regex = re.compile(r'[A-Z][0-9]?')
        tag = ''.join(tag_regex.findall(self._quality))

        if not tag:
            tag = ''.join(word[0] for word in self._quality.split()).upper()

        return '[' + tag + ']-'


class _XMLProfile:
    """Class to manage the xml profiles file."""

    def __init__(self):
        """Class initializer."""
        self._create_xml_files()
        self.available_codecs = CodecsReader()

    def get_xml_profile_qualities(self):
        """Return a list of available Qualities per conversion profile."""
        qualities_per_profile = OrderedDict()

        for xml_file in XML_FILES:
            for profile in self._xml_root(xml_file):
                qualities = self._get_qualities(profile)

                if not qualities:
                    continue

                if profile.tag not in qualities_per_profile:
                    qualities_per_profile[profile.tag] = qualities
                else:
                    qualities_per_profile[profile.tag] += qualities

        return qualities_per_profile

    def _get_qualities(self, profile):
        qualities = []
        for preset in profile:
            if self._codecs_are_available(preset[1].text):
                if LOCALE == 'es_ES':
                    qualities.append(preset[3].text)
                else:
                    qualities.append(preset[0].text)
        return qualities

    def get_xml_profile_attr(self, target_quality, attr_name='preset_params'):
        """Return a param of Profile."""
        param_map = {'preset_name': 0,
                     'preset_params': 1,
                     'file_extension': 2,
                     'preset_name_es': 3}

        for xml_file in XML_FILES:
            for profile in self._xml_root(xml_file):
                for preset in profile:
                    if (preset[0].text == target_quality or
                            preset[3].text == target_quality):
                        return preset[param_map[attr_name]].text

        raise ValueError('Wrong quality or param.')

    def get_profiles(self):
        profiles_dict = OrderedDict()
        for xml_file in XML_FILES:
            for profiles in self._xml_root(xml_file):
                profiles_dict[profiles.tag] = {}
                for presets in profiles:
                    profiles_dict[profiles.tag][presets.tag] = {}
                    for item in presets:
                        if item.tag == 'preset_params':
                            if not self._codecs_are_available(item.text):
                                del profiles_dict[profiles.tag][presets.tag]
                                break
                        profiles_dict[profiles.tag][presets.tag][item.tag] =\
                            item.text

                if not profiles_dict[profiles.tag]:
                    del profiles_dict[profiles.tag]

        return profiles_dict

    @staticmethod
    def _get_preset_codecs(params):
        acodec_regex = re.compile(r'-acodec\s+([^ ]+)')
        vcodec_regex = re.compile(r'-vcodec\s+([^ ]+)')
        scodec_regex = re.compile(r'-scodec\s+([^ ]+)')

        def codec(regex):
            result = regex.findall(params)
            if result:
                return result[0]

            return None

        Codecs = namedtuple('Codecs', ['acodec', 'vcodec', 'scodec'])

        return Codecs(codec(acodec_regex),
                      codec(vcodec_regex),
                      codec(scodec_regex))

    def _codecs_are_available(self, params):
        preset_codecs = self._get_preset_codecs(params)
        vcodec = acodec = scodec = True

        if preset_codecs.vcodec is not None:
            if not (preset_codecs.vcodec in self.available_codecs.vencoders or
                    preset_codecs.vcodec in self.available_codecs.vcodecs):
                vcodec = False

        if preset_codecs.acodec is not None:
            if not (preset_codecs.acodec in self.available_codecs.aencoders or
                    preset_codecs.acodec in self.available_codecs.acodecs):
                acodec = False

        if preset_codecs.scodec is not None:
            if not (preset_codecs.scodec in self.available_codecs.sencoders or
                    preset_codecs.scodec in self.available_codecs.scodecs):
                scodec = False

        return vcodec and acodec and scodec

    def restore_default_profiles(self):
        """Restore default profiles."""
        self._copy_xml_file(file_name=XML_FILES.customized)

    def add_xml_profile(self, profile_name, preset, params, extension):
        """Add a conversion profile."""
        if not profile_name:
            raise ProfileBlankNameError

        profile_name = profile_name.upper()

        if not preset:
            raise ProfileBlankPresetError

        if not params:
            raise ProfileBlankParamsError

        if not extension.startswith('.') or extension not in VALID_VIDEO_EXT:
            raise ProfileExtensionError('Invalid video file extension')

        extension = extension.lower()

        xml_profile = ET.Element(profile_name)

        xml_preset = self._create_xml_preset(preset, params, extension)

        self._insert_xml_elements(xml_profile=xml_profile,
                                  xml_preset=xml_preset,
                                  xml_root=self._xml_root(
                                      XML_FILES.customized))

    def export_xml_profiles(self, dst_dir):
        """Export a file with the conversion profiles."""
        # Raise PermissionError if user doesn't have write permission
        try:
            copy2(src=self._user_xml_file_path(
                file_name=XML_FILES.customized),
                  dst=dst_dir)
        except OSError:
            raise PermissionError

    def import_xml_profiles(self, src_file):
        """Import a conversion profile file."""
        try:
            dst_directory = self._user_xml_file_path(
                XML_FILES.customized)
            copy2(src=src_file, dst=dst_directory)
        except OSError:
            raise PermissionError

    def _user_xml_file_path(self, file_name):
        """Return the path to the profiles file."""
        return join_path(self._user_xml_files_directory(), file_name)

    def _insert_xml_elements(self, xml_profile, xml_preset, xml_root):
        """Insert an xml element into an xml root."""
        for i, elem in enumerate(xml_root[:]):
            if elem.tag == xml_profile.tag:
                xml_root[i].insert(0, xml_preset)
                self._save_xml_tree(xml_tree=xml_root)
                break
        else:
            xml_profile.insert(0, xml_preset)
            xml_root.insert(0, xml_profile)
            self._save_xml_tree(xml_tree=xml_root)

    def _save_xml_tree(self, xml_tree):
        """Save the xml tree."""
        xml_profiles_path = self._user_xml_file_path(
            XML_FILES.customized)

        with open(xml_profiles_path, 'wb') as xml_file:
            ET.ElementTree(xml_tree).write(xml_file,
                                           xml_declaration=True,
                                           encoding='UTF-8')

    def _create_xml_files(self):
        """Create a xml file with the conversion profiles."""
        makedirs(self._user_xml_files_directory(), exist_ok=True)

        for xml_file in XML_FILES:
            if not self._xml_file_is_correct(xml_file):
                self._copy_xml_file(file_name=xml_file)

    def _copy_xml_file(self, file_name):
        """Copy profiles xml file."""
        xml_file_sys_path = self._sys_xml_file_path(file_name)
        xml_file_user_path = self._user_xml_file_path(file_name)

        copy2(src=xml_file_sys_path, dst=xml_file_user_path)

    def _xml_file_is_correct(self, file_name):
        """Validate xml files in user config directory."""
        xml_file_user_path = self._user_xml_file_path(file_name)
        xml_file_sys_path = self._sys_xml_file_path(file_name)

        if not exists(xml_file_user_path) or not getsize(xml_file_user_path):
            return False

        if getmtime(xml_file_sys_path) > getmtime(xml_file_user_path):
            return False

        return True

    def _xml_root(self, xml_file_name):
        """Return the xml root."""
        path = self._user_xml_file_path(file_name=xml_file_name)
        try:
            tree = ET.parse(path)
        except ET.ParseError:
            self.restore_default_profiles()
            tree = ET.parse(path)
        return tree.getroot()

    @staticmethod
    def _user_xml_files_directory():
        """Return the user xml directory path."""
        return join_path(SYS_PATHS.config, 'profiles')

    @staticmethod
    def _sys_xml_file_path(file_name):
        """Return the path to xml profiles file in the system."""
        file_path = join_path(SYS_PATHS.profiles, file_name)
        if exists(file_path):
            # if VideoMorph is installed
            return file_path

        # if not installed
        return join_path(BASE_DIR, VM_PATHS.profiles, file_name)

    @staticmethod
    def _create_xml_preset(preset, params, extension):
        """Return a xml preset."""
        regexp = re.compile(r'[A-z][0-9]?')
        preset_tag = ''.join(regexp.findall(preset))
        xml_preset = ET.Element(preset_tag)
        xml_preset_name = ET.Element('preset_name')
        xml_preset_name.text = preset
        xml_params = ET.Element('preset_params')
        xml_params.text = params
        xml_extension = ET.Element('file_extension')
        xml_extension.text = extension
        xml_preset_name_es = ET.Element('preset_name_es')
        xml_preset_name_es.text = preset

        for i, elem in enumerate([xml_preset_name, xml_params,
                                  xml_extension, xml_preset_name_es]):
            xml_preset.insert(i, elem)

        return xml_preset
