"""This module provides tests for video.py module."""

from videomorph.converter.video import Video


class TestVideo:
    """Class for testing video.py module."""

    def test_get_name(self) -> None:
        """Test TaskList.get_file_name()."""
        assert Video("sample-video.mp4").get_name() == "sample-video"

    def test_get_name_with_extension(self) -> None:
        """Test TaskList.get_file_name() with extension."""
        assert (
            Video("sample-video.mp4").get_name(with_extension=True)
            == "sample-video.mp4"
        )

    def test_video_is_valid_right_duration(self) -> None:
        assert Video("sample-video.mp4").is_valid()

    def test_video_is_valid_zero_duration(self) -> None:
        video = Video("sample-video.mp4")
        video._info.format_info["duration"] = 0
        assert not video.is_valid()

    def test_video_is_valid_wrong_type(self) -> None:
        video = Video("sample-video.mp4")
        video._info.format_info["duration"] = []
        assert not video.is_valid()

    def test_video_is_valid_wrong_value(self) -> None:
        video = Video("sample-video.mp4")
        video._info.format_info["duration"] = "N/A"
        assert not video.is_valid()
