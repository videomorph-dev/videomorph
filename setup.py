"""This module defines the installation script for VideoMorph."""

from pathlib import Path
from sys import platform

from videomorph.converter.constants import __app_name__, __version__
from videomorph.converter.vmpath import SYS_PATHS, VM_PATHS

try:
    from setuptools import setup

    USE_DISTUTILS = False
except ImportError:
    from distutils.core import setup

    USE_DISTUTILS = True


LONG_DESCRIPTION = """Video Converter based on ffmpeg, Python 3 and PyQt6.
Unlike other video converters, VideoMorph focuses on a single goal:
make video conversion simple, with an easy to use GUI and allowing
the user to convert to the currently most popular video formats.
.
VideoMorph GUI is simple and clean, focused on usability, eliminating
annoying options rarely used.
VideoMorph is a video converter, just that. If you want a video editor,
VideoMorph isn't for you."""

COMMONS = dict(
    name=__app_name__.lower(),
    version=__version__,
    description="Video Converter based on ffmpeg, Python, and Qt6.",
    long_description=LONG_DESCRIPTION,
    author="Ozkar L. Garcell",
    author_email="ozkar.garcell@gmail.com",
    maintainer="Leodanis Pozo Ramos",
    maintainer_email="lpozor78@gmail.com",
    url="https://github.com/videomorph-dev/videomorph",
    license="Apache License, Version 2.0",
    packages=["videomorph", "videomorph.converter", "videomorph.forms"],
    platforms=["linux", "darwin", "win32"],
    keywords="multimedia, video conversion, common video formats",
)

COMMONS_SETUPTOOLS = dict(
    entry_points={"gui_scripts": ["videomorph = videomorph.main:main"]}
)


LINUX_DATA_FILES = dict(
    data_files=[  # Desktop entry
        (
            SYS_PATHS["apps"].__str__(),
            [Path(VM_PATHS["apps"], "videomorph.desktop").__str__()],
        ),
        # App icon
        (
            SYS_PATHS["icons"].__str__(),
            [Path(VM_PATHS["icons"], "videomorph.png").__str__()],
        ),
        # App sounds
        (
            SYS_PATHS["sounds"].__str__(),
            [Path(VM_PATHS["sounds"], "successful.wav").__str__()],
        ),
        # App translation file
        (
            SYS_PATHS["i18n"].__str__(),
            [Path(VM_PATHS["i18n"], "videomorph_es.qm").__str__()],
        ),
        # Default conversion profiles
        (
            SYS_PATHS["profiles"].__str__(),
            [
                Path(VM_PATHS["profiles"], "default.json").__str__(),
                Path(VM_PATHS["profiles"], "customized.json").__str__(),
            ],
        ),
        # Documentation files
        (
            SYS_PATHS["doc"].__str__(),
            [
                "README.md",
                "LICENSE",
                "requirements.txt",
                "copyright",
                "changelog.gz",
                "TODO",
                "screenshot.png",
            ],
        ),
        # User's manual
        (
            SYS_PATHS["help"].__str__(),
            [
                Path(VM_PATHS["help"], "manual_es.pdf").__str__(),
                Path(VM_PATHS["help"], "manual_en.pdf").__str__(),
            ],
        ),
        # Man page
        (
            SYS_PATHS["man"].__str__(),
            [Path(VM_PATHS["man"], "videomorph.1.gz").__str__()],
        ),
    ]
)

LINUX_DISTUTILS = dict(scripts=[Path(VM_PATHS["bin"], "videomorph").__str__()])

DARWIN_DATA_FILES = LINUX_DATA_FILES

DARWIN_DISTUTILS = LINUX_DISTUTILS

WIN32_DATA_FILES = dict(
    data_files=[  # App icon
        (
            SYS_PATHS["icons"].__str__(),
            [Path(VM_PATHS["icons"], "videomorph.ico").__str__()],
        ),
        # App sounds
        (
            SYS_PATHS["sounds"].__str__(),
            [Path(VM_PATHS["sounds"], "successful.wav").__str__()],
        ),
        # App translation file
        (
            SYS_PATHS["i18n"].__str__(),
            [Path(VM_PATHS["i18n"], "videomorph_es.qm").__str__()],
        ),
        # Default conversion profiles
        (
            SYS_PATHS["profiles"].__str__(),
            [
                Path(VM_PATHS["profiles"], "default.json").__str__(),
                Path(VM_PATHS["profiles"], "customized.json").__str__(),
            ],
        ),
        # Documentation files
        (
            SYS_PATHS["doc"].__str__(),
            [
                "README.md",
                "LICENSE",
                "requirements.txt",
                "copyright",
                "changelog.gz",
                "TODO",
                "screenshot.png",
            ],
        ),
        # User's manual
        (
            SYS_PATHS["help"].__str__(),
            [
                Path(VM_PATHS["help"], "manual_es.pdf").__str__(),
                Path(VM_PATHS["help"], "manual_en.pdf").__str__(),
            ],
        ),
    ]
)


SETUP_PARAMS = COMMONS

if platform == "linux":
    SETUP_PARAMS.update(LINUX_DATA_FILES)
    if USE_DISTUTILS:
        SETUP_PARAMS.update(LINUX_DISTUTILS)
    else:
        SETUP_PARAMS.update(COMMONS_SETUPTOOLS)
elif platform == "darwin":
    SETUP_PARAMS.update(DARWIN_DATA_FILES)
    if USE_DISTUTILS:
        SETUP_PARAMS.update(DARWIN_DISTUTILS)
    else:
        SETUP_PARAMS.update(COMMONS_SETUPTOOLS)
elif platform == "win32":
    SETUP_PARAMS.update(WIN32_DATA_FILES)
    if not USE_DISTUTILS:
        SETUP_PARAMS.update(COMMONS_SETUPTOOLS)


if __name__ == "__main__":
    setup(**SETUP_PARAMS)
