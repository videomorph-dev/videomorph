# -*- coding: utf-8 -*-

# File name: timer.py
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

"""This module provides Timer."""

from time import time

from .utils import write_time


class ConversionTimer:
    """Class to process Conversion progress times."""

    def __init__(self):
        """Class initializer."""
        self._time_jump = 0.0
        self._partial_time = 0.0
        self._total_time = 0.0

        self._operation_time_read = 0.0

        self.process_start_time = 0.0
        self.process_cum_time = 0.0
        self.operation_start_time = 0.0
        self.operation_cum_time = 0.0

    def update_time(self, op_time_read_sec):
        """Update ConversionTimer with operation time read from conversion."""
        self._operation_time_read = op_time_read_sec

    def init_process_start_time(self):
        """Initialize process start time."""
        self.process_start_time = time()

    def init_operation_start_time(self):
        """Initialize the operation time"""
        self.operation_start_time = time()

    def reset_progress_times(self):
        """Reset the variables used to calculate progress."""
        self._time_jump = 0.0
        self._partial_time = 0.0
        self._total_time = 0.0
        self.operation_start_time = 0.0

    def operation_progress(self, file_duration):
        """Return the operation progress percentage."""
        return int(self._operation_time_read / file_duration * 100)

    def process_progress(self, list_duration):
        """"Calculate total progress percentage."""
        if self._partial_time > self._operation_time_read:
            self._time_jump += self._partial_time

        self._total_time = self._time_jump + self._operation_time_read
        self._partial_time = self._operation_time_read

        return int(self._total_time / float(list_duration) * 100)

    def operation_remaining_time(self, file_duration):
        """Return the operation remaining time."""
        op_time = self._operation_time(file_duration=file_duration)
        # Avoid negative time
        try:
            op_remaining_time = write_time(op_time - self.operation_cum_time)
        except ValueError:
            op_remaining_time = write_time(0)

        return op_remaining_time

    def update_cum_times(self):
        """Real time computation."""
        sys_time = time()
        self.operation_cum_time = sys_time - self.operation_start_time
        self.process_cum_time = sys_time - self.process_start_time

    def _operation_time(self, file_duration):
        """Estimating operation time."""
        speed = self.operation_cum_time / self._operation_time_read

        return file_duration * speed
