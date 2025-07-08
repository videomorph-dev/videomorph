"""This module provides tests for profile.py module."""

from typing import Dict, List

import pytest

from videomorph.converter.library import Library
from videomorph.converter.profile import Profile


@pytest.fixture
def profile() -> Profile:
    """Profile fixture for tests."""
    profile = Profile()
    profile.update(new_quality="MP4 Fullscreen (4:3)")
    return profile


@pytest.fixture
def conv() -> Library:
    """Library fixture for tests."""
    return Library()


def test_get_json_profile_attr(profile: Profile) -> None:
    """Test get_json_profile_attr."""
    attr = profile.get_json_profile_attr(
        target_quality="MP4 Fullscreen (4:3)", attr_name="params"
    )

    assert (
        attr
        == "-f mp4 -r 29.97 -vcodec libx264 -s 640x480 -b:v 1000k -aspect 4:3 -flags +loop -cmp +chroma -maxrate 1500k -bufsize 4M -bt 256k -refs 1 -bf 3 -coder 1 -me_method umh -me_range 16 -subq 7 -partitions +parti4x4+parti8x8+partp8x8+partb8x8 -g 250 -keyint_min 25 -level 30 -qmin 10 -qmax 51 -qcomp 0.6 -sc_threshold 40 -i_qfactor 0.71 -acodec aac -b:a 112k -ar 48000 -ac 2 -strict -2"
    )


def test_get_json_profile_qualities_en(profile: Profile) -> None:
    """Test get_json_profile_qualities -> english."""
    qualities: Dict[str, List[str]] = profile.get_json_profile_qualities(
        "en_US"
    )
    assert qualities["AVI"] == [
        "MS Compatible 640x480",
        "MS Compatible 720x480",
        "XVID Fullscreen 640x480 (4:3)",
        "XVID Widescreen 704x384 (16:9)",
        "AVI Optimized for YouTube",
    ]


def test_get_json_profile_qualities_es(profile: Profile) -> None:
    """Test get_json_profile_qualities -> spanish."""
    qualities: Dict[str, List[str]] = profile.get_json_profile_qualities(
        "es_ES"
    )
    assert qualities["AVI"] == [
        "Compatible MS 640x480",
        "Compatible MS 720x480",
        "XVID Pantalla Completa 640x480 (4:3)",
        "XVID Pantalla Panorámica 704x384 (16:9)",
        "AVI Optimizado para YouTube",
    ]


def test_quality_tag(profile: Profile) -> None:
    """Test Profile.quality_tag."""
    assert profile.quality_tag == "[MP4F]-"


def test_update(profile: Profile) -> None:
    """Test update."""
    profile.update(new_quality="WMV Generic")
    assert (
        profile.params == "-vcodec wmv2 -acodec wmav2 -b:v 1000k "
        "-b:a 160k -r 25"
    )
    assert profile.extension == ".wmv"
