"""This module provides the definition of TaskList and Video classes."""

from collections import deque
from pathlib import Path
from typing import Deque, List, Optional, Union

from videomorph.converter.constants import STATUS
from videomorph.converter.profile import Profile
from videomorph.converter.task import Task
from videomorph.converter.video import Video


class TaskList(list):
    """Class to store the list of video files to convert."""

    def __init__(
        self, profile: Profile, output_dir: Union[str, Path] = Path.home()
    ) -> None:
        """Class initializer."""
        super(TaskList, self).__init__()
        self._profile = profile
        self._position: Optional[int] = None
        self.not_added_files: Deque[Union[str, Path]] = deque()
        self._output_dir = Path(output_dir)
        self._task_paths: set = set()  # Cache for O(1) lookup

    @property
    def output_dir(self) -> Path:
        return self._output_dir

    @output_dir.setter
    def output_dir(self, value: Union[str, Path]) -> None:
        self._output_dir = Path(value)
        for task in self:
            task.output_dir = self._output_dir

    def clear(self) -> None:
        """Clear the list of videos."""
        super(TaskList, self).clear()
        self._task_paths.clear()
        self.position = None

    def add_task(self, video_path: Union[str, Path]) -> bool:
        """Add a task to the task list.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            True if task was added successfully, False otherwise
        """
        video_path_str = str(video_path)
        if video_path_str in self._task_paths:
            return False  # Already added
            
        video = Video(video_path=video_path)
        if video.is_valid():
            self.append(Task(video, self._profile, self.output_dir))
            self._task_paths.add(video_path_str)
            return True

        self.not_added_files.append(video_path)
        return False

    def remove_task(self, position: int) -> None:
        """Remove a task from the list.
        
        Args:
            position: Index of the task to remove
            
        Raises:
            IndexError: If position is out of bounds
        """
        if position < 0 or position >= len(self):
            raise IndexError(f"Task position {position} out of range")
        
        task = self[position]
        self._task_paths.discard(str(task.video.path))
        del self[position]

    def get_task(self, position: int) -> Task:
        """Return a file object."""
        return self[position]

    def get_file_name(
        self, position: int, with_extension: bool = False
    ) -> str:
        """Return the name of a video file."""
        return self[position].video.get_name(with_extension)

    def get_file_path(self, position: int) -> Path:
        """Return the input_path to a video file."""
        return self[position].video.path

    def get_task_status(self, position: int) -> str:
        """Return the video file conversion status."""
        return self[position].status

    def set_task_status(self, position: int, status: str) -> None:
        """Set the video file conversion status."""
        self[position].status = status

    def get_file_info(self, position: int, info_param: str) -> str:
        """Return general streaming info from a video file."""
        return self[position].video.format_info[info_param]

    def running_file_name(self, with_extension: bool = True) -> str:
        """Return the running file name."""
        return self._running_task.video.get_name(with_extension)

    def running_file_info(self, info_param: str) -> str:
        """Return running file info."""
        return self._running_task.video.format_info[info_param]

    @property
    def running_task_status(self) -> str:
        """Return file status."""
        return self._running_task.status

    @running_task_status.setter
    def running_task_status(self, status: str) -> None:
        """Set file status."""
        self._running_task.status = status

    def running_task_conversion_cmd(
        self,
        target_quality: str,
        tagged: bool,
        subtitle: bool,
        replace_source: bool = False,
    ) -> List[str]:
        """Return the conversion command."""
        return self._running_task.build_conversion_cmd(
            target_quality,
            tagged,
            subtitle,
            replace_source=replace_source,
        )

    def running_file_output_name(self, tagged: bool) -> str:
        """Return the output name."""
        return self._running_task.get_output_file_name(tagged)

    def delete_running_file_output(self, tagged: bool) -> bool:
        """Delete output file.
        
        Returns:
            True if file was deleted or didn't exist, False if deletion failed.
        """
        return self._running_task.delete_output(tagged)

    def delete_running_file_input(self) -> None:
        """Delete input file."""
        self._running_task.delete_input()

    def finalize_running_task_output(self) -> None:
        """Finalize output when a temporary file was used."""
        self._running_task.finalize_output()

    @property
    def position(self) -> Optional[int]:
        """Get the current task position.
        
        Returns:
            Current position or None if not set
        """
        return self._position

    @position.setter
    def position(self, value: Optional[int]) -> None:
        """Set the current task position.
        
        Args:
            value: Position to set, or None to unset
        """
        self._position = value

    @property
    def is_exhausted(self) -> bool:
        """Return True if all files in media list are processed."""
        if self._position is None:
            return False
        return self._position + 1 >= len(self)

    @property
    def all_stopped(self) -> bool:
        """Check if all files in the lists have been stopped."""
        for task in self:
            if task.status != STATUS.stopped:
                return False
        return True

    @property
    def all_done(self) -> bool:
        """Check if all files in the lists have been done."""
        for task in self:
            if task.status != STATUS.done:
                return False
        return True

    def duration(self, step: int = 1) -> float:
        """Return the duration time of TaskList counting files to do only."""
        if self._position is not None and self._position >= 0:
            tasks = self[self._position + step :]
            return sum(
                float(task.video.format_info["duration"])
                for task in tasks
                if task.status != STATUS.done
            )

        return sum(
            float(task.video.format_info["duration"])
            for task in self
            if task.status != STATUS.done
        )

    def __contains__(self, file_path: Union[str, Path]) -> bool:
        """Check if a file path is already in the task list.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if path is in the list, False otherwise
        """
        return str(file_path) in self._task_paths

    @property
    def _running_task(self) -> Task:
        """Return the task that is currently running.
        
        Raises:
            ValueError: If no task is currently running
        """
        if self._position is None:
            raise ValueError("No task is currently running")
        return self[self._position]
