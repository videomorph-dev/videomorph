# -*- coding: utf-8 -*-

# File name: mainctrl.py
#
# Copyright (C) 2019 Leodanis Pozo Ramos <lpozor78@gmail.com>
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

"""This module provides Main Controller for Qt GUI."""

import sys
from pathlib import Path

from PyQt5.QtCore import QLibraryInfo
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import qApp

from videomorph import BASE_DIR
from videomorph import LOCALE
from videomorph import SYS_PATHS
from videomorph import VM_PATHS
from videomorph.console import run_on_console
from qtviews.videomorph import VideoMorphMW


class QtMainController:
    """Class to provide main controller for Qt GUI."""

    def __init__(self):
        """Class initializer."""
        self.app = QApplication(sys.argv)

        # Setup app translator
        app_translator = QTranslator()

        translator_pwd = Path(BASE_DIR, VM_PATHS.i18n)

        if translator_pwd.exists():
            app_translator.load(
                str(translator_pwd.joinpath('videomorph_{0}'.format(LOCALE))))
        else:
            translator_sys_path = Path(SYS_PATHS.i18n,
                                       'videomorph_{0}'.format(LOCALE))
            app_translator.load(str(translator_sys_path))

        self.app.installTranslator(app_translator)
        qt_translator = QTranslator()
        qt_translator.load("qt_" + LOCALE,
                           QLibraryInfo.location(
                               QLibraryInfo.TranslationsPath))
        self.app.installTranslator(qt_translator)

        self.model = None
        self.view = VideoMorphMW()

    def run(self):
        """Run the app."""

        # Check for conversion library and run
        if self.view.conversion_lib.library_path:
            if len(sys.argv) > 1:  # If it is running from console
                run_on_console(self.app, self.view)
            else:  # Or is running on GUI
                self.view.show()
                sys.exit(self.app.exec_())
        else:
            msg_box = QMessageBox(
                QMessageBox.Critical,
                self.view.tr('Error!'),
                self.view.no_library_msg,
                QMessageBox.NoButton, self.view)
            msg_box.addButton("&Ok", QMessageBox.AcceptRole)
            if msg_box.exec_() == QMessageBox.AcceptRole:
                qApp.closeAllWindows()
