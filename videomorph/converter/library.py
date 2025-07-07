"""This module provides the definition of the Library class."""

from pathlib import Path
from typing import Any, Optional, Union

from .converter import Converter
from .launchers import launcher_factory
from .reader import OutputReader
from .timer import ConversionTimer


class Library:
    """Conversion Library class."""

    def __init__(self) -> None:
        """Class initializer."""
        self._converter = Converter()
        self.error: Optional[str] = None
        self.reader = OutputReader()
        self.timer = ConversionTimer()

    def __getattr__(self, attr: str) -> Any:
        """Delegate to use instance member objects."""
        return getattr(self._converter, attr)

    def catch_errors(self) -> None:
        """Catch the library error when running."""
        self.error = self.reader.catch_library_error()

    @staticmethod
    def run_player(file_path: Union[str, Path]) -> None:
        """Play a video file with user default player."""
        launcher = launcher_factory()
        launcher.open_with_user_app(url=file_path)
