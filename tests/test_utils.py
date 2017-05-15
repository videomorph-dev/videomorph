#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: test_utils.py
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

"""This module provides tests for utils.py module."""

import nose

from videomorph.converter import utils


@nose.tools.raises(ValueError)
def test_convert_none():
    """Convert None."""
    assert utils.write_time(None)


@nose.tools.raises(ValueError)
def test_convert_wrong_data_type():
    """Convert None."""
    assert utils.write_time('string')
    assert utils.write_time((1, 2))
    assert utils.write_time([1, 2])
    assert utils.write_time({'time': 25})


def test_convert_0():
    """Convert 0."""
    assert utils.write_time(0) == '00s'


def test_convert_2100():
    """Convert 2100."""
    assert utils.write_time(2100) == '35m:00s'


def test_convert_3600():
    """Convert 3600."""
    assert utils.write_time(3600) == '01h:00m:00s'


def test_convert_3659():
    """Convert 3659."""
    assert utils.write_time(3659) == '01h:00m:59s'


def test_convert_3661():
    """Convert 3661."""
    assert utils.write_time(3661) == '01h:01m:01s'


@nose.tools.raises(ValueError)
def test_raise_value_error():
    """Test for negative time value (raises a ValueError)."""
    utils.write_time(-1)


def test_which_existing_app():
    """Test for an existing app."""
    assert utils.which('ls') == '/bin/ls' # Depends on your system


def test_which_non_existing_app():
    """Test for a non existing app."""
    assert utils.which('hypothetical_app') is None


@nose.tools.raises(ValueError)
def test_which_null_arg():
    """Test for a null string param (raises a ValueError)."""
    utils.which('')


def test_get_locale():
    """Test get_locale."""
    from locale import getdefaultlocale
    assert utils.get_locale() == getdefaultlocale()[0] or 'es_ES'


if __name__ == '__main__':
    nose.runmodule()
