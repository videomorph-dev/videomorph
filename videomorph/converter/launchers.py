"""This module provides classes for handing platform dependent stuffs."""

import os
import webbrowser
from pathlib import Path
from subprocess import PIPE, Popen
from sys import platform
from typing import Any, Optional, Type


def get_all_subclasses(cls):
    """Get all subclasses recursively."""
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))
    return all_subclasses


def generic_factory(parent_class: Type[Any]) -> Any:
    """Generic factory function."""
    platform_map = {
        "darwin": "_darwin",
        "linux": "_linux",
        "linux2": "_linux",
        "win32": "_win32",
    }

    # Get all subclasses recursively
    all_subclasses = get_all_subclasses(parent_class)

    # Try exact platform match first
    platform_pattern = platform_map.get(platform)
    if platform_pattern:
        for concrete_class in all_subclasses:
            class_name_lower = concrete_class.__name__.lower()
            if class_name_lower.startswith(platform_pattern):
                return concrete_class()

    # Fall back to checking if platform starts with linux
    if platform.startswith("linux"):
        for concrete_class in all_subclasses:
            class_name_lower = concrete_class.__name__.lower()
            if class_name_lower.startswith("_linux"):
                return concrete_class()

    raise ValueError("No implementation available for {0}".format(platform))


class _Launcher:
    """Abstract class to implement external apps launcher."""

    def __init__(self) -> None:
        self.players = None

    def open_with_user_app(self, url: str) -> None:
        """Open a file or url with user's preferred app."""
        raise NotImplementedError("Must be implemented in subclasses")

    @staticmethod
    def open_with_user_browser(url: str) -> None:
        """Open a web page with default browser."""
        webbrowser.open(url)

    def shutdown_machine(self) -> None:
        """Shutdown computer."""
        raise NotImplementedError("Must be implemented in subclasses")

    def sound_notify(self, sound: Optional[str] = None) -> None:
        """Show system notification."""
        raise NotImplementedError("Must be implemented in subclasses")


class _UnixLauncher(_Launcher):
    """Concrete class to implement external apps launcher in Unix-like systems."""

    def __init__(self):
        super(_UnixLauncher, self).__init__()
        self.players = [
            "vlc",
            "mpv",
            "mplayer",
            "ffplay",
        ]

    def open_with_user_app(self, url):
        """Open a file or url with user's preferred app."""
        if platform == "darwin":
            # Use macOS native 'open' command
            spawn_process(["open", url])
        else:
            opener = self._which("xdg-open")
            if opener is not None:
                spawn_process([opener, url])
            else:
                player = self._get_player()
                resolved_player = self._which(player)
                if resolved_player is None:
                    raise FileNotFoundError("Player not found")
                spawn_process([resolved_player, url])

    def _get_player(self):
        """Return a player from a list of popular players."""
        for player in self.players:
            if self._which(player) is not None:
                return player

        raise FileNotFoundError("Player not found")

    def shutdown_machine(self):
        """Shutdown computer."""
        if platform == "darwin":
            # Use AppleScript for macOS - will show GUI authentication dialog
            spawn_process(
                ["osascript", "-e", 'tell application "System Events" to shut down']
            )
        else:
            spawn_process(["shutdown", "now"])

    def sound_notify(self, sound=None):
        """Show system notification."""

        def _get_ffplay_command(sound_file):
            base_cmd = [
                "ffplay",
                "-nodisp",
                "-autoexit",
                "-loglevel",
                "quiet",
            ]

            if sound_file and sound_file.strip():
                return base_cmd + [sound_file]
            else:
                return base_cmd + [
                    "-f",
                    "lavfi",
                    "-i",
                    "sine=frequency=800:duration=0.3",
                ]

        if self._which("ffplay") is not None:
            import subprocess

            cmd = _get_ffplay_command(sound)
            try:
                subprocess.run(cmd, check=False, timeout=10)
                return
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        # Fallback to platform-specific players
        if platform == "darwin":
            spawn_process(["osascript", "-e", "beep"])
        else:
            spawn_process(["echo", "-e", "\\a"])

    @staticmethod
    def _which(app: str) -> str | None:
        """Resolve the absolute path for an executable in PATH."""
        if not app or not app.strip():
            return None

        sys_paths = os.environ.get("PATH", os.defpath).split(os.pathsep)
        for path in sys_paths:
            try:
                candidate = Path(path, app)
                if candidate.exists() and candidate.is_file():
                    return str(candidate)
            except (OSError, PermissionError):
                continue
        return None


class _LinuxLauncher(_UnixLauncher):
    """Linux launcher (inherits from Unix)."""

    pass


class _DarwinLauncher(_UnixLauncher):
    """macOS launcher (inherits from Unix)."""

    pass


class _Win32Launcher(_Launcher):
    """Concrete class to implement external apps launcher in Windows."""

    def open_with_user_app(self, url):
        """Open a file or url with user's preferred app."""
        import os

        os.startfile(url)

    def shutdown_machine(self):
        """Shutdown computer."""
        spawn_process(["shutdown", "/s"])

    def sound_notify(self, sound=None):
        """Show system notification."""
        try:
            from winsound import MB_OK, PlaySound

            PlaySound(sound, MB_OK)
        except ImportError:
            pass  # winsound not available


def launcher_factory():
    """Factory method to create the appropriate launcher."""
    return generic_factory(parent_class=_Launcher)


def spawn_process(cmd):
    """Launch a process with platform-appropriate settings."""
    if platform == "win32":
        try:
            import subprocess

            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags = subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            return Popen(
                cmd,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                shell=True,
                startupinfo=startupinfo,
                universal_newlines=True,
            )
        except AttributeError:
            # Fallback for platforms without Windows-specific subprocess attributes
            return Popen(
                cmd,
                stdin=PIPE,
                stdout=PIPE,
                stderr=PIPE,
                shell=True,
                universal_newlines=True,
            )
    else:  # Unix-like systems (Linux, macOS)
        return Popen(
            cmd,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True,
        )
