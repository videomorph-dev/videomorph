"""This module defines the installation script for VideoMorph."""

from pathlib import Path
from sys import platform

from videomorph import __app_name__, __version__
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
        (str(SYS_PATHS["apps"]), [str(Path(VM_PATHS["apps"], "videomorph.desktop"))]),
        # App icon
        (str(SYS_PATHS["icons"]), [str(Path(VM_PATHS["icons"], "videomorph.png"))]),
        # App sounds
        (str(SYS_PATHS["sounds"]), [str(Path(VM_PATHS["sounds"], "successful.wav"))]),
        # App translation file
        (str(SYS_PATHS["i18n"]), [str(Path(VM_PATHS["i18n"], "videomorph_es.qm"))]),
        # Default conversion profiles
        (
            str(SYS_PATHS["profiles"]),
            [
                str(Path(VM_PATHS["profiles"], "default.json")),
                str(Path(VM_PATHS["profiles"], "customized.json")),
            ],
        ),
        # Documentation files
        (
            str(SYS_PATHS["doc"]),
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
            str(SYS_PATHS["help"]),
            [
                str(Path(VM_PATHS["help"], "manual_es.pdf")),
                str(Path(VM_PATHS["help"], "manual_en.pdf")),
            ],
        ),
        # Man page
        (str(SYS_PATHS["man"]), [str(Path(VM_PATHS["man"], "videomorph.1.gz"))]),
    ]
)

LINUX_DISTUTILS = dict(scripts=[str(Path(VM_PATHS["bin"], "videomorph"))])

DARWIN_DATA_FILES = LINUX_DATA_FILES

DARWIN_DISTUTILS = LINUX_DISTUTILS

WIN32_DATA_FILES = dict(
    data_files=[  # App icon
        (str(SYS_PATHS["icons"]), [str(Path(VM_PATHS["icons"], "videomorph.ico"))]),
        # App sounds
        (str(SYS_PATHS["sounds"]), [str(Path(VM_PATHS["sounds"], "successful.wav"))]),
        # App translation file
        (str(SYS_PATHS["i18n"]), [str(Path(VM_PATHS["i18n"], "videomorph_es.qm"))]),
        # Default conversion profiles
        (
            str(SYS_PATHS["profiles"]),
            [
                str(Path(VM_PATHS["profiles"], "default.json")),
                str(Path(VM_PATHS["profiles"], "customized.json")),
            ],
        ),
        # Documentation files
        (
            str(SYS_PATHS["doc"]),
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
            str(SYS_PATHS["help"]),
            [
                str(Path(VM_PATHS["help"], "manual_es.pdf")),
                str(Path(VM_PATHS["help"], "manual_en.pdf")),
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
