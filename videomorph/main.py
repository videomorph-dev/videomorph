# -*- coding: utf-8 -*-

# File name: main.py
#
# Copyright '2017' Leodanis Pozo Ramos <lpozo@openmailbox.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

"""This module defines the main() function for VideoMorph."""

import sys
from os import sep
from os.path import exists

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import qApp
from PyQt5.QtCore import QTranslator
from PyQt5.QtCore import QLibraryInfo
from PyQt5.QtWidgets import QApplication

from .videomorph import VideoMorphMW
from .converter import get_locale


def main():
    """Main app function."""
    # Create the app
    app = QApplication(sys.argv)

    # Setup app translator
    locale = get_locale()
    app_translator = QTranslator()
    if exists('..{0}share{1}videomorph{2}translations'.format(sep, sep, sep)):
        app_translator.load(
            "..{0}share{1}videomorph{2}translations{3}videomorph_{4}".format(
                sep, sep, sep, sep, locale))
    else:
        app_translator.load(
            "{0}usr{1}share{2}videomorph{3}translations"
            "{4}videomorph_{5}".format(sep, sep, sep, sep, sep, locale))

    app.installTranslator(app_translator)
    qt_translator = QTranslator()
    qt_translator.load("qt_" + locale,
                       QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qt_translator)

    # Run the app
    run_app(app=app)


def run_app(app):
    """Run the app."""
    # Create the Main Window
    main_win = VideoMorphMW()
    # Check for conversion library and run
    if main_win.conversion_lib.get_system_library_name() is not None:
        if len(sys.argv) > 1:  # If it is running from console
            from .converter import run_on_console
            run_on_console(app, main_win)
        else:  # Or is running on GUI
            main_win.show()
            sys.exit(app.exec_())
    else:
        msg_box = QMessageBox(
            QMessageBox.Critical,
            main_win.tr('Error!'),
            main_win.tr('Ffmpeg or Avconv Libraries '
                        'not Found in your System'),
            QMessageBox.NoButton, main_win)
        msg_box.addButton("&Ok", QMessageBox.AcceptRole)
        if msg_box.exec_() == QMessageBox.AcceptRole:
            qApp.closeAllWindows()
