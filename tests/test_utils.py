#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_utils.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
#   Copyright 2016-2020 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""This module provides tests for utils.py module."""

import pytest
from pytest import param

from videomorph.converter import utils


def test_get_locale_all_es():
    """Test get_locale."""
    assert utils.get_locale() in {"en_US", "es_ES"}


def test_which_existing_app():
    """Test for an existing app."""
    assert utils.which("dir").name == "dir"  # Depends on your system


def test_which_non_existing_app():
    """Test for a non existing app (raises a ValueError)."""
    with pytest.raises(ValueError):
        utils.which("hypothetical_app")


def test_which_null_arg():
    """Test for a null string param (raises a ValueError)."""
    with pytest.raises(ValueError):
        utils.which("")


def test_write_time_none():
    """Convert None."""
    with pytest.raises(ValueError):
        utils.write_time(None)


def test_write_time_sting():
    """Convert string data type."""
    with pytest.raises(ValueError):
        utils.write_time("string")


def test_write_time_tuple():
    """Convert wrong data type."""
    with pytest.raises(ValueError):
        utils.write_time((1, 2))


def test_write_time_wrong_data_types():
    """Convert list data type."""
    with pytest.raises(ValueError):
        utils.write_time([1, 2])


@pytest.mark.parametrize(
    """time, expected""",
    [
        param(0, "00s"),
        param(2100, "35m:00s"),
        param(3600, "01h:00m:00s"),
        param(3659, "01h:00m:59s"),
        param(3661, "01h:01m:01s"),
        param(3661, "01h:01m:01s"),
    ],
)
def test_write_time(time, expected):
    """Test time writer."""
    assert utils.write_time(time) == expected


def test_write_time_negative():
    """Test for negative time value (raises a ValueError)."""
    with pytest.raises(ValueError):
        utils.write_time(-1)


def test_write_size_negative():
    """Test write_size() with negative size."""
    with pytest.raises(ValueError):
        utils.write_size(-1)


@pytest.mark.parametrize(
    """size, expected""",
    [
        param(0, "0.0KiB"),
        param(1024, "1.0KiB"),
        param(1024 * 2048, "2.0MiB"),
        param(1585558454, "1.5GiB"),
    ],
)
def test_write_size(size, expected):
    """Test write_size() with KiB."""
    assert utils.write_size(size) == expected
