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
from os import makedirs
from os.path import exists, getsize
from os.path import getmtime
from os.path import join as join_path
from shutil import copy2

from . import BASE_DIR
from . import LOCALE
from . import SYS_PATHS
from . import VALID_VIDEO_EXT
from . import VM_PATHS
from .codec import CodecsReader

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
            attr_name='preset_extension')

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

    def __init__(self,
                 xml_files=XML_FILES,
                 base_dir=BASE_DIR,
                 sys_path=SYS_PATHS,
                 vmpath=VM_PATHS,
                 valid_extensions=VALID_VIDEO_EXT):
        """Class initializer."""
        self._xml_files = xml_files
        self._base_dir = base_dir
        self._sys_path = sys_path
        self._vmpath = vmpath
        self._valid_ext = valid_extensions
        self._available_codecs = CodecsReader()

        self._create_xml_files()

    def get_xml_profile_qualities(self, locale=LOCALE):
        """Return a list of available Qualities per conversion profile."""
        qualities_per_profile = OrderedDict()

        for xml_file in self._xml_files:
            for profile in self._xml_root(xml_file):
                qualities = self._get_qualities(profile, locale)

                if not qualities:
                    continue

                if profile.get('name') not in qualities_per_profile:
                    qualities_per_profile[profile.get('name')] = qualities
                else:
                    qualities_per_profile[profile.get('name')] += qualities

        return qualities_per_profile

    def _get_qualities(self, profile, locale=LOCALE):
        qualities = []
        for preset in profile:
            if self._codecs_are_available(preset[1].text):
                if locale == 'es_ES':
                    qualities.append(preset[3].text)
                else:
                    qualities.append(preset[0].text)
        return qualities

    def get_xml_profile_attr(self, target_quality, attr_name='preset_params'):
        """Return a param of Profile."""
        param_map = {'preset_name_en': 0,
                     'preset_params': 1,
                     'preset_extension': 2,
                     'preset_name_es': 3}

        for xml_file in self._xml_files:
            for profile in self._xml_root(xml_file):
                for preset in profile:
                    if (preset[0].text == target_quality or
                            preset[3].text == target_quality):
                        return preset[param_map[attr_name]].text

        raise ValueError('Wrong quality or param.')

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
            if not (preset_codecs.vcodec in self._available_codecs.vencoders or
                    preset_codecs.vcodec in self._available_codecs.vcodecs):
                vcodec = False

        if preset_codecs.acodec is not None:
            if not (preset_codecs.acodec in self._available_codecs.aencoders or
                    preset_codecs.acodec in self._available_codecs.acodecs):
                acodec = False

        if preset_codecs.scodec is not None:
            if not (preset_codecs.scodec in self._available_codecs.sencoders or
                    preset_codecs.scodec in self._available_codecs.scodecs):
                scodec = False

        return vcodec and acodec and scodec

    def restore_default_profiles(self):
        """Restore default profiles."""
        for xml_file in self._xml_files:
            self._copy_xml_file(file_name=xml_file)

    def _user_xml_file_path(self, file_name):
        """Return the path to the profiles file."""
        return join_path(self._user_xml_files_directory(), file_name)

    def _create_xml_files(self):
        """Create a xml file with the conversion profiles."""
        makedirs(self._user_xml_files_directory(), exist_ok=True)

        for xml_file in self._xml_files:
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
            self._validate_xml(tree.getroot())
        except (ET.ParseError, AssertionError):
            self.restore_default_profiles()
            tree = ET.parse(path)

        return tree.getroot()

    @staticmethod
    def _validate_xml(xml_root):
        """Validate xml profiles."""
        assert xml_root.tag == 'videomorph', 'videomorph'

        for profile in xml_root:
            assert profile.tag == 'profile', 'profile'
            assert 'name' in profile.attrib, 'name'
            for preset in profile:
                assert preset.tag == 'preset', 'preset'
                assert preset[0].tag == 'preset_name_en', 'preset_name_en'
                assert preset[1].tag == 'preset_params', 'preset_params'
                assert preset[2].tag == 'preset_extension', 'preset_extension'
                assert preset[3].tag == 'preset_name_es', 'preset_name_es'
                assert len(preset) == 4, 'fields'

    def _user_xml_files_directory(self):
        """Return the user xml directory path."""
        return join_path(self._sys_path['config'], 'profiles')

    def _sys_xml_file_path(self, file_name):
        """Return the path to xml profiles file in the system."""
        file_path = join_path(self._sys_path['profiles'], file_name)
        if exists(file_path):
            # if VideoMorph is installed
            return file_path

        # if not installed
        return join_path(self._base_dir, self._vmpath['profiles'], file_name)
