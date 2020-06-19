#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_utils.py
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

"""This module provides tests for utils.py module."""

import nose
from videomorph.converter import utils


def test_get_locale_all_es():
    """Test get_locale."""
    assert utils.get_locale() in {"en_US", "es_ES"}


def test_which_existing_app():
    """Test for an existing app."""
    assert utils.which("dir").endswith("dir")  # Depends on your system


@nose.tools.raises(ValueError)
def test_which_non_existing_app():
    """Test for a non existing app (raises a ValueError)."""
    utils.which("hypothetical_app")


@nose.tools.raises(ValueError)
def test_which_null_arg():
    """Test for a null string param (raises a ValueError)."""
    utils.which("")


@nose.tools.raises(ValueError)
def test_write_time_none():
    """Convert None."""
    assert utils.write_time(None)


@nose.tools.raises(ValueError)
def test_write_time_sting():
    """Convert string data type."""
    assert utils.write_time("string")


@nose.tools.raises(ValueError)
def test_write_time_tuple():
    """Convert wrong data type."""
    assert utils.write_time((1, 2))


@nose.tools.raises(ValueError)
def test_write_time_wrong_data_types():
    """Convert list data type."""
    assert utils.write_time([1, 2])


def test_write_time_0():
    """Convert 0."""
    assert utils.write_time(0) == "00s"


def test_write_time_2100():
    """Convert 2100."""
    assert utils.write_time(2100) == "35m:00s"


def test_write_time_3600():
    """Convert 3600."""
    assert utils.write_time(3600) == "01h:00m:00s"


def test_write_time_3659():
    """Convert 3659."""
    assert utils.write_time(3659) == "01h:00m:59s"


def test_write_time_3661():
    """Convert 3661."""
    assert utils.write_time(3661) == "01h:01m:01s"


@nose.tools.raises(ValueError)
def test_write_time_negative():
    """Test for negative time value (raises a ValueError)."""
    utils.write_time(-1)


def test_write_size0():
    """Test write_size() with zero."""
    assert utils.write_size(0) == "0.0KiB"


@nose.tools.raises(ValueError)
def test_write_size_negative():
    """Test write_size() with negative size."""
    assert utils.write_size(-1)


def test_write_size_kib():
    """Test write_size() with KiB."""
    assert utils.write_size(1024) == "1.0KiB"


def test_write_size_mib():
    """Test write_size() with MiB."""
    assert utils.write_size(1024 * 2048) == "2.0MiB"


def test_write_size_gib():
    """Test write_size() with GiB."""
    assert utils.write_size(1585558454) == "1.5GiB"


if __name__ == "__main__":
    nose.runmodule()
