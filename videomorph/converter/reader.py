"""This module provides Output Reader."""

import re


class OutputReader:
    """Read the converter output."""

    def __init__(self):
        """Class initializer."""
        self._params_regex = {
            "bitrate": r"bitrate=[ ]*[0-9]*\.[0-9]*[a-z]*./[a-z]*",
            "time": r"time=([0-9.:]+) ",
        }
        self._library_errors = (
            "Unknown encoder",
            "Unrecognized option",
            "Invalid argument",
        )
        self._process_output = None

    def update_read(self, process_output):
        """Update the process output."""
        self._process_output = process_output

    def catch_library_error(self):
        """Process the library errors."""
        for error in self._library_errors:
            if error in self._process_output:
                return error

        return None

    @property
    def has_time_read(self):
        """Return the time read."""
        return self._read_output_param(param="time")

    @property
    def bitrate(self):
        """Return the bitrate read."""
        bitrate_read = self._read_output_param(param="bitrate")
        return bitrate_read[0].split("=")[-1].strip()

    @property
    def time(self):
        """Convert time read to seconds."""
        seconds = 0.0
        for time_part in self.has_time_read[0].split(":"):
            seconds = 60 * seconds + float(time_part)

        return seconds

    def _read_output_param(self, param):
        """Read library output looking for some parameters."""
        pattern = re.compile(self._params_regex[param])

        return pattern.findall(self._process_output)
