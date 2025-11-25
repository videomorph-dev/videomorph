"""Tests for videomorph.converter.task."""

from pathlib import Path

from videomorph.converter.task import (
    _DELETE_RETRY_ATTEMPTS,
    Task,
)


class DummyProfile:
    """Minimal profile replacement for Task tests."""

    def __init__(self):
        self.extension = ".mp4"
        self.params = ""
        self.quality_tag = "[T]-"

    def update(self, new_quality=None):
        """No-op update used in tests."""
        return None


class DummyVideo:
    """Minimal video replacement for Task tests."""

    def __init__(self, video_path: Path):
        self.path = video_path
        self.format_info = {"duration": "1"}

    def get_name(self, with_extension=False):
        if with_extension:
            return self.path.name
        return self.path.stem


def _build_task(tmp_path):
    video_file = tmp_path / "input.mp4"
    video_file.write_text("video")
    return Task(
        video=DummyVideo(video_file),
        profile=DummyProfile(),
        output_dir=tmp_path,
    )


def test_delete_output_handles_missing_file(tmp_path):
    """delete_output should return True when output file is absent."""
    task = _build_task(tmp_path)

    # Ensure file does not exist
    output_path = task._get_output_path(tagged=False)
    if output_path.exists():
        output_path.unlink()

    # Should return True (file doesn't exist is considered success)
    result = task.delete_output(tagged=False)
    assert result is True


def test_delete_output_successfully_deletes_file(tmp_path):
    """delete_output should return True when file is successfully deleted."""
    task = _build_task(tmp_path)

    # Create the output file
    output_path = task._get_output_path(tagged=False)
    output_path.write_text("test output")
    assert output_path.exists()

    # Delete it
    result = task.delete_output(tagged=False)

    # Should return True and file should be gone
    assert result is True
    assert not output_path.exists()


def test_delete_output_stops_after_limited_retries(monkeypatch, tmp_path):
    """delete_output must not loop forever when a file is locked."""
    task = _build_task(tmp_path)

    class LockedPath:
        def __init__(self):
            self.attempts = 0

        def unlink(self):
            self.attempts += 1
            raise PermissionError("in use")

        def __str__(self):
            return "locked-file"

    locked_path = LockedPath()
    monkeypatch.setattr(
        task,
        "_get_output_path",
        lambda tagged: locked_path,
    )

    result = task.delete_output(tagged=False)

    # Verify it stops after retry attempts, not infinite loop
    assert locked_path.attempts == _DELETE_RETRY_ATTEMPTS
    # Should return False when deletion fails after retries
    assert result is False
