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
import sys
from collections import OrderedDict
from functools import partial
from os import sep
from os.path import dirname
from os.path import exists
from os.path import isdir

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
                             QCheckBox,
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
from . import CONV_LIB
from . import STATUS
from . import VERSION
from . import VIDEO_FILTERS
from . import videomorph_qrc
from .about import AboutVMDialog
from .converter import ConversionLib
from .converter import get_locale
from .converter import InvalidMetadataError
from .converter import media_files_generator
from .converter import MediaList
from .converter import which
from .converter import write_time
from .converter import XMLProfile
from .settings import SettingsDialog
from .addprofile import AddProfileDialog
# import performance

# Conversion tasks list table columns
NAME, DURATION, QUALITY, PROGRESS = range(4)


class VideoMorphMW(QMainWindow):
    """Video Morph Main Window class."""

    def __init__(self):
        """Class initializer."""
        super(VideoMorphMW, self).__init__()
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
        icon.addPixmap(QPixmap(':/logo/videomorph.png'))
        self.setWindowIcon(icon)
        # Define app central widget
        self.central_widget = QWidget(self)
        # Difine layouts
        self.vertical_layout = QVBoxLayout(self.central_widget)
        self.horizontal_layout = QHBoxLayout()
        self.vertical_layout_1 = QVBoxLayout()
        self.vertical_layout_2 = QVBoxLayout()
        # Define groups
        self._group_settings()
        self._fix_layout()
        self._group_tasks_list()
        self._group_output_directory()
        self._group_progress()
        # Add layouts
        self.horizontal_layout.addLayout(self.vertical_layout_2)
        self.vertical_layout.addLayout(self.horizontal_layout)
        # Set central widget
        self.setCentralWidget(self.central_widget)

        # Create actions
        self._create_actions()

        # Default Source directory
        self.source_dir = QDir.homePath()

        # XML Profile
        self.xml_profile = XMLProfile()
        self.xml_profile.create_profiles_xml_file()
        self.xml_profile.set_xml_root()

        # Populate PROFILES combo box
        self.populate_profiles_combo()

        # Create conversion library
        self.conversion_lib = ConversionLib()
        self.conversion_lib.converter.setup_process(
            reader=self._read_encoding_output,
            finisher=self._finish_file_encoding,
            process_channel=QProcess.MergedChannels)

        # Read app settings
        self._read_app_settings()

        # Create the conversion profile object only once
        self.conversion_profile = self.xml_profile.get_conversion_profile(
            profile_name=self.cb_profiles.currentText(),
            target_quality=self.cb_presets.currentText(),
            prober=self.conversion_lib.prober)

        # Create initial Settings if not created
        self._create_initial_settings()

        # Disable presets and profiles combo boxes
        self.cb_presets.setEnabled(False)
        self.cb_profiles.setEnabled(False)

        # Create app main menu bar
        self._create_main_menu()

        # Create the toolbar
        self._create_toolbar()

        # Create app status bar
        self._create_status_bar()

        # Set tool buttons style
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

    def _group_settings(self):
        """Settings group."""
        gb_settings = QGroupBox(self.central_widget)
        gb_settings.setTitle(self.tr('Conversion Presets'))
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
            gb_settings.sizePolicy().hasHeightForWidth())
        gb_settings.setSizePolicy(size_policy)
        horizontal_layout = QHBoxLayout(gb_settings)
        vertical_layout = QVBoxLayout()
        horizontal_layout_1 = QHBoxLayout()
        label = QLabel(self.tr('Convert To:'))
        horizontal_layout_1.addWidget(label)
        spacer_item = QSpacerItem(40,
                                  20,
                                  QSizePolicy.Expanding,
                                  QSizePolicy.Minimum)
        horizontal_layout_1.addItem(spacer_item)
        vertical_layout.addLayout(horizontal_layout_1)
        self.cb_profiles = QComboBox(
            gb_settings,
            statusTip=self.tr('Select a Video Format'),
            toolTip=self.tr('Select a Video Format'))
        self.cb_profiles.setMinimumSize(QSize(200, 0))
        vertical_layout.addWidget(self.cb_profiles)
        horizontal_layout_2 = QHBoxLayout()
        label = QLabel(self.tr('Target Quality:'))
        horizontal_layout_2.addWidget(label)
        spacer_item_1 = QSpacerItem(40, 20,
                                    QSizePolicy.Expanding,
                                    QSizePolicy.Minimum)
        horizontal_layout_2.addItem(spacer_item_1)
        vertical_layout.addLayout(horizontal_layout_2)
        self.cb_presets = QComboBox(
            gb_settings,
            statusTip=self.tr('Select a Video Target Quality'),
            toolTip=self.tr('Select a Video Target Quality'))
        self.cb_presets.setMinimumSize(QSize(200, 0))

        self.cb_profiles.currentIndexChanged.connect(partial(
            self.populate_presets_combo, self.cb_presets))

        self.cb_presets.activated.connect(self._update_media_files_status)

        vertical_layout.addWidget(self.cb_presets)
        self.chb_subtitle = QCheckBox(self.tr('Insert Subtitles if Available'),
                                      statusTip=self.tr(
                                          'Insert Subtitles if Available '
                                          'in Source Directory'),
                                      toolTip=self.tr(
                                          'Insert Subtitles if Available '
                                          'in Source Directory'))
        self.chb_subtitle.setEnabled(False)
        vertical_layout.addWidget(self.chb_subtitle)
        self.chb_delete = QCheckBox(self.tr('Delete Input Video '
                                            'Files When Finished'),
                                    statusTip=self.tr(
                                        'Delete Input Video '
                                        'Files When Finished'),
                                    toolTip=self.tr(
                                        'Delete Input Video '
                                        'Files When Finished'))
        self.chb_delete.setEnabled(False)
        vertical_layout.addWidget(self.chb_delete)
        horizontal_layout.addLayout(vertical_layout)
        self.vertical_layout_1.addWidget(gb_settings)

    def _group_tasks_list(self):
        """Define the Tasks Group arrangement."""
        gb_tasks = QGroupBox(self.central_widget)
        gb_tasks.setTitle(self.tr('List of Conversion Tasks'))
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
            gb_tasks.sizePolicy().hasHeightForWidth())
        gb_tasks.setSizePolicy(size_policy)
        horizontal_layout = QHBoxLayout(gb_tasks)
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
        horizontal_layout.addWidget(self.tb_tasks)
        self.vertical_layout_2.addWidget(gb_tasks)
        self.tb_tasks.doubleClicked.connect(self._update_edit_triggers)

    def _group_output_directory(self):
        """Define the output directory Group arrangement."""
        gb_output_dir = QGroupBox(self.central_widget)
        gb_output_dir.setTitle(self.tr('Output Directory'))
        vertical_layout = QVBoxLayout(gb_output_dir)
        vertical_layout_1 = QVBoxLayout()
        horizontal_layout = QHBoxLayout()
        self.le_output = QLineEdit(
            str(QDir.homePath()),
            statusTip=self.tr('Choose Output Directory'),
            toolTip=self.tr('Choose Output Directory'))
        self.le_output.setReadOnly(True)
        horizontal_layout.addWidget(self.le_output)
        self.tb_output = QToolButton(
            gb_output_dir,
            statusTip=self.tr('Choose Output Directory'),
            toolTip=self.tr('Choose Output Directory'))
        self.tb_output.setText('...')
        self.tb_output.clicked.connect(self.output_directory)
        horizontal_layout.addWidget(self.tb_output)
        vertical_layout_1.addLayout(horizontal_layout)
        vertical_layout.addLayout(vertical_layout_1)
        self.vertical_layout_2.addWidget(gb_output_dir)

    def _group_progress(self):
        """Define the Progress Group arrangement."""
        gb_progress = QGroupBox(self.central_widget)
        gb_progress.setTitle(self.tr('Progress'))
        vertical_layout = QVBoxLayout(gb_progress)
        label_progress = QLabel(gb_progress)
        label_progress.setText(self.tr('Operation Progress'))
        vertical_layout.addWidget(label_progress)
        self.pb_progress = QProgressBar(gb_progress)
        self.pb_progress.setProperty('value', 0)
        vertical_layout.addWidget(self.pb_progress)
        label_total_progress = QLabel(gb_progress)
        label_total_progress.setText(self.tr('Total Progress'))
        vertical_layout.addWidget(label_total_progress)
        self.pb_total_progress = QProgressBar(gb_progress)
        self.pb_total_progress.setProperty('value', 0)
        vertical_layout.addWidget(self.pb_total_progress)
        self.vertical_layout_2.addWidget(gb_progress)

    def _action_factory(self, text, callback, enabled=True, **kwargs):
        """Helper method used for creating actions.

        Args:
            text (str): Text to show in the action
            callback (method): Method to be called when action is triggered
            enabled (bool): Set the action enabled or not
        kwargs:
            checkable (bool): Turn the action checkable or not
            shortcut (str): Define the key shortcut to run the action
            icon (QIcon): Icon for the action
            tip (str): Tip to show in status bar or hint
        """
        action = QAction(text, self, triggered=callback)

        action.setEnabled(enabled)

        if 'icon' in kwargs:
            action.setIcon(kwargs['icon'])
        if 'shortcut' in kwargs:
            action.setShortcut(kwargs['shortcut'])
        if 'tip' in kwargs:
            action.setToolTip(kwargs['tip'])
            action.setStatusTip(kwargs['tip'])
        if 'checkable' in kwargs:
            action.setCheckable(kwargs['checkable'])

        return action

    def _create_actions(self):
        """Create actions."""
        self.add_media_file_action = self._action_factory(
            icon=self.style().standardIcon(QStyle.SP_DialogOpenButton),
            text=self.tr('&Open'),
            shortcut="Ctrl+O",
            tip=self.tr('Add Video Files to the List of Conversion Tasks'),
            callback=self.open_media_files)

        self.add_profile_action = self._action_factory(
            icon=self.style().standardIcon(QStyle.SP_DialogApplyButton),
            text=self.tr('&Add Customized Profile...'),
            shortcut="Ctrl+F",
            tip=self.tr('Add Customized Profile'),
            callback=self.add_costume_profile)

        self.export_profile_action = self._action_factory(
            icon=self.style().standardIcon(QStyle.SP_ArrowUp),
            text=self.tr('&Export Conversion Profiles...'),
            shortcut="Ctrl+E",
            tip=self.tr('Export Conversion Profiles'),
            callback=self.export_profiles)

        self.import_profile_action = self._action_factory(
            icon=self.style().standardIcon(QStyle.SP_DialogSaveButton),
            text=self.tr('&Import Conversion Profiles...'),
            shortcut="Ctrl+I",
            tip=self.tr('Import Conversion Profiles'),
            callback=self.import_profiles)

        self.restore_profile_action = self._action_factory(
            text=self.tr('&Restore to Default Conversion Profiles'),
            tip=self.tr('Restore to Default Conversion Profiles'),
            callback=self.restore_profiles)

        self.clear_media_list_action = self._action_factory(
            icon=self.style().standardIcon(QStyle.SP_TrashIcon),
            text=self.tr('Clear &List'),
            shortcut="Ctrl+Del",
            enabled=False,
            tip=self.tr('Clear the Video Files List'),
            callback=self.clear_media_list)

        self.remove_media_file_action = self._action_factory(
            icon=self.style().standardIcon(QStyle.SP_BrowserStop),
            text=self.tr('&Remove File'),
            shortcut="Del",
            enabled=False,
            tip=self.tr('Remove Video File from the List'),
            callback=self.remove_media_file)

        self.convert_action = self._action_factory(
            icon=self.style().standardIcon(QStyle.SP_MediaPlay),
            text=self.tr('&Convert'),
            shortcut="Ctrl+R",
            enabled=False,
            tip=self.tr('Start Conversion Process'),
            callback=self.start_encoding)

        self.stop_action = self._action_factory(
            icon=self.style().standardIcon(QStyle.SP_MediaStop),
            text=self.tr('&Stop'),
            shortcut="Ctrl+P",
            enabled=False,
            tip=self.tr('Stop Video File Conversion'),
            callback=self.stop_file_encoding)

        self.stop_all_action = self._action_factory(
            icon=self.style().standardIcon(QStyle.SP_DialogCancelButton),
            text=self.tr('S&top All'),
            shortcut="Ctrl+A",
            enabled=False,
            tip=self.tr('Stop All Video Conversion Tasks'),
            callback=self.stop_all_files_encoding)

        self.about_action = self._action_factory(
            icon=self.style().standardIcon(QStyle.SP_MessageBoxInformation),
            text=self.tr('&About VideoMorph...'),
            shortcut="Ctrl+H",
            tip=self.tr('About VideoMorph'),
            callback=self.about)

        self.exit_action = self._action_factory(
            icon=self.style().standardIcon(QStyle.SP_DialogCloseButton),
            text=self.tr('E&xit'),
            shortcut="Ctrl+Q",
            tip=self.tr('Exit VideoMorph'),
            callback=self.close)

        self.settings_action = self._action_factory(
            icon=self.style().standardIcon(QStyle.SP_FileDialogDetailedView),
            text=self.tr('&Settings...'),
            shortcut="Ctrl+S",
            tip=self.tr('Open VideoMorph Settings Dialog'),
            callback=self.settings)

    def _create_main_menu(self):
        """Create main app menu."""
        # File menu
        self.file_menu = self.menuBar().addMenu(self.tr('&File'))
        self.file_menu.addAction(self.add_media_file_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.settings_action)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.exit_action)
        # Edit menu
        self.edit_menu = self.menuBar().addMenu(self.tr('&Edit'))
        self.edit_menu.addAction(self.add_profile_action)
        self.edit_menu.addAction(self.export_profile_action)
        self.edit_menu.addAction(self.import_profile_action)
        self.edit_menu.addAction(self.restore_profile_action)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.clear_media_list_action)
        self.edit_menu.addAction(self.remove_media_file_action)
        # Conversion menu
        self.conversion_menu = self.menuBar().addMenu(self.tr('&Conversion'))
        self.conversion_menu.addAction(self.convert_action)
        self.conversion_menu.addAction(self.stop_action)
        self.conversion_menu.addSeparator()
        self.conversion_menu.addAction(self.stop_all_action)
        # Help menu
        self.help_menu = self.menuBar().addMenu(self.tr('&Help'))
        self.help_menu.addAction(self.about_action)

    def _create_toolbar(self):
        """Create a toolbar and add it to the interface."""
        self.tool_bar = QToolBar(self)
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
        # Add the toolbar to main window
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)

    def _create_status_bar(self):
        """Create app status bar."""
        self.statusBar().showMessage(self.tr('Ready'))

    def _fix_layout(self):
        """Fix widgets layout."""
        spacer_item = QSpacerItem(20,
                                  40,
                                  QSizePolicy.Minimum,
                                  QSizePolicy.Expanding)
        self.vertical_layout_1.addItem(spacer_item)
        self.horizontal_layout.addLayout(self.vertical_layout_1)

    def _update_edit_triggers(self):
        """Toggle Edit triggers on task table."""
        if (int(self.tb_tasks.currentColumn()) == QUALITY and not
                self.conversion_lib.converter.is_running):
            self.tb_tasks.setEditTriggers(QAbstractItemView.AllEditTriggers)
        else:
            self.tb_tasks.setEditTriggers(QAbstractItemView.NoEditTriggers)

    @staticmethod
    def _get_settings_file():
        return QSettings('{0}{1}.videomorph{2}config.ini'.format(
            QDir.homePath(), sep, sep), QSettings.IniFormat)

    def _create_initial_settings(self):
        """Create initial settings file."""
        if not exists('{0}{1}.videomorph{2}config.ini'.format(
                QDir.homePath(), sep, sep)):
            self._write_app_settings(pos=QPoint(100, 50),
                                     size=QSize(1096, 510),
                                     profile_index=0,
                                     preset_index=0)

    def _read_app_settings(self):
        """Read the app settings."""
        settings = self._get_settings_file()
        pos = settings.value("pos", QPoint(600, 200), type=QPoint)
        size = settings.value("size", QSize(1096, 510), type=QSize)
        self.resize(size)
        self.move(pos)
        if 'profile_index' and 'preset_index' in settings.allKeys():
            profile = settings.value('profile_index')
            preset = settings.value('preset_index')
            self.cb_profiles.setCurrentIndex(int(profile))
            self.cb_presets.setCurrentIndex(int(preset))
        if 'output_dir' in settings.allKeys():
            self.le_output.setText(str(settings.value('output_dir')))
        if 'source_dir' in settings.allKeys():
            self.source_dir = str(settings.value('source_dir'))
        if 'conversion_lib' in settings.allKeys():
            self.conversion_lib.name = settings.value(
                'conversion_lib')

    def _write_app_settings(self, **app_settings):
        """Write app settings on exit.

        Args:
            app_settings (OrderedDict): OrderedDict to collect all app settings
        """
        settings_file = self._get_settings_file()

        settings = OrderedDict(
            pos=self.pos(),
            size=self.size(),
            profile_index=self.cb_profiles.currentIndex(),
            preset_index=self.cb_presets.currentIndex(),
            source_dir=self.source_dir,
            output_dir=self.le_output.text(),
            conv_lib=self.conversion_lib.name)

        if app_settings:
            settings.update(app_settings)

        for key, setting in settings.items():
            settings_file.setValue(key, setting)

    def _reset_progress_times(self):
        """Reset the variables used to calculate progress."""
        self.time_jump = 0.0
        self.partial_time = 0.0
        self.total_time = 0.0

    def check_conversion_lib(self):
        """Check if ffmpeg or/and avconv are installed on the system."""
        if self.conversion_lib.name is not None:
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

    def about(self):
        """Show About dialog."""
        about_dlg = AboutVMDialog(parent=self)
        about_dlg.exec_()

    def settings(self):
        """Open a Setting Dialog to define the conversion library to use."""
        settings_dlg = SettingsDialog(parent=self)
        if self.conversion_lib.name == CONV_LIB.ffmpeg:
            settings_dlg.radio_btn_ffmpeg.setChecked(True)
        elif self.conversion_lib.name == CONV_LIB.avconv:
            settings_dlg.radio_btn_avconv.setChecked(True)

        if not which(CONV_LIB.ffmpeg):
            settings_dlg.radio_btn_ffmpeg.setEnabled(False)
        elif not which(CONV_LIB.avconv):
            settings_dlg.radio_btn_avconv.setEnabled(False)

        if settings_dlg.exec_():
            if settings_dlg.radio_btn_ffmpeg.isChecked():
                self.conversion_lib.name = CONV_LIB.ffmpeg
            elif settings_dlg.radio_btn_avconv.isChecked():
                self.conversion_lib.name = CONV_LIB.avconv

    def populate_profiles_combo(self):
        """Populate profiles combobox."""
        # Clear combobox content
        self.cb_profiles.clear()
        # Populate the combobox with new data
        self.cb_profiles.addItems(self.xml_profile.get_qualities_per_profile(
            locale=get_locale()).keys())

    def populate_presets_combo(self, cb_presets):
        """Populate presets combobox.

        Args:
            cb_presets (QComboBox): List all available presets
        """
        current_profile = self.cb_profiles.currentText()
        if current_profile != '':
            cb_presets.clear()
            cb_presets.addItems(self.xml_profile.get_qualities_per_profile(
                locale=get_locale())[current_profile])
            self._update_media_files_status()

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

    def closeEvent(self, event):
        """Things to todo on close."""
        # Disconnect the finished signal
        self.conversion_lib.converter.finished_disconnect(
            self._finish_file_encoding)
        # Close communication and kill the encoding process
        if self.conversion_lib.converter.is_running:
            self.conversion_lib.converter.close()
            self.conversion_lib.converter.kill()
        # Save settings
        self._write_app_settings()

        event.accept()

    # @performance.measure_exec_time
    def _fill_media_list(self, files_paths):
        """Fill MediaList object with MediaFile objects."""
        for file in media_files_generator(
                files_paths=files_paths,
                conversion_profile=self.conversion_profile):
            try:
                self.media_list.add_file(file)
            except InvalidMetadataError:
                msg_box = QMessageBox(
                    QMessageBox.Critical,
                    self.tr('Error!'),
                    self.tr('Invalid Video File Information for: {fn}. '
                            'File not Added to Conversion List'.format(
                                fn=file.get_name(
                                    with_extension=True))),
                    QMessageBox.Ok,
                    self)
                msg_box.show()
                # An error occurred, so interface get initial state back, but
                # only if the list is empty
                if not self.media_list.length:
                    self.update_interface(convert=False,
                                          clear=False,
                                          remove=False,
                                          stop=False,
                                          stop_all=False,
                                          presets=False,
                                          profiles=False,
                                          subtitles_chb=False,
                                          delete_chb=False)

        return self.media_list

    def _load_files(self, source_dir=QDir.homePath()):
        """Load video files."""
        source_dir = source_dir if isdir(source_dir) else QDir.homePath()

        # Dialog title
        title = self.tr('Select Video Files')
        # Media filters
        video_filters = (self.tr('Video Files') + ' ' +
                         '(' + VIDEO_FILTERS + ')')

        # Select media files and store their path
        files_paths, _ = QFileDialog.getOpenFileNames(self,
                                                      title,
                                                      source_dir,
                                                      video_filters)

        if not files_paths:
            self.source_dir = source_dir
            return None
        else:
            # Update the source directory
            self.source_dir = dirname(files_paths[0])

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
                row=row, column=NAME)

            self._insert_table_item(
                item_text=str(write_time(
                    media_file.get_info('format_duration'))),
                row=row, column=DURATION)

            self._insert_table_item(
                item_text=str(self.cb_presets.currentText()),
                row=row, column=QUALITY)

            self._insert_table_item(item_text=self.tr('To Convert'),
                                    row=row, column=PROGRESS)

    def add_media_files(self, *files):
        """Add video files to conversion list.

        Args:
            files (list): List of video file paths
        """
        # Update tool buttons so you can convert, or add_file, or clear...
        # only if there is not a conversion process running
        if self.conversion_lib.converter.is_running:
            self.update_interface(presets=False,
                                  profiles=False,
                                  subtitles_chb=False,
                                  convert=False,
                                  clear=False,
                                  remove=False,
                                  output_dir=False,
                                  settings=False,
                                  delete_chb=False)
        else:
            # This rewind the encoding list if the encoding process is
            # not running
            self.media_list.position = -1
            # Update ui
            self.update_interface(stop=False, stop_all=False, remove=False)

        self._fill_media_list(files)

        self._create_table()

        # After adding files to the list, recalculate the list duration
        self.total_duration = self.media_list.duration

    def open_media_files(self):
        """Add media files to the list of conversion tasks."""
        files_paths = self._load_files(source_dir=self.source_dir)
        # If no file is selected then return
        if files_paths is None:
            return

        self.add_media_files(*files_paths)

    def remove_media_file(self):
        """Remove selected media file from the list."""
        file_row = self.tb_tasks.currentItem().row()

        msg_box = QMessageBox(
            QMessageBox.Warning,
            self.tr('Warning!'),
            self.tr('Remove Video File from the List of Tasks?'),
            QMessageBox.NoButton, self)

        msg_box.addButton(self.tr("&Yes"), QMessageBox.AcceptRole)
        msg_box.addButton(self.tr("&No"), QMessageBox.RejectRole)

        if msg_box.exec_() == QMessageBox.AcceptRole:
            # Delete file from table
            self.tb_tasks.removeRow(file_row)
            # Remove file from self.media_list
            self.media_list.delete_file(file_index=file_row)
            self.total_duration = self.media_list.duration

        # If all files are deleted... update the interface
        if not self.tb_tasks.rowCount():
            self.update_interface(convert=False,
                                  clear=False,
                                  remove=False,
                                  stop=False,
                                  stop_all=False,
                                  presets=False,
                                  profiles=False,
                                  subtitles_chb=False,
                                  delete_chb=False)

    def add_costume_profile(self):
        """Show dialog for adding conversion profiles."""
        add_profile_dlg = AddProfileDialog(parent=self)
        add_profile_dlg.exec_()

    def _export_import_profiles(self, func, path, msg_info):
        try:
            func(path)
        except PermissionError:
            QMessageBox.critical(
                self, self.tr('Error!'),
                self.tr('Access Denied for Writing to Selected Directory'))
        else:
            QMessageBox.information(
                self, self.tr('Information!'),
                msg_info)

    def export_profiles(self):
        """Export conversion profiles."""
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(
            self,
            self.tr('Export to Directory'),
            QDir.homePath(),
            options=options)

        if directory:
            msg_info = self.tr('Conversion Profiles Successfully Exported')

            self._export_import_profiles(
                func=self.xml_profile.export_profile_xml_file,
                path=directory, msg_info=msg_info)

    def import_profiles(self):
        """Import conversion profiles."""
        # Dialog title
        title = self.tr('Select a Profiles File')
        # Media filters
        profile_filters = (self.tr('Profiles Files ') + '(*.xml)')

        # Select media files and store their path
        file_path, _ = QFileDialog.getOpenFileName(self,
                                                   title,
                                                   QDir.homePath(),
                                                   profile_filters)
        if file_path:
            msg_info = self.tr('Conversion Profiles Successfully Imported')

            self._export_import_profiles(
                func=self.xml_profile.import_profile_xml,
                path=file_path, msg_info=msg_info)

    def restore_profiles(self):
        """Restore default profiles."""
        self.xml_profile.create_profiles_xml_file(restore=True)
        self.xml_profile.set_xml_root()
        self.populate_profiles_combo()

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
            # Clear MediaList so it contains no element
            self.media_list.clear()
            # Update buttons so user cannot convert, clear, or stop if there
            # is no file in the list
            self.update_interface(convert=False,
                                  clear=False,
                                  remove=False,
                                  stop=False,
                                  stop_all=False,
                                  presets=False,
                                  profiles=False,
                                  subtitles_chb=False,
                                  delete_chb=False)

    def start_encoding(self):
        """Start the encoding process."""
        # Update tool buttons state
        self.update_interface(presets=False,
                              profiles=False,
                              subtitles_chb=False,
                              add_costume_profile=False,
                              convert=False,
                              clear=False,
                              remove=False,
                              output_dir=False,
                              settings=False,
                              delete_chb=False)

        # Increment the the MediaList index
        self.media_list.position += 1

        running_media = self.media_list.running_file
        running_media.conversion_profile.quality = self.tb_tasks.item(
            self.media_list.position, QUALITY).text()

        if (running_media.status != STATUS.done and
                running_media.status != STATUS.stopped):
            try:
                self.conversion_lib.converter.start_encoding(
                    cmd=running_media.get_conversion_cmd(
                        output_dir=self.le_output.text(),
                        subtitle=bool(self.chb_subtitle.checkState())))
            except PermissionError:
                msg_box = QMessageBox(
                    QMessageBox.Critical,
                    self.tr('Error!'),
                    self.tr('Can not Write to Selected Output Directory'),
                    QMessageBox.Ok,
                    self)
                msg_box.show()
                self.media_list.position = -1
                self.update_interface(convert=False, stop=False,
                                      stop_all=False, remove=False)
        else:
            self._end_encoding_process()

    def stop_file_encoding(self):
        """Stop file encoding process and continue with the list."""
        # Set MediaFile.status attribute
        self.media_list.running_file.status = STATUS.stopped
        # Delete the file when conversion is stopped by the user
        self.media_list.running_file.delete_output(
            output_path=self.le_output.text())
        # Update the list duration and partial time for total progress bar
        self.total_duration = self.media_list.duration
        self._reset_progress_times()
        # Terminate the file encoding
        self.conversion_lib.converter.stop_encoding()

    def stop_all_files_encoding(self):
        """Stop the conversion process for all the files in list."""
        # Delete the file when conversion is stopped by the user
        self.media_list.running_file.delete_output(self.le_output.text())
        for media_file in self.media_list:
            # Set MediaFile.status attribute
            if media_file.status != STATUS.done:
                media_file.status = STATUS.stopped
                self.media_list.position = self.media_list.index(
                    media_file)
                self.tb_tasks.item(self.media_list.position,
                                   PROGRESS).setText(self.tr('Stopped!'))

        self.conversion_lib.converter.stop_encoding()

        # Update the list duration and partial time for total progress bar
        self.total_duration = self.media_list.duration
        self._reset_progress_times()

    def _finish_file_encoding(self):
        """Finish the file encoding process."""
        if self.media_list.running_file.status != STATUS.stopped:
            # Close and kill the converter process
            self.conversion_lib.converter.close()
            # Check if the process finished OK
            if (self.conversion_lib.converter.exit_status() ==
                    QProcess.NormalExit):
                # When finished a file conversion...
                self.tb_tasks.item(self.media_list.position,
                                   PROGRESS).setText(self.tr('Done!'))
                self.media_list.running_file.status = STATUS.done
                self.pb_progress.setProperty("value", 0)
                if self.chb_delete.checkState():
                    self.media_list.running_file.delete_input()
            # Attempt to end the conversion process
            self._end_encoding_process()
        else:
            # If the process was stopped
            if not self.conversion_lib.converter.is_running:
                self.tb_tasks.item(self.media_list.position,
                                   PROGRESS).setText(self.tr('Stopped!'))
            # Attempt to end the conversion process
            self._end_encoding_process()

    def _end_encoding_process(self):
        """End up the encoding process."""
        # Test if encoding process is finished
        if self.conversion_lib.converter.encoding_done(self.media_list):
            if not self.media_list.all_stopped:
                msg_box = QMessageBox(
                    QMessageBox.Information,
                    self.tr('Information!'),
                    self.tr('Encoding Process Successfully Finished!'),
                    QMessageBox.Ok,
                    self)
                msg_box.show()
            else:
                msg_box = QMessageBox(
                    QMessageBox.Information,
                    self.tr('Information!'),
                    self.tr('Encoding Process Stopped by the User!'),
                    QMessageBox.Ok,
                    self)
                msg_box.show()
            self.setWindowTitle(APPNAME + ' ' + VERSION)
            self.statusBar().showMessage(self.tr('Ready'))
            self.chb_delete.setChecked(False)
            # Reset all progress related variables
            self.pb_progress.setProperty("value", 0)
            self.pb_total_progress.setProperty("value", 0)
            self._reset_progress_times()
            self.total_duration = self.media_list.duration
            # Reset the position
            self.media_list.position = -1
            # Update tool buttons
            self.update_interface(convert=False, stop=False,
                                  stop_all=False, remove=False)
        else:
            self.start_encoding()

    def _read_encoding_output(self):
        """Read the encoding output from the converter stdout."""
        time_pattern = re.compile(r'time=([0-9.:]+) ')
        process_output = str(self.conversion_lib.converter.read_all())
        time_read = time_pattern.findall(process_output)

        if not time_read:
            return

        # Convert time to seconds
        if ':' in time_read[0]:
            time_in_secs = 0.0
            for part in time_read[0].split(':'):
                time_in_secs = 60 * time_in_secs + float(part)
        else:
            time_in_secs = float(time_read[0])

        # Calculate operation progress percent
        op_time = self.media_list.running_file.get_info('format_duration')
        operation_progress = int(time_in_secs / float(op_time) * 100)

        # Update the table and the operation progress bar
        self.pb_progress.setProperty("value", operation_progress)
        self.tb_tasks.item(self.media_list.position, 3).setText(
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
                        m=self.media_list.running_file.get_name(True),
                        ort=operation_remaining_time,
                        trt=total_remaining_time))

        current_file_name = self.media_list.running_file.get_name(
            with_extension=True)

        self.setWindowTitle(str(operation_progress) + '%' + '-' +
                            '[' + current_file_name + ']' +
                            ' - ' + APPNAME + ' ' + VERSION)

    def _update_media_files_status(self):
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
            rows = self.tb_tasks.rowCount()
            if rows:
                for row in range(rows):
                    self.tb_tasks.item(row, QUALITY).setText(
                        str(self.cb_presets.currentText()))

                    if (self.media_list.get_file_status(row) == STATUS.done or
                            self.media_list.get_file_status(row) ==
                            STATUS.stopped):
                        self.tb_tasks.item(row, PROGRESS).setText(
                            self.tr('To Convert'))

                self.update_interface(clear=False, stop=False,
                                      stop_all=False, remove=False)
            self._set_media_status()
            self.total_duration = self.media_list.duration

    def _set_media_status(self):
        """Update media files state of conversion."""
        for media_file in self.media_list:
            media_file.status = STATUS.todo
        self.media_list.position = -1

    def update_interface(self, **i_vars):
        """Update the interface status.

        Args:
            i_vars (dict): Dict to collect all the interface variables
        """
        variables = dict(add=True,
                         convert=True,
                         clear=True,
                         remove=True,
                         stop=True,
                         stop_all=True,
                         presets=True,
                         profiles=True,
                         add_costume_profile=True,
                         output_dir=True,
                         settings=True,
                         subtitles_chb=True,
                         delete_chb=True)

        variables.update(i_vars)

        self.add_media_file_action.setEnabled(variables['add'])
        self.convert_action.setEnabled(variables['convert'])
        self.clear_media_list_action.setEnabled(variables['clear'])
        self.remove_media_file_action.setEnabled(variables['remove'])
        self.stop_action.setEnabled(variables['stop'])
        self.stop_all_action.setEnabled(variables['stop_all'])
        self.cb_presets.setEnabled(variables['presets'])
        self.cb_profiles.setEnabled(variables['profiles'])
        self.add_profile_action.setEnabled(variables['add_costume_profile'])
        self.tb_output.setEnabled(variables['output_dir'])
        self.chb_subtitle.setEnabled(variables['subtitles_chb'])
        self.chb_delete.setEnabled(variables['delete_chb'])
        self.settings_action.setEnabled(variables['settings'])
        self.tb_tasks.setCurrentItem(None)

    def _enable_remove_file_action(self):
        if not self.conversion_lib.converter.is_running:
            self.remove_media_file_action.setEnabled(True)


class TargetQualityDelegate(QItemDelegate):
    """Combobox to select the target quality from the task list."""

    def __init__(self, parent=None):
        """Class initializer."""
        super(TargetQualityDelegate, self).__init__(parent)
        self.parent = parent

    def createEditor(self, parent, option, index):
        """Create a ComboBox to edit the Target Quality."""
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
        """Set Target Quality."""
        text = index.model().data(index, Qt.DisplayRole)
        if index.column() == QUALITY:
            i = editor.findText(text)
            if i == -1:
                i = 0
            editor.setCurrentIndex(i)
        else:
            QItemDelegate.setEditorData(self, editor, index)

    def update(self, editor, index):
        """Update several things in the interface."""
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
    # Create the app
    app = QApplication(sys.argv)
    # Set app translator
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

    main_win = VideoMorphMW()
    if main_win.check_conversion_lib():
        # If it is running on console
        if len(sys.argv) > 1:
            from .converter import run_on_console
            run_on_console(app, main_win)
        else:
            main_win.show()
            sys.exit(app.exec_())


if __name__ == '__main__':
    main()
