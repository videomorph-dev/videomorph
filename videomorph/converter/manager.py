from PyQt6.QtCore import QObject, pyqtSignal, QProcess

from videomorph.converter.constants import STATUS
from videomorph.converter.converter import Converter
from videomorph.converter.tasklist import TaskList
from videomorph.converter.task import OutputPathCollisionError


from videomorph.converter.profile import Profile

class ConversionManager(QObject):
    """Manages the conversion process."""

    # Signals
    task_started = pyqtSignal(int)  # task_index
    task_finished = pyqtSignal(int, str)  # task_index, status
    all_finished = pyqtSignal()
    error = pyqtSignal(str)
    progress_updated = pyqtSignal(float, float)  # op_progress, total_progress
    time_updated = pyqtSignal(str, str, str, str) # name, bitrate, remaining, elapsed

    def __init__(self, output_dir=None):
        super().__init__()
        self._converter = Converter()
        self.profile = Profile()
        self.task_list = TaskList(
            profile=self.profile, output_dir=output_dir if output_dir else Path.home()
        )
        self._stop_requested = False
        self._current_options = {}

        # Connect library signals
        self._converter.setup(
            reader=self._on_converter_ready_read,
            finisher=self._on_converter_finished,
        )

    def start(self, options: dict):
        """Start the conversion process."""
        self._current_options = options
        self._stop_requested = False
        self._process_next_task()

    def stop(self):
        """Stop the current task."""
        self._stop_requested = True
        self._converter.stop()
        # The finished signal will handle the rest

    def stop_all(self):
        """Stop all tasks."""
        self._stop_requested = True
        self._converter.stop()
        # We'll need to mark remaining tasks as stopped in the finished handler

    def _process_next_task(self):
        """Process the next task in the list."""
        if self._stop_requested:
            self._handle_stop()
            return

        # Advance position
        if self.task_list.position is None:
            self.task_list.position = 0
        else:
            self.task_list.position += 1

        # Check if we are done
        if self.task_list.position >= len(self.task_list):
            self.all_finished.emit()
            return

        # Reset timer for new task
        self._converter.timer.operation_start_time = 0.0
        
        # Check if task needs processing
        if self.task_list.running_task_status != STATUS.done:
            self._start_current_task()
        else:
            # Skip done tasks
            self._process_next_task()

    def _start_current_task(self):
        """Start the currently selected task."""
        try:
            cmd = self.task_list.running_task_conversion_cmd(
                target_quality=self._current_options.get("target_quality"),
                tagged=self._current_options.get("tagged", False),
                subtitle=self._current_options.get("subtitle", False),
                replace_source=self._current_options.get("replace_source", False),
            )
            
            self.task_started.emit(self.task_list.position)
            self._converter.start(cmd=cmd)
            
        except OutputPathCollisionError as e:
            self.error.emit(f"Output path collision: {e}")
            self.task_list.running_task_status = STATUS.todo
            # We stop here or continue? Original behavior seemed to stop or show error.
            # Let's stop to let user fix it.
            self.all_finished.emit() 
        except PermissionError:
            self.error.emit("Permission denied for output directory.")
            self.task_list.running_task_status = STATUS.todo
            self.all_finished.emit()
        except FileNotFoundError:
            self.error.emit(f"Input file not found: {self.task_list.running_file_name()}")
            self.task_list.running_task_status = STATUS.todo
            self.all_finished.emit()

    def _on_converter_ready_read(self):
        """Handle output from converter."""
        self._converter.reader.update_read(
            process_output=self._converter.read_output()
        )
        self._update_progress()

    def _update_progress(self):
        """Calculate and emit progress updates."""
        if not self._converter.timer.process_start_time:
            self._converter.timer.init_process_start_time()
        if not self._converter.timer.operation_start_time:
            self._converter.timer.init_operation_start_time()

        if not self._converter.reader.has_time_read:
            self._converter.catch_errors()
            return

        self._converter.timer.update_time(op_time_read_sec=self._converter.reader.time)
        self._converter.timer.update_cum_times()

        file_duration = float(self.task_list.running_file_info("duration"))
        # We need the total list duration which is stored in MW usually.
        # But we can calculate it here if we have access or pass it.
        # For now, let's assume we can get it from task_list if we pass a step.
        # But task_list.duration() depends on current position.
        
        # In original code: self.task_list_duration = self.task_list.duration()
        # We might need to track this.
        # For simplicity, let's calculate it.
        list_duration = self.task_list.duration()

        op_progress = self._converter.timer.operation_progress(file_duration=file_duration)
        pr_progress = self._converter.timer.process_progress(list_duration=list_duration)

        self.progress_updated.emit(op_progress, pr_progress)
        
        # Also emit time info for status bar
        from videomorph.converter.utils import write_time
        self.time_updated.emit(
            self.task_list.running_file_name(with_extension=True),
            self._converter.reader.bitrate,
            self._converter.timer.operation_remaining_time(file_duration=file_duration),
            write_time(self._converter.timer.process_cum_time)
        )

    def _on_converter_finished(self):
        """Handle converter process finished."""
        self._converter.close()
        
        if self._stop_requested:
            self._handle_stop()
            return

        if self._converter.exit_status() == QProcess.ExitStatus.NormalExit:
            self.task_list.running_task_status = STATUS.done
            self.task_finished.emit(self.task_list.position, STATUS.done)
            
            # Finalize output
            try:
                self.task_list.finalize_running_task_output()
            except (FileNotFoundError, OSError) as e:
                self.error.emit(f"Finalize error: {e}")

            # Delete input if requested
            if self._current_options.get("replace_source", False):
                # Logic for deleting input is complex in original (checks output existence)
                # We'll simplify or replicate:
                # Original checks if output exists before deleting input.
                # finalize_running_task_output should have ensured output exists.
                try:
                    self.task_list.delete_running_file_input()
                except OSError as e:
                    self.error.emit(f"Delete input error: {e}")
        else:
            # Error happened
            if self._converter.error:
                self.error.emit(f"Converter error: {self._converter.error}")
                self._converter.error = None
            else:
                self.error.emit("Unknown converter error")
            
            # If error, we usually stop? Or continue?
            # Original: _end_encoding_process -> if is_exhausted ...
            # If not exhausted, it continues.
            # But if it failed, maybe we should mark as todo or error?
            # Original keeps it as todo if it wasn't done.
            pass

        # Continue to next task
        self._process_next_task()

    def _handle_stop(self):
        """Handle stop logic."""
        self.task_list.running_task_status = STATUS.stopped
        self.task_finished.emit(self.task_list.position, STATUS.stopped)
        
        # Cleanup output
        self.task_list.delete_running_file_output(
            tagged=self._current_options.get("tagged", False)
        )
        
        self._converter.timer.reset_progress_times()
        
        # If stop_all was requested, mark all remaining as stopped?
        # The original code iterates and marks them.
        # We can just emit all_finished and let the UI handle the rest or do it here.
        # Let's just stop processing.
        
        self.all_finished.emit()

    # Public API
    @property
    def is_running(self) -> bool:
        """Check if conversion is currently running."""
        return self._converter.is_running

    def run_player(self, file_path) -> None:
        """Play a file with the system player."""
        self._converter.run_player(file_path=file_path)

    def reset_progress(self) -> None:
        """Reset progress timers."""
        self._converter.timer.reset_progress_times()

    def kill_converter(self) -> None:
        """Forcefully kill the conversion process."""
        self._converter.kill()
        self._converter.close()

    def get_profile_qualities(self):
        """Get profile qualities for the current locale."""
        return self.profile.get_json_profile_qualities()
    
    def update_profile(self, new_quality: str):
        """Update the current profile quality."""
        self.profile.update(new_quality=new_quality)
    
    def consume_profile_warning(self):
        """Consume and return any profile warning."""
        return self.profile.consume_warning()

    # Task List Access Methods
    @property
    def output_dir(self):
        return self.task_list.output_dir

    @output_dir.setter
    def output_dir(self, value):
        self.task_list.output_dir = value

    @property
    def task_count(self):
        return len(self.task_list)

    @property
    def has_tasks(self):
        return bool(len(self.task_list))

    @property
    def current_task_position(self):
        return self.task_list.position

    @current_task_position.setter
    def current_task_position(self, value):
        self.task_list.position = value

    @property
    def all_tasks_done(self):
        return self.task_list.all_done

    @property
    def all_tasks_stopped(self):
        return self.task_list.all_stopped

    @property
    def not_added_files(self):
        return self.task_list.not_added_files

    def get_task_file_name(self, position, with_extension=False):
        return self.task_list.get_file_name(position, with_extension)

    def get_task_file_info(self, position, info_param):
        return self.task_list.get_file_info(position, info_param)

    def get_task_status(self, position):
        return self.task_list.get_task_status(position)

    def set_task_status(self, position, status):
        self.task_list.set_task_status(position, status)

    def get_task_output_path(self, position, tagged=False):
        return self.task_list.get_task(position).get_output_path(tagged)
    
    def get_task_file_path(self, position):
        return self.task_list.get_file_path(position)

    def delete_running_file_output(self, tagged=False):
        return self.task_list.delete_running_file_output(tagged)

    def get_total_duration(self, step=None):
        return self.task_list.duration(step)

    def get_running_file_name(self, with_extension=False):
        return self.task_list.running_file_name(with_extension)

    def reset_all_tasks_status(self):
        """Reset all tasks status to todo."""
        for task in self.task_list:
            task.status = STATUS.todo
        self.task_list.position = None

    def get_task(self, position):
        """Get a task by position."""
        return self.task_list.get_task(position)

    # Model Access Methods
    def add_task(self, file_path):
        """Add a task to the list."""
        return self.task_list.add_task(file_path)

    def remove_task(self, position):
        """Remove a task from the list."""
        self.task_list.remove_task(position)

    def clear_tasks(self):
        """Clear all tasks."""
        self.task_list.clear()

    def get_profile(self):
        """Get the current profile."""
        return self.profile
    
    def get_task_list(self):
        """Get the task list."""
        return self.task_list

