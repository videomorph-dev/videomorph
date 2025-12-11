"""This module provides tests for converter library."""

from typing import List

from PyQt6.QtCore import QProcess

from videomorph.converter.converter import Converter
from videomorph.converter.profile import Profile
from videomorph.converter.tasklist import TaskList


class TestConverter:
    """Class for testing Converter."""

    converter = Converter()
    profile = Profile()
    profile.update(new_quality="FLV Fullscreen 320x240 (4:3)")
    media_list = TaskList(profile)

    @classmethod
    def setup_class(cls) -> None:
        """Setup method to run before all tests."""
        # Add a test video file to the task list
        cls.media_list.add_task("sample-video.mp4")

    @classmethod
    def teardown_class(cls) -> None:
        """Teardown method to run after all tests."""
        try:
            if len(cls.media_list) > 0 and cls.media_list.position is not None:
                cls.media_list.delete_running_file_output(tagged=True)
        except (IndexError, AttributeError, ValueError):
            pass  # No tasks to clean up or no running task

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
        library_path = self.converter._library_path
        assert library_path is not None
        assert "ffmpeg" in library_path

    def test_prober_path(self) -> None:
        """Test the Library.prober_path."""
        from videomorph.converter.paths import path_manager

        assert path_manager.probe_path is not None
        assert "ffprobe" in path_manager.probe_path

    def test_start(self) -> None:
        """Test Library.start()."""
        self.converter.start(cmd=self.get_conversion_cmd())

        assert self.converter.state() == QProcess.ProcessState.Starting
        self.converter.stop()

    def test_read_output(self) -> None:
        """Test Library.read_output()."""
        self.converter.start(cmd=self.get_conversion_cmd())
        assert self.converter.read_output()
        self.converter.stop()

    def test_catch_library_error_true(self) -> None:
        """Test _OutputReader.catch_library_error() -> true."""
        self.converter.reader.update_read(
            "Some random output with " "Unknown encoder error"
        )
        assert self.converter.reader.catch_library_error() == "Unknown encoder"

    def test_catch_library_error_false(self) -> None:
        """Test _OutputReader.catch_library_error() -> false."""
        self.converter.reader.update_read("Some random output with " "no error")
        assert self.converter.reader.catch_library_error() is None

    def test_stop(self) -> None:
        """Test Library.stop()."""
        self.converter.stop()
        assert not self.converter.is_running
