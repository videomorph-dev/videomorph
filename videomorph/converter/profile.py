"""This module provides the Profile class for JSON-based profiles."""

import json
import re
from collections import OrderedDict, namedtuple
from pathlib import Path
from shutil import copy2
from typing import Any, Dict, List, Optional

from videomorph.converter import LOCALE, VALID_VIDEO_EXT
from videomorph.converter.codec import CodecsReader
from videomorph.converter.vmpath import packaged_profile, profiles_user_dir

JSONFiles = namedtuple("JSONFiles", "default customized")
JSON_FILES = JSONFiles("default.json", "customized.json")


class Profile:
    """Base class for a Conversion Profile."""

    def __init__(self) -> None:
        """Class initializer."""
        self._json_profile = _JSONProfile()
        self._quality: Optional[str] = None
        self.extension: Optional[str] = None
        self.params: Optional[str] = None

    def __getattr__(self, attr: str) -> Any:
        """Delegate to manage the _JSONProfile object."""
        return getattr(self._json_profile, attr)

    def update(self, new_quality):
        """Set the target Quality and other parameters needed to get it."""
        self._quality = new_quality
        # Update the params and extension when the target quality change
        self.params = self.get_json_profile_attr(
            target_quality=self._quality, attr_name="params"
        )
        self.extension = self.get_json_profile_attr(
            target_quality=self._quality, attr_name="extension"
        )

    @property
    def quality_tag(self) -> str:
        """Generate a tag from profile quality string."""
        if self._quality is None:
            return "[?]-"

        tag_regex = re.compile(r"[A-Z][0-9]?")
        tag = "".join(tag_regex.findall(self._quality))

        if not tag:
            tag = "".join(word[0] for word in self._quality.split()).upper()

        return "[" + tag + "]-"


class _JSONProfile:
    """Class to manage the json profiles file."""

    def __init__(
        self,
        json_files=JSON_FILES,
        valid_extensions=VALID_VIDEO_EXT,
    ):
        """Class initializer."""
        self._json_files = json_files
        self._valid_ext = valid_extensions
        self._codecs_reader = None  # Lazy initialization
        self._user_profiles_dir = profiles_user_dir()

        self._create_json_files()
    
    @property
    def _available_codecs(self):
        """Lazy-load codecs only when needed."""
        if self._codecs_reader is None:
            self._codecs_reader = CodecsReader()
        return self._codecs_reader

    def get_json_profile_qualities(self, locale=LOCALE) -> OrderedDict:
        """Return a list of available Qualities per conversion profile."""
        qualities_per_profile = OrderedDict()

        for json_file in self._json_files:
            profiles_data = self._load_json_data(json_file)
            
            for profile in profiles_data:
                qualities = self._get_qualities(profile, locale)

                if not qualities:
                    continue

                profile_name = profile.get("name")
                if profile_name not in qualities_per_profile:
                    qualities_per_profile[profile_name] = qualities
                else:
                    qualities_per_profile[profile_name] += qualities

        return qualities_per_profile

    def _get_qualities(self, profile: Dict, locale=LOCALE) -> List[str]:
        """Extract quality names from profile presets."""
        qualities = []
        for preset in profile.get("presets", []):
            if self._codecs_are_available(preset.get("params", "")):
                if locale == "es_ES":
                    qualities.append(preset.get("name_es", ""))
                else:
                    qualities.append(preset.get("name_en", ""))
        return qualities

    def get_json_profile_attr(self, target_quality: str, attr_name: str = "params") -> str:
        """Return a param of Profile."""
        for json_file in self._json_files:
            profiles_data = self._load_json_data(json_file)
            
            for profile in profiles_data:
                for preset in profile.get("presets", []):
                    if (
                        preset.get("name_en") == target_quality
                        or preset.get("name_es") == target_quality
                    ):
                        return preset.get(attr_name, "")

        raise ValueError(f"Wrong quality '{target_quality}' or param '{attr_name}'.")

    @staticmethod
    def _get_preset_codecs(params: str):
        """Extract codec information from ffmpeg parameters."""
        acodec_regex = re.compile(r"-acodec\s+([^ ]+)")
        vcodec_regex = re.compile(r"-vcodec\s+([^ ]+)")
        scodec_regex = re.compile(r"-scodec\s+([^ ]+)")

        def codec(regex):
            result = regex.findall(params)
            if result:
                return result[0]
            return None

        Codecs = namedtuple("Codecs", ["acodec", "vcodec", "scodec"])

        return Codecs(
            codec(acodec_regex), codec(vcodec_regex), codec(scodec_regex)
        )

    def _codecs_are_available(self, params: str) -> bool:
        """Check if all codecs in params are available in the system."""
        preset_codecs = self._get_preset_codecs(params)
        vcodec = acodec = scodec = True

        if preset_codecs.vcodec is not None:
            if not (
                preset_codecs.vcodec in self._available_codecs.vencoders
                or preset_codecs.vcodec in self._available_codecs.vcodecs
            ):
                vcodec = False

        if preset_codecs.acodec is not None:
            if not (
                preset_codecs.acodec in self._available_codecs.aencoders
                or preset_codecs.acodec in self._available_codecs.acodecs
            ):
                acodec = False

        if preset_codecs.scodec is not None:
            if not (
                preset_codecs.scodec in self._available_codecs.sencoders
                or preset_codecs.scodec in self._available_codecs.scodecs
            ):
                scodec = False

        return vcodec and acodec and scodec

    def restore_default_profiles(self):
        """Restore default profiles."""
        for json_file in self._json_files:
            self._copy_json_file(file_name=json_file)

    def _user_json_file_path(self, file_name: str) -> Path:
        """Return the path to the profiles file."""
        return self._user_json_files_directory() / file_name

    def _create_json_files(self):
        """Create a json file with the conversion profiles."""
        self._user_json_files_directory().mkdir(parents=True, exist_ok=True)

        for json_file in self._json_files:
            if not self._json_file_is_correct(json_file):
                self._copy_json_file(file_name=json_file)

    def _copy_json_file(self, file_name: str):
        """Copy profiles json file."""
        copy2(
            src=self._sys_json_file_path(file_name),
            dst=self._user_json_file_path(file_name),
        )

    def _json_file_is_correct(self, file_name: str) -> bool:
        """Validate json files in user config directory."""
        json_file_user_path = self._user_json_file_path(file_name)
        json_file_sys_path = self._sys_json_file_path(file_name)

        if not json_file_user_path.exists() or json_file_user_path.stat().st_size == 0:
            return False

        if json_file_sys_path.stat().st_mtime > json_file_user_path.stat().st_mtime:
            return False

        return True

    def _load_json_data(self, json_file_name: str) -> List[Dict]:
        """Load and validate JSON data from file."""
        path = self._user_json_file_path(file_name=json_file_name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._validate_json(data)
            return data
        except (json.JSONDecodeError, AssertionError, FileNotFoundError) as e:
            print(f"Error loading JSON file {path}: {e}")
            self.restore_default_profiles()
            # Try again after restoring defaults
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data

    @staticmethod
    def _validate_json(profiles_data: List[Dict]):
        """Validate json profiles structure."""
        assert isinstance(profiles_data, list), "Root must be an array"

        for profile in profiles_data:
            assert isinstance(profile, dict), "Profile must be an object"
            assert "name" in profile, "Profile must have 'name'"
            assert "presets" in profile, "Profile must have 'presets'"
            assert isinstance(profile["presets"], list), "Presets must be an array"
            
            for preset in profile["presets"]:
                assert isinstance(preset, dict), "Preset must be an object"
                required_fields = ["name_en", "params", "extension", "name_es"]
                for field in required_fields:
                    assert field in preset, f"Preset must have '{field}'"
                    assert isinstance(preset[field], str), f"'{field}' must be a string"

    def _user_json_files_directory(self) -> Path:
        """Return the user json directory path."""
        return self._user_profiles_dir

    def _sys_json_file_path(self, file_name: str) -> Path:
        """Return the path to json profiles file in the system."""
        return packaged_profile(file_name)
