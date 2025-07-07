"""This module provides tests for media.py module."""

import pytest

from videomorph.converter import STATUS
from videomorph.converter.library import Library
from videomorph.converter.profile import Profile
from videomorph.converter.task import Task
from videomorph.converter.tasklist import TaskList


class TestMedia:
    """Class for testing media.py module."""

    @pytest.fixture
    def conv_lib(self):
        """Library fixture."""
        return Library()

    @pytest.fixture
    def profile(self):
        """Profile fixture."""
        profile = Profile()
        profile.update(new_quality="MP4 High Quality")
        return profile

    @pytest.fixture
    def media_list(self, profile):
        """Media list fixture."""
        media_list = TaskList(profile=profile)
        # Use the sample video file that exists
        success = media_list.add_task("sample-video.mp4")
        assert success, "Failed to add sample video to task list"
        return media_list

    def test_add_task(self, media_list):
        """Test TaskList.add_task()."""
        assert len(media_list) == 1
        assert (
            media_list.get_file_name(0, with_extension=True)
            == "sample-video.mp4"
        )

    def test_delete_file(self, media_list):
        """Test TaskList.delete_file()."""
        # Be sure there is one element in the list
        assert media_list
        media_list.delete_file(position=0)
        assert not media_list

    def test_get_file_object(self, media_list):
        """Test TaskList.get_task()."""
        assert isinstance(media_list.get_task(0), Task)

    def test_get_file_name(self, media_list):
        """Test TaskList.get_file_name()."""
        assert media_list.get_file_name(0) == "sample-video.mp4"

    def test_get_file_name_with_extension(self, media_list):
        """Test TaskList.get_file_name() with extension."""
        assert (
            media_list.get_file_name(0, with_extension=True)
            == "sample-video.mp4"
        )

    def test_get_file_path(self, media_list):
        """Test TaskList.get_file_path()."""
        path = media_list.get_file_path(0)
        assert path.name == "sample-video.mp4"

    def test_get_task_status(self, media_list):
        """Test TaskList.get_task_status()."""
        assert media_list.get_task_status(0) == STATUS.todo

    def test_set_task_status(self, media_list):
        """Test TaskList.set_task_status()."""
        media_list.set_task_status(0, STATUS.done)
        assert media_list.get_task_status(0) == STATUS.done

    def test_get_file_info(self, media_list):
        """Test TaskList.get_file_info()."""
        duration = media_list.get_file_info(0, "duration")
        assert duration is not None

    def test_clear(self, media_list):
        """Test TaskList.clear()."""
        media_list.clear()
        assert not media_list

    def test_output_dir_property(self, profile):
        """Test TaskList output_dir property."""
        media_list = TaskList(profile=profile)
        original_dir = media_list.output_dir
        media_list.output_dir = "/tmp"
        assert media_list.output_dir.name == "tmp"
        # Reset to original
        media_list.output_dir = original_dir

    def test_build_conversion_cmd(self, media_list):
        """Test Task.build_conversion_cmd."""
        cmd = media_list.get_task(0).build_conversion_cmd(
            tagged=True,
            subtitle=False,
            target_quality="MP4 High Quality",
        )
        assert isinstance(cmd, list)
        assert len(cmd) > 0
        assert "-i" in cmd
        assert "sample-video.mp4" in cmd[cmd.index("-i") + 1]

    def test_running_task_conversion_cmd(self, media_list):
        """Test TaskList.running_task_conversion_cmd()."""
        # Set position to first task
        media_list._position = 0
        cmd = media_list.running_task_conversion_cmd(
            tagged=True,
            subtitle=False,
            target_quality="MP4 High Quality",
        )
        assert isinstance(cmd, list)
        assert len(cmd) > 0
        assert "-i" in cmd
