# -*- coding: utf-8 -*-
#
# File name: main.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
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

"""This module contains the main function for VideoMorph."""

import sys
from os import sep
from os.path import exists
from os.path import join as join_path

from PyQt5.QtCore import QLibraryInfo
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import qApp

from .converter import BASE_DIR
from .converter import LOCALE
from .converter import SYS_PATHS
from .converter import VM_PATHS
from .converter.console import run_on_console
from .forms.videomorph import VideoMorphMW


def main():
    """Main app function."""
    # Create the app
    app = QApplication(sys.argv)

    # Setup app translator
    app_translator = QTranslator()

    if exists(join_path(BASE_DIR, VM_PATHS.i18n)):
        app_translator.load(join_path(
            BASE_DIR, VM_PATHS.i18n, 'videomorph_{0}'.format(LOCALE)))
    else:
        app_translator.load(join_path(
            SYS_PATHS.i18n, 'videomorph_{0}'.format(LOCALE)))

    app.installTranslator(app_translator)
    qt_translator = QTranslator()
    qt_translator.load("qt_" + LOCALE,
                       QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qt_translator)

    # Run the app
    run_app(app=app)


def run_app(app):
    """Run the app."""
    # Create the Main Window
    main_win = VideoMorphMW()
    # Check for conversion library and run
    if main_win.conversion_lib.library_path:
        if len(sys.argv) > 1:  # If it is running from console
            run_on_console(app, main_win)
        else:  # Or is running on GUI
            main_win.show()
            sys.exit(app.exec_())
    else:
        msg_box = QMessageBox(
            QMessageBox.Critical,
            main_win.tr('Error!'),
            main_win.no_library_msg,
            QMessageBox.NoButton, main_win)
        msg_box.addButton("&Ok", QMessageBox.AcceptRole)
        if msg_box.exec_() == QMessageBox.AcceptRole:
            qApp.closeAllWindows()
