"""This module provides the definition of the Converter class."""

from pathlib import Path
from typing import Any, Optional, Union

from PyQt6.QtCore import QProcess

from videomorph.converter.launchers import launcher_factory
from videomorph.converter.paths import path_manager
from videomorph.converter.reader import OutputReader
from videomorph.converter.timer import ConversionTimer


class Converter:
    """Converter class."""

    def __init__(self, library_path=None) -> None:
        """Class initializer."""
        self._library_path = library_path or path_manager.library_path
        self._process = QProcess()
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.error: Optional[str] = None
        self.reader = OutputReader()
        self.timer = ConversionTimer()

    def setup(self, reader, finisher):
        """Set up the QProcess object."""
        self._process.readyRead.connect(reader)
        self._process.finished.connect(finisher)

    def start(self, cmd):
        """Start the encoding process."""
        self._process.start(self._library_path, cmd)

    def stop(self):
        """Terminate the encoding process."""
        self._process.terminate()
        if self.is_running:
            self._process.kill()

    def disconnect_finished(self, connected):
        """Disconnect the QProcess.finished method."""
        self._process.finished.disconnect(connected)

    def close(self):
        """Call QProcess.close method."""
        self._process.close()

    def kill(self):
        """Call QProcess.kill method."""
        self._process.kill()

    def state(self):
        """Call QProcess.state method."""
        return self._process.state()

    def exit_status(self):
        """Call QProcess.exit_status method."""
        return self._process.exitStatus()

    def read_output(self):
        """Call QProcess.readAll method."""
        return str(self._process.readAll())

    @property
    def is_running(self):
        """Return QProcess state."""
        return self._process.state() == QProcess.ProcessState.Running

    def catch_errors(self) -> None:
        """Catch the library error when running."""
        self.error = self.reader.catch_library_error()

    @staticmethod
    def run_player(file_path: Union[str, Path]) -> None:
        """Play a video file with user default player."""
        launcher = launcher_factory()
        launcher.open_with_user_app(url=file_path)
