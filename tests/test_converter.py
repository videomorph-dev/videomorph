"""This module provides tests for converter library."""

from typing import List
from PyQt6.QtCore import QProcess

from videomorph.converter import tasklist
from videomorph.converter.library import Library
from videomorph.converter.profile import Profile


class TestConversionLib:
    """Class for testing Library."""

    conv_lib = Library()
    profile = Profile()
    profile.update(new_quality="FLV Fullscreen 320x240 (4:3)")
    media_list = tasklist.TaskList(profile)

    @classmethod
    def setup_class(cls) -> None:
        """Setup method to run before all tests."""
        # Add a test video file to the task list
        cls.media_list.add_task("sample-video.mp4")

    @classmethod
    def teardown_class(cls) -> None:
        """Teardown method to run after all tests."""
        try:
            if len(cls.media_list) > 0:
                cls.media_list.delete_running_file_output(tagged=True)
        except (IndexError, AttributeError):
            pass  # No tasks to clean up

    def get_conversion_cmd(self) -> List[str]:
        """Return a conversion command."""
        cmd = self.media_list.get_task(position=0).build_conversion_cmd(
            subtitle=False,
            tagged=True,
            target_quality="FLV Fullscreen 320x240 (4:3)",
        )
        return cmd

    def test_get_library_path(self) -> None:
        """Test Library.library_path."""
        library_path = self.conv_lib._converter._library_path
        assert library_path is not None
        assert "ffmpeg" in library_path

    def test_prober_path(self) -> None:
        """Test the Library.prober_path."""
        from videomorph.converter.vmpath import PROBE_PATH

        assert PROBE_PATH is not None
        assert "ffprobe" in PROBE_PATH

    def test_start_converter(self) -> None:
        """Test Library.start_converter()."""
        self.conv_lib.start_converter(cmd=self.get_conversion_cmd())

        assert (
            self.conv_lib.converter_state() == QProcess.ProcessState.Starting
        )
        self.conv_lib.stop_converter()

    def test_read_converter_output(self) -> None:
        """Test Library.read_converter_output()."""
        self.conv_lib.start_converter(cmd=self.get_conversion_cmd())
        assert self.conv_lib.read_converter_output()
        self.conv_lib.stop_converter()

    def test_catch_library_error_true(self) -> None:
        """Test _OutputReader.catch_library_error() -> true."""
        self.conv_lib.reader.update_read(
            "Some random output with " "Unknown encoder error"
        )
        assert self.conv_lib.reader.catch_library_error() == "Unknown encoder"

    def test_catch_library_error_false(self) -> None:
        """Test _OutputReader.catch_library_error() -> false."""
        self.conv_lib.reader.update_read("Some random output with " "no error")
        assert self.conv_lib.reader.catch_library_error() is None

    def test_stop_converter(self) -> None:
        """Test Library.stop_converter()."""
        self.conv_lib.stop_converter()
        assert not self.conv_lib.converter_is_running
