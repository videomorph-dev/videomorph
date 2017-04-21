# VideoMorph

[![Build Status](https://travis-ci.org/codeshard/videomorph.png?branch=master)](https://travis-ci.org/codeshard/videomorph)
[![codecov.io](https://codecov.io/github/codeshard/videomorph/coverage.svg?branch=master)](https://codecov.io/github/codeshard/videomorph?branch=master)

VideoMorph is a small GUI wrapper for [ffmpeg](http://ffmpeg.org),
based on code from [python-video-converter](https://github.com/senko/python-video-converter)
and presets idea from [QWinFF](http://qwinff.github.io) and
[FF Multi Converter](https://github.com/Ilias95/FF-Multi-Converter).

## Screenshot

![Screenshot](screenshot.png)

## Goal

Unlike other video converters, VideoMorph focuses on a single goal:
video conversion, making it simple, easy to use and allowing the user to convert
to the currently most popular video formats.

VideoMorph UI is simple and clean, focused on usability, eliminating annoying options rarely used.
VideoMorph is a video converter, just that. If you want a video editor,
VideoMorph isn't for you.

## Installation and requirements

To install the package:

    sudo python3 setup.py install # This does not install dependencies

    or:

    sudo install.sh # This does install dependencies

To install the .deb file

    use GDebi Packages Installer, just that...

This only installs VideoMorph. The [ffmpeg](http://ffmpeg.org) package should be installed
or compiled in your distribution.

## Acknowledgements

VideoMorph uses the following libraries and programs:

 - [Qt5](http://www.qt.io/qt5-4/)
 - [PyQt5](https://riverbankcomputing.com/software/pyqt/download5)
 - [FFmpeg](ffmpeg.org)

You should have installed these programs and libraries for the proper
functioning of VideoMorph.

## Contributing

Just clone the repo and make a pull request!

## Licensing and Patents

VideoMorph is licenced under Apache License Version 2.0, more info at [http://www.apache.org/licenses/](http://www.apache.org/licenses/)
Following the idea of [python-video-converter](https://github.com/senko/python-video-converter)
VideoMorph only uses the [ffmpeg](http://ffmpeg.org) binary, so, VideoMorph doesn't need to be licensed
under LGPL/GPL

## Authors and Copyright

Code & Artwork by:

 - [Ozkar L. Garcell](mailto:codeshard@openmailbox.org)
 - [Leodanis Pozo Ramos](mailto:lpozo@openmailbox.org)

Contributors:

 - [Maikel Llamaret Heredia](http://gutl.jovenclub.cu)
 - [Carlos Parra Zaldivar](http://libreoffice.cubava.cu)
