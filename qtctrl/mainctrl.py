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
from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import qApp

from videomorph import BASE_DIR
from videomorph import LOCALE
from videomorph import STATUS
from videomorph import SYS_PATHS
from videomorph import VM_PATHS
from videomorph.conversionlib import ConversionLib
from videomorph.console import run_on_console
from videomorph.media import MediaList
from videomorph.profile import ConversionProfile
from qtviews import COLUMNS
from qtviews.videomorph import VideoMorphMW
from qtviews.about import AboutVMDialog
from qtviews.changelog import ChangelogDialog


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

        self._init_model()

        self.view = VideoMorphMW(self)

        self.no_library_msg = self.view.tr('Ffmpeg Library not Found'
                                           ' in your System')

    def _init_model(self):
        self.media_list_duration = 0.0
        self.source_dir = Path().home()

        self.conversion_lib = ConversionLib()
        self.conversion_lib.setup_converter(
            reader=self._ready_read,
            finisher=self._finish_file_encoding,
            process_channel=QProcess.MergedChannels)
        self.reader = self.conversion_lib.reader
        self.timer = self.conversion_lib.timer
        self.profile = ConversionProfile(
            prober=self.conversion_lib.prober_path)

        self.media_list = MediaList(profile=self.profile)

    def _ready_read(self):
        """Is called when the conversion process emit a new output."""
        self.reader.update_read(
            process_output=self.conversion_lib.read_converter_output())

        self.view.update_conversion_progress()

    def _finish_file_encoding(self):
        """Finish the file encoding process."""
        if self.media_list.running_file_status != STATUS.stopped:
            file_name = self.media_list.running_file_name(with_extension=True)
            self.view.notify(file_name)
            # Close and kill the converterprocess
            self.conversion_lib.close_converter()
            # Check if the process finished OK
            if (self.conversion_lib.converter_exit_status() ==
                    QProcess.NormalExit):
                # When finished a file conversion...
                self.tb_tasks.item(self.media_list.position,
                                   COLUMNS.PROGRESS).setText(self.tr('Done!'))
                self.media_list.running_file_status = STATUS.done
                self.pb_progress.setProperty("value", 0)
                if self.chb_delete.checkState():
                    self.media_list.delete_running_file_input()
        else:
            # If the process was stopped
            if not self.conversion_lib.converter_is_running:
                self.view.tb_tasks.item(
                    self.media_list.position,
                    COLUMNS.PROGRESS).setText(self.tr('Stopped!'))
        # Attempt to end the conversion process
        self._end_encoding_process()

    def run_app(self):
        """Run the app."""

        # Check for conversion library and run
        if self.conversion_lib.library_path:
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

    def on_about_action_clicked(self):
        """Show About dialog."""
        about_dlg = AboutVMDialog(parent=self.view)
        about_dlg.exec_()

    def on_changelog_action_clicked(self):
        """Show the changelog dialog."""
        changelog_dlg = ChangelogDialog(parent=self.view)
        changelog_dlg.exec_()
