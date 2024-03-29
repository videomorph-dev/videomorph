# -*- coding: utf-8 -*-
#
# File name: main.py
#
#   VideoMorph - A PyQt6 frontend to ffmpeg.
#   Copyright 2016-2022 VideoMorph Development Team

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
from pathlib import Path

from PyQt6.QtCore import QTranslator
from PyQt6.QtWidgets import QApplication, QMessageBox

from .converter import BASE_DIR, LOCALE, VM_PATHS
from .converter.console import run_on_console
from .converter.vmpath import LIBRARY_PATH
from .forms.videomorph import VideoMorphMW


def main():
    """Main app function."""
    # Create the app
    app = QApplication(sys.argv)
    qApp= QApplication.instance()

    # Setup app translator
    app_translator = QTranslator()

    i18n_dir = Path(BASE_DIR, VM_PATHS["i18n"])
    i18n_file = i18n_dir.joinpath("".join(("videomorph_", LOCALE[:2], ".qm")))

    if i18n_file.exists():
        trans = i18n_dir.joinpath("videomorph_{0}".format(LOCALE)).__str__()
        app_translator.load(trans)
        app.installTranslator(app_translator)

    # Create the Main Window
    main_win = VideoMorphMW()

    # Check for conversion library and run
    if LIBRARY_PATH:
        if len(sys.argv) > 1:  # If it is running from console
            run_on_console(app, main_win)
        else:  # Or is running on GUI
            main_win.show()
            sys.exit(app.exec())
    else:
        msg_box = QMessageBox(
            QMessageBox.Icon.Critical,
            main_win.tr('Error!'),
            main_win.no_library_msg,
            QMessageBox.StandardButton.NoButton, main_win)
        msg_box.addButton("&Ok", QMessageBox.ButtonRole.AcceptRole)
        if msg_box.exec() == QMessageBox.ButtonRole.AcceptRole:
            qApp.closeAllWindows()
