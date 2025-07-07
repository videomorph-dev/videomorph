"""This module provides tests for utils.py module."""

import pytest

from videomorph.converter import utils


def test_get_locale_all_es() -> None:
    """Test get_locale."""
    assert utils.get_locale() in {"en_US", "es_ES"}


def test_which_existing_app() -> None:
    """Test for an existing app."""
    assert utils.which("dir").endswith("dir")  # Depends on your system


def test_which_non_existing_app() -> None:
    """Test for a non existing app (raises a ValueError)."""
    with pytest.raises(ValueError):
        utils.which("hypothetical_app")


def test_which_null_arg() -> None:
    """Test for a null string param (raises a ValueError)."""
    with pytest.raises(ValueError):
        utils.which("")


def test_write_time_none() -> None:
    """Convert None."""
    with pytest.raises(ValueError):
        utils.write_time(None)


def test_write_time_sting() -> None:
    """Convert string data type."""
    with pytest.raises(ValueError):
        utils.write_time("string")


def test_write_time_tuple() -> None:
    """Convert wrong data type."""
    with pytest.raises(ValueError):
        utils.write_time((1, 2))


def test_write_time_wrong_data_types() -> None:
    """Convert list data type."""
    with pytest.raises(ValueError):
        utils.write_time([1, 2])


def test_write_time_0() -> None:
    """Convert 0."""
    assert utils.write_time(0) == "00s"


def test_write_time_2100() -> None:
    """Convert 2100."""
    assert utils.write_time(2100) == "35m:00s"


def test_write_time_3600() -> None:
    """Convert 3600."""
    assert utils.write_time(3600) == "01h:00m:00s"


def test_write_time_3659() -> None:
    """Convert 3659."""
    assert utils.write_time(3659) == "01h:00m:59s"


def test_write_time_3661() -> None:
    """Convert 3661."""
    assert utils.write_time(3661) == "01h:01m:01s"


def test_write_time_negative() -> None:
    """Test for negative time value (raises a ValueError)."""
    with pytest.raises(ValueError):
        utils.write_time(-1)


def test_write_size0() -> None:
    """Test write_size() with zero."""
    assert utils.write_size(0) == "0.0KiB"


def test_write_size_negative() -> None:
    """Test write_size() with negative size."""
    with pytest.raises(ValueError):
        utils.write_size(-1)


def test_write_size_kib() -> None:
    """Test write_size() with KiB."""
    assert utils.write_size(1024) == "1.0KiB"


def test_write_size_mib() -> None:
    """Test write_size() with MiB."""
    assert utils.write_size(1024 * 2048) == "2.0MiB"


def test_write_size_gib() -> None:
    """Test write_size() with GiB."""
    assert utils.write_size(1585558454) == "1.5GiB"
