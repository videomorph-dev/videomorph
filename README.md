# VideoMorph

![Building](https://github.com/videomorph-dev/videomorph/workflows/Building/badge.svg)
[![Open Source Love](https://badges.frapsoft.com/os/v2/open-source.svg?v=102)](https://github.com/ellerbrock/open-source-badge/)
[![Maintainability](https://api.codeclimate.com/v1/badges/5f6cd3f7c20bccee2065/maintainability)](https://codeclimate.com/github/videomorph-dev/videomorph/maintainability)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/videomorph-dev/videomorph/pulls)

**VideoMorph** is a **video converter** based on [ffmpeg](http://ffmpeg.org). It's written with [Python](https://python.org) 3 and [PyQt5](https://www.riverbankcomputing.com/static/Docs/PyQt5/introduction.html). With VideoMorph, you can convert your favorite videos to the currently more popular video formats, such as **MPG**, **MP4**, **AVI**, **WEBM**, **DVD**, **VCD**, **FLV**, **MOV**, **OGV**, **WMV**, **MKV**. You can also extract the audio to a file with **MP3** or **OGA** formats.

VideoMorph is a video converter, just that. It consists on a GUI wrapper for [Ffmpeg](http://ffmpeg.org), based on general ideas from [python-video-converter](https://github.com/senko/python-video-converter), and presets idea from [QWinFF](http://qwinff.github.io). If you're looking for a video editor, then VideoMorph isn't for you.

- [VideoMorph](#videomorph)
  - [GUI Screenshot](#gui-screenshot)
  - [Requirements](#requirements)
  - [Installing VideoMorph](#installing-videomorph)
    - [Installing From the Binary Packages](#installing-from-the-binary-packages)
      - [On GNU/Linux](#on-gnulinux)
      - [On Windows](#on-windows)
    - [Installing Form the Source Packages](#installing-form-the-source-packages)
      - [On GNU/Linux](#on-gnulinux-1)
      - [On Windows](#on-windows-1)
    - [Using Portable Editions (if available)](#using-portable-editions-if-available)
  - [Contributing to the Source](#contributing-to-the-source)
    - [Setting Up the Development Environment](#setting-up-the-development-environment)
    - [Commiting Changes](#commiting-changes)
    - [Internal Contributions Procedure](#internal-contributions-procedure)
    - [External Contributions Procedure](#external-contributions-procedure)
    - [Branch Naming Conventions](#branch-naming-conventions)
    - [Coding and Docstrings Style](#coding-and-docstrings-style)
    - [Commit Messaging Style](#commit-messaging-style)
  - [Licensing](#licensing)
  - [Authors and Contributors](#authors-and-contributors)
  - [Copyright](#copyright)

## GUI Screenshot

![Screenshot](screenshot.png)

## Requirements

VideoMorph uses the following external libraries and programs:

- [PyQt5](https://www.riverbankcomputing.com/static/Docs/PyQt5/introduction.html) >= 5.15.2
- [FFmpeg](http://ffmpeg.org)
- [Python](https://python.org) >= 3.7

You need to install these programs and libraries for VideoMorph to work properly.

On Windows systems, you also need:

- [setuptools](https://pypi.python.org/pypi/setuptools)

## Installing VideoMorph

You can install and use VideoMorph on GNU/Linux and Windows systems. There are several ways to install the application. Let's take a look at them.

```
Note: We haven't made VideoMorph run on macOS, yet :-|
```

### Installing From the Binary Packages

On GNU/Linux and Windows, you can install VideoMorph using the appropriate binary package.

#### On GNU/Linux

You can install VideoMorph on Debian/Ubuntu and derivatives by running the following steps:

1. Download the `.deb` package
2. Open a terminal, and run the following commands as **root** or using **sudo**:

```sh
$ apt install ffmpeg python3 python3-pyqt5
    ...
$ cd <directory containing VideoMorph binary>
$ dpkg -i videomorph_x.x_all.deb
    ...
```

That's enough to get VideoMorph (and its dependencies) installed on your system. You can also install VideoMorph's `.deb` package using GDebi, which is a GUI Package Installer that manages the dependencies for you.

#### On Windows

To install VideoMorph on Windows systems, you need to:

1. Download the installer that matches your architecture
2. Run the installer as an `administrator`
3. Follow the on-screen instructions

### Installing Form the Source Packages

You can install VideoMorph from the source packages. Let's take a look at how to do it.

#### On GNU/Linux

To install the application from the source package on a GNU/Linux system, do the following:

1. Download the `.tar.gz` package
2. Run the following commands:

```bash
$ tar -xvf videomorph-x.x.tar.gz
    ...
$ cd videomorph-x.x
$ sudo pip3 install -r requirements.txt
    ...
$ python3 setup.py build
    ...
$ sudo python3 setup.py install
```

The preceding commands build and install VideoMorph and part of its dependencies on your system. To complete the installation, you need to install Ffmpeg form your distro's software repository.

```
Note: If you install Ffmpeg from its sources, then you need to make sure that the commands `ffmpeg`, and `ffprobe` are in your system's PATH.
```

On Debian/Ubuntu derivatives, you can also install VideoMorph by running the `install.sh`  script as **root** or using **sudo**:

```bash
$ tar -xvf videomorph-x.x.tar.gz
$ cd videomorph-x.x
$ sudo ./install.sh
```

This commands unpack and install VideoMorph and its dependencies (Ffmpeg, and PyQt5) from your distro's current repository.

#### On Windows

To install VideoMorph from the source package on Windows, you need to make sure you have Python3 installed. Then run the following steps:

1. Download and decompress the `.zip` source package
2. Open your Windows' command-line (`cmd.exe`), and type the following commands:

```
C:/> cd videomorph-x.x
C:/> pip install -r requirements.txt
    ...
C:/> python3 setup.py build
    ...
C:/> python3 setup.py install
```

This installs VideoMorph on your system, but you need to install Ffmpeg manually.

```
Note: It's possible that you have to run the second and the fourth command as an `administrator`.
```

### Using Portable Editions (if available)

To use a Portable Edition (PE) of VideoMorph, you need to:

1. Download the PE package that matches your current system
2. Decompress the `.tar.gz` or the `.zip` file (Linux and Windows respectively) in any directory
3. Double-click on VideoMorph's executable (`videomorph` or `videomorph.exe`)

## Contributing to the Source

If you want to contribute to VideoMorph's development cycle, you can follow the steps described in this section.

Reach out to contribute with:

- Translations
- Artwork and GUI design
- Customized conversion presets
- Tutorials on how to use VideoMorph
- Documentation
- Feature requests
- Bug reports

All contributions are welcome, even a report about a typo is welcome, so it's your turn to talk, but remember: VideoMorph is just a video converter, not a video editor.

### Setting Up the Development Environment

To set up the development environment and contribute code to VideoMorph, just open a command-line and type in:

```sh
$ python3 -m venv venv
    ...
$ source venv/bin/activate
(venv)$ pip install -r requirements.txt
```

You also need to install the Ffmpeg library on your system and make it available in your system PATH.

### Commiting Changes

The following members of the VideoMorph Development Team can commit changes into the repo:

- [Leodanis Pozo Ramos](https://github.com/lpozo)
- [Leonel Salazar Videaux](https://github.com/leonel-lordford)
- [Ozkar L. Garcell](https://github.com/codeshard)

### Internal Contributions Procedure

1. Create a new feature branch from `develop`
2. Work on new features or bug fixes
3. Push your feature branch to the `videomorph-dev`
4. Create a pull request (PR) targeting `develop`
5. Wait for review, feedback, and approval
6. Make the required updates if any
7. Merge the approved PR into `develop`
8. Delete the temporarily branch

```
Note: The preceding procedure is intended to be used by the members of the VideoMorph Development Team.
```

### External Contributions Procedure

External contributors must:

1. Fork the repo on GitHub
2. Create a new feature branch from `develop`
3. Work on your feature
4. Make a PR targeting `develop` on `videomorph-dev`
5. Wait for review, feedback, and approval
6. Make the required updates if any

### Branch Naming Conventions

The name for a branch will be like:

```
username_i000_topic
```

Where:

- `username` corresponds to the GitHub username
- `i000` represents the issue number the branch is dealing with. If there is no issue to map the branch then `i000` will be used
- `topic` stands for a descriptive name that reflects the main goal of the branch (e.g: `john_i024_support_mov_format`)

### Coding and Docstrings Style

- VideoMorph's code follows the coding style guidelines described in [PEP8](https://www.python.org/dev/peps/pep-0008/)
- Docstrings in VideoMorph's code will follow the guidelines described in [PEP257](https://www.python.org/dev/peps/pep-0257/)

You can use [Black](https://github.com/ambv/black) to automatically format your code, just set the line length to 79. You can also use [isort](https://github.com/timothycrosley/isort) for your imports.

### Commit Messaging Style

General rules for writing commit messages:

1. Separate subject from body with a blank line
2. Limit the subject line to 50 characters
3. Capitalize the subject line
4. Do not end the subject line with a period
5. Use the imperative mood in the subject line
6. Wrap the body at 72 characters
7. Use the body to explain what and why vs how

Here's an example:

```
Add support for MOV format

Add support for MOV format with several presets to increase the
default conversion options.
```

Keep in mind that not all commits require an explanatory body, sometimes the subject line is enough.

For more details see: [How to Write a Git Commit Message](https://chris.beams.io/posts/git-commit/)

## Licensing

VideoMorph is licensed under [Apache License Version 2.0](http://www.apache.org/licenses/).

Following the idea of [python-video-converter](https://github.com/senko/python-video-converter), VideoMorph only uses the Ffmpeg binaries, so it doesn't need to be licensed under LGPL/GPL.

## Authors and Contributors

Authors:

- [Leodanis Pozo Ramos](mailto:lpozor78@gmail.com)
- [Ozkar L. Garcell](mailto:ozkar.garcell@gmail.com)

Contributors:

- [Maikel Llamaret Heredia](http://gutl.jovenclub.cu) **[Rest In Peace Dear Friend]**
- [Leonel Salazar Videaux](http://debianhlg.cubava.cu/)
- [Carlos Parra Zaldivar](http://libreoffice.cubava.cu)
- Osmel Cruz

## Copyright

Copyright 2016-2021 VideoMorph Development Team.
