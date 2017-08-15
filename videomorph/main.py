# -*- coding: utf-8 -*-
#
# File _name: main.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg and avconv.
#   Copyright 2016-2017 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import sys
from os import sep
from os.path import exists

from PyQt5.QtCore import QLibraryInfo
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import qApp

from .froms import VideoMorphMW
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
