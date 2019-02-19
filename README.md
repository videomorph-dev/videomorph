# VideoMorph

[![Open Source Love](https://badges.frapsoft.com/os/v2/open-source.svg?v=102)](https://github.com/ellerbrock/open-source-badge/)
[![Build Status](https://travis-ci.org/videomorph-dev/videomorph.png?branch=master)](https://travis-ci.org/videomorph-dev/videomorph)
[![codecov](https://codecov.io/gh/videomorph-dev/videomorph/branch/master/graph/badge.svg)](https://codecov.io/gh/videomorph-dev/videomorph)
[![Maintainability](https://api.codeclimate.com/v1/badges/5f6cd3f7c20bccee2065/maintainability)](https://codeclimate.com/github/videomorph-dev/videomorph/maintainability)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/videomorph-dev/videomorph/pulls)

VideoMorph is a GUI wrapper for [ffmpeg](http://ffmpeg.org), based on general ideas from [python-video-converter](https://github.com/senko/python-video-converter) and presets idea from [QWinFF](http://qwinff.github.io).

## GUI Screenshot

![Screenshot](screenshot.png)

## App Goal

Unlike other video converters, VideoMorph focuses on a single goal: **make video conversion simple, fast and easy**, by providing an user-friendly GUI and by allowing you to convert your videos to the currently most popular formats (`AVI`, `MP4`, `MPG`, `WEBM`, `DVD`, `VCD`, `FLV`, `MOV`, `WMV`, `OGV`).

VideoMorph's GUI is intended to be simple and clean, focused on usability and free of awkward and rarely used options.

VideoMorph is a video converter, just that. If you want a video editor, VideoMorph isn't for you.

## Requirements

VideoMorph uses the following libraries and programs:

 - [PyQt5](https://riverbankcomputing.com/software/pyqt/download5)
 - [FFmpeg](http://ffmpeg.org)
 - [Python](https://python.org) > 3.4

You should install these programs and libraries for VideoMorph to work properly.

On Windows systems you'll also need:

 - [setuptools](https://pypi.python.org/pypi/setuptools)

## Installation

To install the application from the source file (`TAR.GZ` format package) on a GNU/Linux system, open a command-line and type this:

```console
$ tar -xvf videomorph-x.x.tar.gz
$ cd videomorph-x.x
$ python3 setup.py build
$ sudo python3 setup.py install
```

The preceding commands doesn't install the requirements, so you'll have to install them manually.

On Debian based Linux distributions you can install VideoMorph by typing at your command-line:

```console
$ sudo install.sh
```

This command should install VideoMorph and its dependencies, including [ffmpeg](http://ffmpeg.org) library and [PyQt5](https://riverbankcomputing.com/software/pyqt/download5), from your current repository.

To install from the `DEB` package on Debian based distros, it is recommended you to use [GDebi]() packages installer and follow the instructions, just that... This should install VideoMorph and all its dependencies from your current repository.

To use a Portable Edition (PE), decompress the `TAR.GZ` or the `ZIP` file (GNU/Linux and Windows respectively) in any directory, and then double-click on `videomorph` or `videomorph.exe` depending on your platform.

On Windows you can use the installers we provide.

## Contributing

Read VideoMorph's Manifest, then just clone the repo and make a pull request!

## Licensing and Patents

VideoMorph is licensed under [Apache License Version 2.0](http://www.apache.org/licenses/).
Following the idea of [python-video-converter](https://github.com/senko/python-video-converter), VideoMorph only uses the [ffmpeg](http://ffmpeg.org) binaries, so, it doesn't need to be licensed under LGPL/GPL.

## Authors and Contributors

Authors:

 - [Ozkar L. Garcell](mailto:ozkar.garcell@gmail.com)
 - [Leodanis Pozo Ramos](mailto:lpozor78@gmail.com)

Contributors:

 - [Maikel Llamaret Heredia](http://gutl.jovenclub.cu)
 - [Carlos Parra Zaldivar](http://libreoffice.cubava.cu)
 - [Leonel Salazar Videaux](http://debianhlg.cubava.cu/)
 - Osmel Cruz

## Copyright

Copyright 2016-2018 VideoMorph Development Team.
