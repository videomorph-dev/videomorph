#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File name: videomorph.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg and avconv.
#   Copyright 2015-2016 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""This module defines the VideoMorph main window that holds the UI."""

import re
from os import sep
from os.path import exists
from os.path import basename
from functools import partial
from time import time

from PyQt5.QtCore import (QSize,
                          Qt,
                          QSettings,
                          QDir,
                          QPoint,
                          QProcess,
                          QTranslator,
                          QLibraryInfo)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (QMainWindow,
                             QApplication,
                             QWidget,
                             QVBoxLayout,
                             QHBoxLayout,
                             QSizePolicy,
                             QGroupBox,
                             QLabel,
                             QSpacerItem,
                             QComboBox,
                             QProgressBar,
                             QToolBar,
                             QTableWidget,
                             QTableWidgetItem,
                             QLineEdit,
                             QAction,
                             QStyle,
                             QAbstractItemView,
                             QFileDialog,
                             QMessageBox,
                             QHeaderView,
                             QToolButton,
                             QItemDelegate,
                             qApp)

from . import APPNAME
from . import VERSION
from . import videomorph_qrc
from .about import AboutVMDialog
from .converter import Converter
from .converter import CONV_LIB
from .converter import STATUS
from .converter import InvalidMetadataError
from .converter import MediaFileThread
from .converter import media_file_factory
from .converter import MediaList
from .converter import which
from .converter import write_time
from .converter import get_locale
from .settings import SettingsDialog
from .addprofile import AddProfileDialog

# Conversion tasks list table columns
NAME, DURATION, QUALITY, PROGRESS = range(4)


class MMWindow(QMainWindow):
    """Main Window class."""

    def __init__(self):
        """Class initializer."""
        super(MMWindow, self).__init__()
        # App data structures
        # Create the Media list object
        self.media_list = MediaList()
        # Variables for calculating total progress
        self.time_jump = 0.0
        self.partial_time = 0.0
        self.total_time = 0.0
        self.total_duration = 0.0

        # App interface setup
        # Window size
        self.resize(680, 576)
        # Set window title
        self.setWindowTitle(APPNAME + ' ' + VERSION)
        # Define and set app icon
        icon = QIcon()
        icon.addPixmap(QPixmap(':/logo/images/videomorph.png'))
        self.setWindowIcon(icon)
        # Define app central widget
        self.central_widget = QWidget(self)
        # Difine layouts
        self.vl = QVBoxLayout(self.central_widget)
        self.hl = QHBoxLayout()
        self.vl1 = QVBoxLayout()
        self.vl2 = QVBoxLayout()
        # Define groups
        self.group_settings()
        self.fix_layout()
        self.group_tasks_list()
        self.group_output_directory()
        self.group_progress()
        # Create the toolbar
        self.create_toolbar()
        # Add layouts
        self.hl.addLayout(self.vl2)
        self.vl.addLayout(self.hl)
        # Set central widget
        self.setCentralWidget(self.central_widget)
        # Create actions
        self.create_actions()

        # Default conversion library and prober
        self.conversion_lib = CONV_LIB.ffmpeg
        self.prober = "ffprobe"

        # Create initial Settings if not created
        self.create_initial_settings()

        # XML Profile
        from .converter import XMLProfile
        self.xml_profile = XMLProfile
        self.xml_profile.create_profiles_xml_file()
        self.xml_profile.set_xml_root()

        # Populate PROFILES combo box
        self.populate_profiles_combo()

        # Create the conversion profile object only once
        self.conversion_profile = self.xml_profile.get_conversion_profile(
            profile_name=self.cb_profiles.currentText(),
            target_quality=self.cb_presets.currentText())

        # Read app settings
        self.read_app_settings()

        # Create the converter according to the user selection of
        # conversion library
        self.converter = Converter(media_list=self.media_list,
                                   conversion_lib=self.conversion_lib)

        self.converter.process.setProcessChannelMode(QProcess.MergedChannels)
        self.converter.process.readyRead.connect(self._read_encoding_output)
        self.converter.process.finished.connect(self.finish_file_encoding)

        # Disable presets and profiles combo boxes
        self.cb_presets.setEnabled(False)
        self.cb_profiles.setEnabled(False)

        # Create app main menu bar
        self.create_main_menu()

        # Create app status bar
        self.create_status_bar()

        # Set tool buttons style
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

    def group_settings(self):
        """Settings group."""
        gb_settings = QGroupBox(self.central_widget)
        gb_settings.setTitle(self.tr('Conversion Presets'))
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
            gb_settings.sizePolicy().hasHeightForWidth())
        gb_settings.setSizePolicy(size_policy)
        hl = QHBoxLayout(gb_settings)
        vl = QVBoxLayout()
        hl1 = QHBoxLayout()
        label = QLabel(self.tr('Convert To:'))
        hl1.addWidget(label)
        spacer_item = QSpacerItem(40,
                                  20,
                                  QSizePolicy.Expanding,
                                  QSizePolicy.Minimum)
        hl1.addItem(spacer_item)
        vl.addLayout(hl1)
        self.cb_profiles = QComboBox(
            gb_settings,
            statusTip=self.tr('Select the Desired Video Format'))
        self.cb_profiles.setMinimumSize(QSize(200, 0))
        vl.addWidget(self.cb_profiles)
        hl2 = QHBoxLayout()
        label = QLabel(self.tr('Target Quality:'))
        hl2.addWidget(label)
        spacerItem1 = QSpacerItem(40,
                                  20,
                                  QSizePolicy.Expanding,
                                  QSizePolicy.Minimum)
        hl2.addItem(spacerItem1)
        vl.addLayout(hl2)
        self.cb_presets = QComboBox(
            gb_settings,
            statusTip=self.tr('Select the Desired Video Quality'))
        self.cb_presets.setMinimumSize(QSize(200, 0))

        self.cb_profiles.currentIndexChanged.connect(partial(
            self.populate_presets_combo, self.cb_presets))

        self.cb_presets.activated.connect(self.update_media_files_status)

        vl.addWidget(self.cb_presets)
        hl.addLayout(vl)
        self.vl1.addWidget(gb_settings)

    def fix_layout(self):
        """Fix widgets layout."""
        spacer_item = QSpacerItem(20,
                                  40,
                                  QSizePolicy.Minimum,
                                  QSizePolicy.Expanding)
        self.vl1.addItem(spacer_item)
        self.hl.addLayout(self.vl1)

    def group_tasks_list(self):
        """Define the Tasks Group arrangement."""
        gb_tasks = QGroupBox(self.central_widget)
        gb_tasks.setTitle(self.tr('List of Conversion Tasks'))
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(gb_tasks.sizePolicy().hasHeightForWidth())
        gb_tasks.setSizePolicy(sizePolicy)
        hl = QHBoxLayout(gb_tasks)
        self.tb_tasks = QTableWidget(gb_tasks)
        self.tb_tasks.setColumnCount(4)
        self.tb_tasks.setRowCount(0)
        self.tb_tasks.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tb_tasks.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tb_tasks.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch)
        self.tb_tasks.setHorizontalHeaderLabels(
            [self.tr('File Name'),
             self.tr('Duration'),
             self.tr('Target Quality'),
             self.tr('Progress')])
        self.tb_tasks.cellClicked.connect(self._enable_remove_file_action)
        # Create a combo box for Target quality
        self.tb_tasks.setItemDelegate(TargetQualityDelegate(parent=self))
        hl.addWidget(self.tb_tasks)
        self.vl2.addWidget(gb_tasks)
        self.tb_tasks.doubleClicked.connect(self.update_edit_triggers)

    def update_edit_triggers(self):
        if (int(self.tb_tasks.currentColumn()) == QUALITY and not
                self.converter.is_running):
            self.tb_tasks.setEditTriggers(QAbstractItemView.AllEditTriggers)
        else:
            self.tb_tasks.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def group_output_directory(self):
        """Define the output directory Group arrangement."""
        gb_output = QGroupBox(self.central_widget)
        gb_output.setTitle(self.tr('Output Directory'))
        vl = QVBoxLayout(gb_output)
        vl1 = QVBoxLayout()
        hl = QHBoxLayout()
        self.le_output = QLineEdit(
            str(QDir.homePath()),
            statusTip=self.tr('Choose Output Directory'))
        self.le_output.setReadOnly(True)
        hl.addWidget(self.le_output)
        self.tb_output = QToolButton(
            gb_output,
            statusTip=self.tr('Choose Output Directory'))
        self.tb_output.setText('...')
        self.tb_output.clicked.connect(self.output_directory)
        hl.addWidget(self.tb_output)
        vl1.addLayout(hl)
        vl.addLayout(vl1)
        self.vl2.addWidget(gb_output)

    def group_progress(self):
        """Define the Progress Group arrangement."""
        gb_progress = QGroupBox(self.central_widget)
        gb_progress.setTitle(self.tr('Progress'))
        vl = QVBoxLayout(gb_progress)
        label_progress = QLabel(gb_progress)
        label_progress.setText(self.tr('Operation Progress'))
        vl.addWidget(label_progress)
        self.pb_progress = QProgressBar(gb_progress)
        self.pb_progress.setProperty('value', 0)
        vl.addWidget(self.pb_progress)
        label_total_progress = QLabel(gb_progress)
        label_total_progress.setText(self.tr('Total Progress'))
        vl.addWidget(label_total_progress)
        self.pb_total_progress = QProgressBar(gb_progress)
        self.pb_total_progress.setProperty('value', 0)
        vl.addWidget(self.pb_total_progress)
        self.vl2.addWidget(gb_progress)

    @staticmethod
    def _get_settings_file():
        return QSettings('{0}{1}.videomorph{2}config.ini'.format(
                            QDir.homePath(), sep, sep),
                         QSettings.IniFormat)

    def create_initial_settings(self):
        if not exists('{0}{1}.videomorph{2}config.ini'.format(
                QDir.homePath(), sep, sep)):
            self.write_app_settings(pos=QPoint(100, 50),
                                    size=QSize(1096, 510),
                                    profile_index=0,
                                    preset_index=0)

    def read_app_settings(self):
        """Read the app settings."""
        settings = self._get_settings_file()
        pos = settings.value("pos", QPoint(600, 200), type=QPoint)
        size = settings.value("size", QSize(1096, 510), type=QSize)
        self.resize(size)
        self.move(pos)
        if 'profile' and 'preset' in settings.allKeys():
            prof = settings.value('profile')
            pres = settings.value('preset')
            self.cb_profiles.setCurrentIndex(int(prof))
            self.cb_presets.setCurrentIndex(int(pres))
        if 'output_dir' in settings.allKeys():
            self.le_output.setText(str(settings.value('output_dir')))
        if 'conversion_lib' in settings.allKeys():
            self.conversion_lib = settings.value('conversion_lib')

    def write_app_settings(self,
                           pos,
                           size,
                           profile_index,
                           preset_index,
                           output_dir=QDir.homePath(),
                           conv_lib=CONV_LIB.ffmpeg):
        """Write app settings on exit."""
        settings = self._get_settings_file()
        settings.setValue("pos", pos)
        settings.setValue("size", size)
        settings.setValue("profile", profile_index)
        settings.setValue("preset", preset_index)
        settings.setValue("output_dir", output_dir)
        settings.setValue('conversion_lib', conv_lib)

    def closeEvent(self, event):
        """Things to todo on close."""
        # Disconnect the finished signal
        self.converter.process.finished.disconnect(self.finish_file_encoding)
        # Close communication and kill the encoding process
        if self.converter.is_running:
            self.converter.process.close()
            self.converter.process.kill()
        # Save settings
        self.write_app_settings(pos=self.pos(),
                                size=self.size(),
                                profile_index=self.cb_profiles.currentIndex(),
                                preset_index=self.cb_presets.currentIndex(),
                                output_dir=self.le_output.text(),
                                conv_lib=self.conversion_lib)
        event.accept()

    def check_conversion_lib(self):
        """Check if ffmpeg or/and avconv are installed on the system."""
        if which(CONV_LIB.ffmpeg) or which(CONV_LIB.avconv):
            return True
        else:
            msg_box = QMessageBox(
                QMessageBox.Critical,
                self.tr('Error!'),
                self.tr('Ffmpeg or Avconv Libraries not Found in your System'),
                QMessageBox.NoButton, self)
            msg_box.addButton("&Ok", QMessageBox.AcceptRole)
            if msg_box.exec_() == QMessageBox.AcceptRole:
                qApp.closeAllWindows()
                return False

    def create_actions(self):
        """Create the actions and connect them to the tool bar buttons."""
        self.add_media_file_action = QAction(
            # Remove this line to use costume icons
            self.style().standardIcon(QStyle.SP_DialogOpenButton),
            self.tr('&Open'),
            self,
            shortcut="Ctrl+O",
            enabled=True,
            statusTip=self.tr('Add Video Files to the List '
                              'of Conversion Tasks'),
            triggered=self.add_media)
        # Uncomment this line to use costume icons
        # self.add_media_file_action.setIcon(QIcon(':/icons/images/abrir.png'))

        self.add_profile_action = QAction(
            # Remove this line to use costume icons
            self.style().standardIcon(QStyle.SP_DialogApplyButton),
            self.tr('&Add Customized Profile...'),
            self,
            shortcut="Ctrl+F",
            enabled=True,
            statusTip=self.tr('Add Customized Profile'),
            triggered=self.add_profile)

        self.export_profile_action = QAction(
            # Remove this line to use costume icons
            self.style().standardIcon(QStyle.SP_DialogSaveButton),
            self.tr('&Export Conversion Profiles...'),
            self,
            shortcut="Ctrl+E",
            enabled=True,
            statusTip=self.tr('Export Conversion Profiles'),
            triggered=self.export_profile)

        self.clear_media_list_action = QAction(
            # Remove this line to use costume icons
            self.style().standardIcon(QStyle.SP_TrashIcon),
            self.tr('Clear &List'),
            self,
            shortcut="Ctrl+Del",
            enabled=False,
            statusTip=self.tr('Clear the Video Files List'),
            triggered=self.clear_media_list)
        # Uncomment this line to use costume icons
        # self.clear_media_list_action.setIcon(QIcon(':/icons/images/limpiar.png'))

        self.remove_media_file_action = QAction(
            # Remove this line to use costume icons
            self.style().standardIcon(QStyle.SP_BrowserStop),
            self.tr('&Remove File'),
            self,
            shortcut="Del",
            enabled=False,
            statusTip=self.tr('Remove Video File from the List'),
            triggered=self.remove_media_file)
        # Uncomment this line to use costume icons
        # self.remove_media_file_action.setIcon(QIcon(':/icons/images/eliminar.png'))

        self.convert_action = QAction(
            # Remove this line to use costume icons
            self.style().standardIcon(QStyle.SP_MediaPlay),
            self.tr('&Convert'),
            self,
            shortcut="Ctrl+R",
            enabled=False,
            statusTip=self.tr('Start Conversion Process'),
            triggered=self.start_encoding)
        # Uncomment this line to use costume icons
        # self.convert_action.setIcon(QIcon(':/icons/images/convertir.png'))

        self.stop_action = QAction(
            # Remove this line to use costume icons
            self.style().standardIcon(QStyle.SP_MediaStop),
            self.tr('&Stop'),
            self,
            shortcut="Ctrl+P",
            enabled=False,
            statusTip=self.tr('Stop Video File Conversion'),
            triggered=self.stop_file_encoding)
        # Uncomment this line to use costume icons
        # self.stop_action.setIcon(QIcon(':/icons/images/parar.png'))

        self.stop_all_action = QAction(
            # Remove this line to use costume icons
            self.style().standardIcon(QStyle.SP_DialogCancelButton),
            self.tr('S&top All'),
            self,
            shortcut="Ctrl+A",
            enabled=False,
            statusTip=self.tr('Stop All Video Conversion Tasks'),
            triggered=self.stop_all_files_encoding)

        self.about_action = QAction(
            # Remove this line to use costume icons
            self.style().standardIcon(QStyle.SP_MessageBoxInformation),
            self.tr('&About VideoMorph...'),
            self,
            shortcut="Ctrl+H",
            enabled=True,
            statusTip=self.tr('About VideoMorph'),
            triggered=self.about)
        # Uncomment this line to use costume icons
        # self.about_action.setIcon(QIcon(':/icons/images/parar.png'))

        self.exit_action = QAction(
            self.style().standardIcon(QStyle.SP_DialogCloseButton),
            self.tr('E&xit'),
            self,
            shortcut="Ctrl+Q",
            enabled=True,
            statusTip=self.tr('Exit VideoMorph'),
            triggered=self.close)

        self.settings_action = QAction(
            self.style().standardIcon(QStyle.SP_FileDialogDetailedView),
            self.tr('&Settings...'),
            self,
            shortcut="Ctrl+S",
            enabled=True,
            statusTip=self.tr('Open VideoMorph Settings Dialog'),
            triggered=self.settings)

        # Add actions to the tool bar
        self.tool_bar.addAction(self.add_media_file_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.clear_media_list_action)
        self.tool_bar.addAction(self.remove_media_file_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.convert_action)
        self.tool_bar.addAction(self.stop_action)
        self.tool_bar.addAction(self.stop_all_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.settings_action)

    def create_main_menu(self):
        self.file_menu = self.menuBar().addMenu(self.tr('&File'))
        self.file_menu.addAction(self.add_media_file_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.settings_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)

        self.edit_menu = self.menuBar().addMenu(self.tr('&Edit'))
        self.edit_menu.addAction(self.add_profile_action)
        self.edit_menu.addAction(self.export_profile_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.clear_media_list_action)
        self.edit_menu.addAction(self.remove_media_file_action)

        self.convert_menu = self.menuBar().addMenu(self.tr('&Conversion'))
        self.convert_menu.addAction(self.convert_action)
        self.convert_menu.addAction(self.stop_action)
        self.convert_menu.addSeparator()
        self.convert_menu.addAction(self.stop_all_action)

        self.hel_menu = self.menuBar().addMenu(self.tr('&Help'))
        self.hel_menu.addAction(self.about_action)

    def create_toolbar(self):
        """Create and add_file a tool bar to the interface."""
        self.tool_bar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)

    def create_status_bar(self):
        self.statusBar().showMessage(self.tr('Ready'))

    def about(self):
        a = AboutVMDialog(parent=self)
        a.exec_()

    def settings(self):
        """Open a Setting Dialog to define the conversion library to use."""
        s = SettingsDialog(parent=self)
        if self.conversion_lib == CONV_LIB.ffmpeg:
            s.radio_btn_ffmpeg.setChecked(True)
        elif self.conversion_lib == CONV_LIB.avconv:
            s.radio_btn_avconv.setChecked(True)

        if not which(CONV_LIB.ffmpeg):
            s.radio_btn_ffmpeg.setEnabled(False)
        elif not which(CONV_LIB.avconv):
            s.radio_btn_avconv.setEnabled(False)

        if s.exec_():
            if s.radio_btn_ffmpeg.isChecked():
                self.conversion_lib = CONV_LIB.ffmpeg
                self.converter.conversion_lib = self.conversion_lib
                self.prober = 'ffprobe'
            elif s.radio_btn_avconv.isChecked():
                self.conversion_lib = CONV_LIB.avconv
                self.converter.conversion_lib = self.conversion_lib
                self.prober = 'avprobe'

    def populate_profiles_combo(self):
        """Populate profiles combobox."""
        # Clear combobox content
        self.cb_profiles.clear()
        # Populate the combobox with new data
        self.cb_profiles.addItems(self.xml_profile.get_qualities_per_profile(
                locale=get_locale()).keys())

    def populate_presets_combo(self, cb_presets):
        """Populate presets combo box."""
        current_profile = self.cb_profiles.currentText()
        if current_profile != '':
            cb_presets.clear()
            cb_presets.addItems(self.xml_profile.get_qualities_per_profile(
                    locale=get_locale())[current_profile])
            self.update_media_files_status()

    def output_directory(self):
        """Choose output directory."""
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(
            self,
            self.tr('Choose Output Directory'),
            QDir.homePath(),
            options=options)

        if directory:
            self.le_output.setText(directory)
            self.update_interface(stop=False, stop_all=False, remove=False)

    def _fill_media_list(self, files_paths):
        threads = []
        for file_path in files_paths:
            t = MediaFileThread(factory=media_file_factory,
                                media_path=file_path,
                                conversion_profile=self.conversion_profile,
                                prober=self.prober)
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        for thread in threads:
            try:
                self.media_list.add_file(thread.media_file)
            except InvalidMetadataError:
                msg_box = QMessageBox(
                    QMessageBox.Critical,
                    self.tr('Error!'),
                    self.tr('Invalid Video File Information for: {fn}. '
                            'File not Added to Conversion List'.format(
                        fn=thread.media_file.get_name(with_extension=True))),
                    QMessageBox.Ok,
                    self)
                msg_box.show()

        return self.media_list

    def _load_files(self):
        # Dialog title
        title = self.tr('Select Video Files')
        # Media filters
        v_filter = (self.tr('Video Files') +
                    '(*.mkv *.ogg *.mp4 *.mpg *.dat '
                    '*.f4v *.flv *.wv *.3gp *.avi *.webm '
                    '*.wmv *.mov *.vob *.ogv *.ts)')

        # Select media files and store their path
        files_paths, _ = QFileDialog.getOpenFileNames(self,
                                                      title,
                                                      QDir.homePath(),
                                                      v_filter)
        return files_paths

    def _insert_table_item(self, item_text, row, column):
        item = QTableWidgetItem()
        item.setText(item_text)
        self.tb_tasks.setItem(row, column, item)

    def _create_table(self):
        self.tb_tasks.setRowCount(self.media_list.length)

        for row, media_file in enumerate(self.media_list):
            self._insert_table_item(
                item_text=media_file.get_name(with_extension=True),
                row=row,
                column=NAME)

            self._insert_table_item(
                item_text=str(write_time(media_file.info.format_duration)),
                row=row,
                column=DURATION)

            self._insert_table_item(
                item_text=str(self.cb_presets.currentText()),
                row=row,
                column=QUALITY)

            self._insert_table_item(item_text=self.tr('To Convert'),
                                    row=row,
                                    column=PROGRESS)

    def add_media(self):
        """Add media files to the list of conversion tasks."""
        files_paths = self._load_files()
        # If no file is selected then return
        if not files_paths:
            return

        # Update tool buttons so you can convert, or add_file, or clear...
        # only if there is not a conversion process running
        if self.converter.is_running:
            self.update_interface(presets=False,
                                  profiles=False,
                                  convert=False,
                                  clear=False,
                                  remove=False,
                                  output_dir=False,
                                  settings=False)
        else:
            # This rewind the encoding list if the encoding process is
            # not running
            self.media_list.running_index = -1
            # Update ui
            self.update_interface(stop=False, stop_all=False, remove=False)
        start = time()
        self._fill_media_list(files_paths)
        print(time() - start)

        self._create_table()

        # After adding files to the list, recalculate the list duration
        self.total_duration = self.media_list.duration

    def remove_media_file(self):
        """Remove selected media file from the list."""
        item = self.tb_tasks.currentItem().row()
        if item is not None:
            # Delete file from table
            self.tb_tasks.removeRow(item)
            # If all files are deleted... update the interface
            if not self.tb_tasks.rowCount():
                self.update_interface(convert=False,
                                      clear=False,
                                      remove=False,
                                      stop=False,
                                      stop_all=False,
                                      presets=False,
                                      profiles=False)
            # Remove file from MediaList
            self.media_list.delete_file(file_index=item)
            self.total_duration = self.media_list.duration

    def add_profile(self):
        ap = AddProfileDialog(parent=self)
        ap.exec_()

    def export_profile(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(
            self,
            self.tr('Export to Directory'),
            QDir.homePath(),
            options=options)

        if directory:
            try:
                self.xml_profile.export_profile_xml_file(dst_dir=directory)
            except PermissionError:
                QMessageBox.critical(
                    self, self.tr('Error!'),
                    self.tr("Access Denied for Writing to: {dir}".format(
                        dir=directory)))
            else:
                QMessageBox.information(
                    self, self.tr('Information!'),
                    self.tr('Conversion Profiles Successfully '
                            'Exported to: {dir}'.format(dir=directory)))

    def clear_media_list(self):
        """Clear media conversion list with user confirmation."""
        msg_box = QMessageBox(
            QMessageBox.Warning,
            self.tr('Warning!'),
            self.tr('Clear All Tasks?'),
            QMessageBox.NoButton, self)

        msg_box.addButton(self.tr("&Yes"), QMessageBox.AcceptRole)
        msg_box.addButton(self.tr("&No"), QMessageBox.RejectRole)

        if msg_box.exec_() == QMessageBox.AcceptRole:
            # If user says YES clear table of conversion tasks
            self.tb_tasks.clearContents()
            self.tb_tasks.setRowCount(0)
            # Clear MediaList.medias so it does not contain any element
            self.media_list.clear()
            # Update buttons so user cannot convert, clear, or stop if there
            # is no file in the list
            self.update_interface(convert=False,
                                  clear=False,
                                  remove=False,
                                  stop=False,
                                  stop_all=False,
                                  presets=False,
                                  profiles=False)

    def start_encoding(self):
        """Start the encoding process."""
        # Update tool buttons state
        self.update_interface(presets=False,
                              profiles=False,
                              add_profile=False,
                              convert=False,
                              clear=False,
                              remove=False,
                              output_dir=False,
                              settings=False)

        # Increment the the MediaList index
        self.media_list.running_index += 1

        running_media = self.media_list.get_running_file()
        running_media.conversion_profile.quality = self.tb_tasks.item(
            self.media_list.running_index, QUALITY).text()

        if (not running_media.status == STATUS.done and not
                running_media.status == STATUS.stopped):
            try:
                self.converter.start_encoding(
                    cmd=running_media.get_conversion_cmd(
                        output_dir=self.le_output.text()))
            except PermissionError:
                msg_box = QMessageBox(
                    QMessageBox.Critical,
                    self.tr('Error!'),
                    self.tr('Can not Write to Selected Output Directory'),
                    QMessageBox.Ok,
                    self)
                msg_box.show()
                self.media_list.running_index = -1
                self.update_interface(convert=False, stop=False,
                                      stop_all=False, remove=False)
        else:
            self.end_encoding_process()

    def stop_file_encoding(self):
        """Stop file encoding process and continue with the list."""
        # Set MediaFile.status attribute
        self.media_list.get_running_file().status = STATUS.stopped
        # Delete the file when conversion is stopped by the user
        self.media_list.get_running_file().delete_output(self.le_output.text())
        # Update the list duration and partial time for total progress bar
        self.total_duration = self.media_list.duration
        self.time_jump = 0.0
        self.partial_time = 0.0
        self.total_time = 0.0
        # Terminate the file encoding
        self.converter.stop_encoding()

    def stop_all_files_encoding(self):
        # Delete the file when conversion is stopped by the user
        self.media_list.get_running_file().delete_output(self.le_output.text())
        for media_file in self.media_list:
            # Set MediaFile.status attribute
            if media_file.status != STATUS.done:
                media_file.status = STATUS.stopped
                self.media_list.running_index = self.media_list.index(
                    media_file)
                self.tb_tasks.item(self.media_list.running_index,
                                   PROGRESS).setText(self.tr('Stopped!'))

        self.converter.stop_encoding()

        # Update the list duration and partial time for total progress bar
        self.total_duration = self.media_list.duration
        self.time_jump = 0.0
        self.partial_time = 0.0
        self.total_time = 0.0

    def finish_file_encoding(self):
        """Finish the file encoding process."""
        if not self.media_list.get_running_file().status == STATUS.stopped:
            # Close and kill the converter process
            self.converter.process.close()
            # Check if the process finished OK
            if self.converter.process.exitStatus() == QProcess.NormalExit:
                # When finished a file conversion...
                self.tb_tasks.item(self.media_list.running_index,
                                   PROGRESS).setText(self.tr('Done!'))
                self.media_list.get_running_file().status = STATUS.done
                self.pb_progress.setProperty("value", 0)
            # Attempt to end the conversion process
            self.end_encoding_process()
        else:
            # If the process was stopped
            if not self.converter.is_running:
                self.tb_tasks.item(self.media_list.running_index,
                                   PROGRESS).setText(self.tr('Stopped!'))
            # Attempt to end the conversion process
            self.end_encoding_process()

    def end_encoding_process(self):
        """End up the encoding process."""
        # Test if encoding process is finished
        if self.converter.encoding_done:
            msg_box = QMessageBox(
                QMessageBox.Information,
                self.tr('Information!'),
                self.tr('Encoding Process Successfully Finished!'),
                QMessageBox.Ok,
                self)
            msg_box.show()
            self.setWindowTitle(APPNAME + ' ' + VERSION)
            self.statusBar().showMessage(self.tr('Ready'))
            # Reset all progress related variables
            self.pb_progress.setProperty("value", 0)
            self.pb_total_progress.setProperty("value", 0)
            self.time_jump = 0.0
            self.partial_time = 0.0
            self.total_time = 0.0
            self.total_duration = self.media_list.duration
            # Reset the running_index
            self.media_list.running_index = -1
            # Update tool buttons
            self.update_interface(convert=False, stop=False,
                                  stop_all=False, remove=False)
        else:
            self.start_encoding()

    def _read_encoding_output(self):
        """Read the encoding output from the self.converter stdout."""
        time_pattern = re.compile(r'time=([0-9.:]+) ')
        ret = str(self.converter.process.readAll())
        time = time_pattern.findall(ret)

        if not time:
            return

        # Convert time to seconds
        if ':' in time[0]:
            time_in_secs = 0
            for part in time[0].split(':'):
                time_in_secs = 60 * time_in_secs + float(part)
        else:
            time_in_secs = float(time[0])

        # Calculate operation progress percent
        op_time = self.media_list.get_running_file().info.format_duration
        operation_progress = int(time_in_secs / float(op_time) * 100)

        # Update the table and the operation progress bar
        self.pb_progress.setProperty("value", operation_progress)
        self.tb_tasks.item(self.media_list.running_index, 3).setText(
            str(operation_progress) + "%")

        # Calculate total time
        if self.partial_time > time_in_secs:
            self.time_jump += self.partial_time
            self.total_time = self.time_jump + time_in_secs
            self.partial_time = time_in_secs
        else:
            self.total_time = self.time_jump + time_in_secs
            self.partial_time = time_in_secs

        # Calculate total progress percent
        total_progress = int(self.total_time /
                             float(self.total_duration) * 100)
        # Update the total progress bar
        self.pb_total_progress.setProperty("value", total_progress)

        # Avoid negative total_remaining_time
        try:
            total_remaining_time = write_time(self.total_duration -
                                              self.total_time)
        except ValueError:
            total_remaining_time = write_time(0)
        # Avoid negative operation_remaining_time
        try:
            operation_remaining_time = write_time(float(op_time) -
                                                  time_in_secs)
        except ValueError:
            operation_remaining_time = write_time(0)

        self.statusBar().showMessage(
            self.tr('Converting: {m}\t\t\t '
                    'Operation Remaining Time: {ort}\t\t\t '
                    'Total Remaining Time: {trt}').format(
                m=self.media_list.get_running_file().get_name(True),
                ort=operation_remaining_time,
                trt=total_remaining_time))

        current_file_name = basename(
            self.media_list.get_running_file().path)

        self.setWindowTitle(str(operation_progress) + '%' + '-' +
                            '[' + current_file_name + ']' +
                            ' - ' + APPNAME + ' ' + VERSION)

    def update_media_files_status(self):
        """Update file status."""
        # Current item
        item = self.tb_tasks.currentItem()
        if item is not None:
            # Update target_quality in table
            self.tb_tasks.item(item.row(), QUALITY).setText(
                str(self.cb_presets.currentText()))
            # Update table Progress field if file is: Done or Stopped
            if (self.media_list.get_file_status(item.row()) == STATUS.done or
                    self.media_list.get_file_status(
                        item.row()) == STATUS.stopped):
                self.tb_tasks.item(item.row(), PROGRESS).setText(
                    self.tr('To Convert'))
            # Update file Done or Stopped status
            self.media_list.set_file_status(file_index=item.row(),
                                            status=STATUS.todo)
            # Update total duration of the new tasks list
            self.total_duration = self.media_list.duration
            # Update the interface
            self.update_interface(clear=False, stop=False,
                                  stop_all=False, remove=False)
        else:
            if self.tb_tasks.rowCount():
                for i in range(self.tb_tasks.rowCount()):
                    self.tb_tasks.item(i, QUALITY).setText(
                        str(self.cb_presets.currentText()))

                    if (self.media_list.get_file_status(i) == STATUS.done or
                            self.media_list.get_file_status(i) ==
                            STATUS.stopped):
                        self.tb_tasks.item(i, PROGRESS).setText(
                            self.tr('To Convert'))

                self.update_interface(clear=False, stop=False,
                                      stop_all=False, remove=False)
            self._set_media_status()
            self.total_duration = self.media_list.duration

    def _set_media_status(self):
        """Update media files state of conversion."""
        for media_file in self.media_list:
            media_file.status = STATUS.todo
        self.media_list.running_index = -1

    def update_interface(self,
                         add=True,
                         convert=True,
                         clear=True,
                         remove=True,
                         stop=True,
                         stop_all=True,
                         presets=True,
                         profiles=True,
                         add_profile=True,
                         output_dir=True,
                         settings=True):
        self.add_media_file_action.setEnabled(add)
        self.convert_action.setEnabled(convert)
        self.clear_media_list_action.setEnabled(clear)
        self.remove_media_file_action.setEnabled(remove)
        self.stop_action.setEnabled(stop)
        self.stop_all_action.setEnabled(stop_all)
        self.cb_presets.setEnabled(presets)
        self.cb_profiles.setEnabled(profiles)
        self.add_profile_action.setEnabled(add_profile)
        self.tb_output.setEnabled(output_dir)
        self.tb_tasks.setCurrentItem(None)
        self.settings_action.setEnabled(settings)

    def _enable_remove_file_action(self):
        if not self.converter.is_running:
            self.remove_media_file_action.setEnabled(True)


class TargetQualityDelegate(QItemDelegate):
    """Combobox to select the target quality from the task list."""

    def __init__(self, parent=None):
        """Class initializer."""
        super(TargetQualityDelegate, self).__init__(parent)
        self.parent = parent

    def createEditor(self, parent, option, index):
        if index.column() == QUALITY:
            editor = QComboBox(parent)
            self.parent.populate_presets_combo(cb_presets=editor)
            editor.activated.connect(partial(self.update,
                                             editor,
                                             index))
            return editor
        else:
            return QItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.DisplayRole)
        if index.column() == QUALITY:
            i = editor.findText(text)
            if i == -1:
                i = 0
            editor.setCurrentIndex(i)
        else:
            QItemDelegate.setEditorData(self, editor, index)

    def update(self, editor, index):

        # Update table Progress field if file is: Done or Stopped
        if (self.parent.media_list.get_file_status(
                index.row()) == STATUS.done or
                self.parent.media_list.get_file_status(
                index.row()) == STATUS.stopped):
            self.parent.tb_tasks.item(index.row(), PROGRESS).setText(
                self.tr('To Convert'))
        # Update file status
        self.parent.media_list.set_file_status(file_index=index.row(),
                                               status=STATUS.todo)
        # Update total duration of the new tasks list
        self.parent.total_duration = self.parent.media_list.duration
        # Update the interface
        self.parent.update_interface(clear=False,
                                     stop=False,
                                     stop_all=False,
                                     remove=False)

        self.parent.tb_tasks.setEditTriggers(QAbstractItemView.NoEditTriggers)


def main():
    """Main app function."""
    # TODO: Make it run on Windows
    import sys
    from os.path import dirname, realpath, exists
    app = QApplication(sys.argv)
    file_path = dirname(realpath(__file__))
    locale = get_locale()
    appTranslator = QTranslator()
    if exists(file_path + '{0}translations{1}'.format(sep, sep)):
        appTranslator.load("{0}{1}translations{2}videomorph_{3}".format(
            file_path, sep, sep, locale))
    else:
        appTranslator.load(
            "{0}usr{1}share{2}videomorph{3}"
            "translations{4}videomorph_{5}".format(sep, sep, sep, sep, sep,
                                                   locale))
    app.installTranslator(appTranslator)
    qtTranslator = QTranslator()
    qtTranslator.load("qt_" + locale,
                      QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(qtTranslator)
    main_win = MMWindow()
    if main_win.check_conversion_lib():
        main_win.show()
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
