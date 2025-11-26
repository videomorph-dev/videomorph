"""This module defines the VideoMorph terminal options."""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from PyQt6.QtWidgets import QApplication

from videomorph.converter import APP_NAME, VALID_VIDEO_EXT, VERSION


def run_on_console(app: QApplication, main_win) -> None:
    """Provide options to run VideoMorph from the command line."""

    # Add a parser for command line
    parser = argparse.ArgumentParser(description=APP_NAME + " " + VERSION)

    # Add options for command line
    parser.add_argument(
        "-i",
        "--input-file",
        help="take the input_path to a video file(s) as input",
        action="store",
        nargs="*",
        dest="input_file",
    )

    parser.add_argument(
        "-d",
        "--input-dir",
        help="take a directory as input and find video " "files recursively",
        action="store",
        dest="input_dir",
    )

    # Process the command line input
    args = parser.parse_args()

    files = []

    if args.input_file:
        for file in args.input_file:
            try:
                path = Path(file)
                if path.exists() and path.is_file():
                    files.append(path.__str__())
                else:
                    print(
                        "Video file: {0}, doesn't exist".format(file),
                        file=sys.stderr,
                    )
            except (OSError, PermissionError) as e:
                print(
                    "Error accessing file {0}: {1}".format(file, e),
                    file=sys.stderr,
                )

    if args.input_dir:
        try:
            files = search_directory_recursively(
                directory=args.input_dir, files=files
            )
        except IsADirectoryError as error:
            print(error, file=sys.stderr)
        except FileNotFoundError as error:
            print(error, file=sys.stderr)

    if files:
        # Avoid duplicated files
        files_to_add = set(files)
        # Add files
        main_win.add_tasks(*files_to_add)
        main_win.show()
        main_win.start_encoding()
        sys.exit(app.exec())


def search_directory_recursively(
    directory: str, files: Optional[List[str]] = None
) -> List[str]:
    """Search a directory for video files."""
    if files is None:
        files = []

    dir_path = Path(directory)
    if not dir_path.is_dir():
        raise IsADirectoryError(
            "Directory: {0}, doesn't exist".format(directory)
        )

    for path in dir_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in VALID_VIDEO_EXT:
            files.append(path.__str__())

    if not files:
        raise FileNotFoundError(
            "No Video Files Found in: {0}".format(directory)
        )

    return files
