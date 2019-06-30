# -*- coding: utf-8 -*-
#
# File name: videomorph.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
#   Copyright 2016-2018 VideoMorph Development Team

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

from collections import OrderedDict
from functools import partial
from os.path import join as join_path
from os.path import dirname
from os.path import exists
from os.path import isdir
from os.path import isfile

from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QDir
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import qApp


from videomorph.converter import APP_NAME
from videomorph.converter import BASE_DIR
from videomorph.converter import LOCALE
from videomorph.converter import STATUS
from videomorph.converter import SYS_PATHS
from videomorph.converter import VERSION
from videomorph.converter import VIDEO_FILTERS
from videomorph.converter import VM_PATHS
from videomorph.converter.console import search_directory_recursively
from videomorph.converter.conversionlib import ConversionLib
from videomorph.converter.media import MediaList
from videomorph.converter.platformdeps import PlayerNotFoundError
from videomorph.converter.platformdeps import launcher_factory
from videomorph.converter.profile import ConversionProfile
from videomorph.converter.utils import write_time
from . import COLUMNS
from . import videomorph_qrc
from .vmwidgets import TasksListTable
from .about import AboutVMDialog
from .addprofile import AddProfileDialog
from .changelog import ChangelogDialog
from .info import InfoDialog


class VideoMorphMW(QMainWindow):
    """VideoMorph Main Window class."""

    def __init__(self):
        """Class initializer."""
        super(VideoMorphMW, self).__init__()
        self.title = APP_NAME + ' ' + VERSION
        self.icon = self._get_app_icon()
        self.source_dir = QDir.homePath()
        self.media_list_duration = 0.0
        self.no_library_msg = self.tr('Ffmpeg Library not Found'
                                      ' in your System')

        self._setup_ui()
        self._setup_model()

        self.populate_profiles_combo()

        self._load_app_settings()

    def _setup_model(self):
        """Setup the app model."""
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

    def _setup_ui(self):
        """Setup UI."""
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.resize(950, 500)
        self.setWindowTitle(self.title)
        self.setWindowIcon(self.icon)
        self._create_actions()
        self._create_general_layout()
        self._create_main_menu()
        self._create_toolbar()
        self._create_status_bar()
        self._create_sys_tray_icon(self.icon)
        self._create_context_menu()
        self._update_ui_when_no_file()

    def _get_app_icon(self):
        """Set window icon."""
        icon = QIcon()
        icon.addPixmap(QPixmap(':/icons/videomorph.ico'))
        return icon

    def _create_general_layout(self):
        """General layout."""
        general_layout = QHBoxLayout(self.central_widget)
        settings_layout = QVBoxLayout()
        settings_layout.addWidget(self._group_settings())
        conversion_layout = QVBoxLayout()
        conversion_layout.addWidget(self._group_tasks_list())
        conversion_layout.addWidget(self._group_output_directory())
        conversion_layout.addWidget(self._group_progress())
        general_layout.addLayout(settings_layout)
        general_layout.addLayout(conversion_layout)

    def _create_sys_tray_icon(self, icon):
        self.tray_icon_menu = QMenu(self)
        self.tray_icon_menu.addAction(self.open_media_file_action)
        self.tray_icon_menu.addAction(self.open_media_dir_action)
        self.tray_icon_menu.addSeparator()
        self.tray_icon_menu.addAction(self.clear_media_list_action)
        self.tray_icon_menu.addSeparator()
        self.tray_icon_menu.addAction(self.convert_action)
        self.tray_icon_menu.addAction(self.stop_all_action)
        self.tray_icon_menu.addSeparator()
        self.tray_icon_menu.addAction(self.exit_action)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setContextMenu(self.tray_icon_menu)

        self.tray_icon.show()

    def _group_settings(self):
        """Settings group."""
        settings_gb = QGroupBox(self.central_widget)
        settings_gb.setTitle(self.tr('Conversion Profile'))
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
            settings_gb.sizePolicy().hasHeightForWidth())
        settings_gb.setSizePolicy(size_policy)

        settings_layout = QVBoxLayout()

        convert_label = QLabel(self.tr('Convert to:'))
        settings_layout.addWidget(convert_label)

        profile_tip = self.tr('Select a Video Format')
        self.profiles_combo = QComboBox(settings_gb,
                                        statusTip=profile_tip,
                                        toolTip=profile_tip)
        self.profiles_combo.setMinimumSize(QSize(200, 0))
        self.profiles_combo.setIconSize(QSize(22, 22))
        settings_layout.addWidget(self.profiles_combo)

        quality_label = QLabel(self.tr('Target Quality:'))
        settings_layout.addWidget(quality_label)

        preset_tip = self.tr('Select a Video Target Quality')
        self.quality_combo = QComboBox(settings_gb,
                                       statusTip=preset_tip,
                                       toolTip=preset_tip)
        self.quality_combo.setMinimumSize(QSize(200, 0))
        self.profiles_combo.currentIndexChanged.connect(partial(
            self.populate_quality_combo, self.quality_combo))
        self.quality_combo.activated.connect(self._update_media_files_status)
        settings_layout.addWidget(self.quality_combo)

        options_label = QLabel(self.tr('Other Options:'))
        settings_layout.addWidget(options_label)

        sub_tip = self.tr('Insert Subtitles if Available in Source Directory')
        self.subtitle_chb = QCheckBox(self.tr('Insert Subtitles if Available'),
                                      statusTip=sub_tip,
                                      toolTip=sub_tip)
        self.subtitle_chb.clicked.connect(self._on_modify_conversion_option)
        settings_layout.addWidget(self.subtitle_chb)

        del_text = self.tr('Delete Input Video Files when Finished')
        self.delete_chb = QCheckBox(del_text,
                                    statusTip=del_text,
                                    toolTip=del_text)
        self.delete_chb.clicked.connect(self._on_modify_conversion_option)
        settings_layout.addWidget(self.delete_chb)

        tag_text = self.tr('Use Format Tag in Output Video File Name')
        tag_tip_text = (tag_text + '. ' +
                        self.tr('Useful when Converting a '
                                'Video File to Multiples Formats'))
        self.tag_chb = QCheckBox(tag_text,
                                 statusTip=tag_tip_text,
                                 toolTip=tag_tip_text)
        self.tag_chb.clicked.connect(self._on_modify_conversion_option)
        settings_layout.addWidget(self.tag_chb)

        shutdown_text = self.tr('Shutdown Computer when Conversion Finished')
        self.shutdown_chb = QCheckBox(shutdown_text,
                                      statusTip=shutdown_text,
                                      toolTip=shutdown_text)
        settings_layout.addWidget(self.shutdown_chb)
        settings_layout.addStretch()

        settings_gb.setLayout(settings_layout)

        return settings_gb

    def _group_tasks_list(self):
        """Define the Tasks Group arrangement."""
        tasks_gb = QGroupBox(self.central_widget)
        tasks_text = self.tr('List of Conversion Tasks')
        tasks_gb.setTitle(tasks_text)
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(
            tasks_gb.sizePolicy().hasHeightForWidth())
        tasks_gb.setSizePolicy(size_policy)

        tasks_layout = QVBoxLayout()

        self.tasks_table = TasksListTable(parent=tasks_gb,
                                          window=self)
        self.tasks_table.cellPressed.connect(self._enable_context_menu_action)
        self.tasks_table.doubleClicked.connect(self._update_edit_triggers)
        tasks_layout.addWidget(self.tasks_table)
        tasks_gb.setLayout(tasks_layout)

        return tasks_gb

    def _group_output_directory(self):
        """Define the output directory Group arrangement."""
        output_dir_gb = QGroupBox(self.central_widget)
        output_dir_gb.setTitle(self.tr('Output Directory'))

        output_dir_layout = QHBoxLayout(output_dir_gb)

        outputdir_tip = self.tr('Choose Output Directory')
        self.output_edit = QLineEdit(str(QDir.homePath()),
                                     statusTip=outputdir_tip,
                                     toolTip=outputdir_tip)
        self.output_edit.setReadOnly(True)
        output_dir_layout.addWidget(self.output_edit)

        outputbtn_tip = self.tr('Choose Output Directory')
        self.output_btn = QToolButton(output_dir_gb,
                                      statusTip=outputbtn_tip,
                                      toolTip=outputbtn_tip)
        self.output_btn.setIcon(QIcon(':/icons/output-folder.png'))
        self.output_btn.clicked.connect(self.output_directory)
        output_dir_layout.addWidget(self.output_btn)

        output_dir_gb.setLayout(output_dir_layout)

        return output_dir_gb

    def _group_progress(self):
        """Define the Progress Group arrangement."""
        progress_gb = QGroupBox(self.central_widget)
        progress_gb.setTitle(self.tr('Progress'))

        progress_layout = QVBoxLayout()

        progress_label = QLabel(self.tr('Operation Progress'))
        progress_layout.addWidget(progress_label)

        self.operation_pb = QProgressBar()
        self.operation_pb.setProperty('value', 0)
        progress_layout.addWidget(self.operation_pb)

        total_progress_label = QLabel(self.tr('Total Progress'))
        progress_layout.addWidget(total_progress_label)

        self.total_pb = QProgressBar()
        self.total_pb.setProperty('value', 0)
        progress_layout.addWidget(self.total_pb)

        progress_gb.setLayout(progress_layout)

        return progress_gb

    def _action_factory(self, **kwargs):
        """Helper method used for creating actions.

        Args:
            text (str): Text to show in the action
            callback (method): Method to be called when action is triggered
        kwargs:
            checkable (bool): Turn the action checkable or not
            shortcut (str): Define the key shortcut to run the action
            icon (QIcon): Icon for the action
            tip (str): Tip to show in status bar or hint
        """
        action = QAction(kwargs['text'], self, triggered=kwargs['callback'])

        try:
            action.setIcon(kwargs['icon'])
        except KeyError:
            pass

        try:
            action.setShortcut(kwargs['shortcut'])
        except KeyError:
            pass

        try:
            action.setToolTip(kwargs['tip'])
            action.setStatusTip(kwargs['tip'])
        except KeyError:
            pass

        try:
            action.setCheckable(kwargs['checkable'])
        except KeyError:
            pass

        return action

    def _create_actions(self):
        """Create actions."""
        actions = {'open_media_file_action':
                   dict(icon=QIcon(':/icons/video-file.png'),
                        text=self.tr('&Add Files...'),
                        shortcut="Ctrl+O",
                        tip=self.tr('Add Video Files to the '
                                    'List of Conversion Tasks'),
                        callback=self.open_media_files),

                   'open_media_dir_action':
                   dict(icon=QIcon(':/icons/add-folder.png'),
                        text=self.tr('Add &Directory...'),
                        shortcut="Ctrl+D",
                        tip=self.tr('Add all the Video Files in a Directory '
                                    'to the List of Conversion Tasks'),
                        callback=self.open_media_dir),

                   'add_profile_action':
                   dict(icon=QIcon(':/icons/add-profile.png'),
                        text=self.tr('&Add Customized Profile...'),
                        shortcut="Ctrl+F",
                        tip=self.tr('Add Customized Profile'),
                        callback=self.add_customized_profile),

                   'export_profile_action':
                   dict(icon=QIcon(':/icons/export.png'),
                        text=self.tr('&Export Conversion Profiles...'),
                        shortcut="Ctrl+E",
                        tip=self.tr('Export Conversion Profiles'),
                        callback=self.export_profiles),

                   'import_profile_action':
                   dict(icon=QIcon(':/icons/import.png'),
                        text=self.tr('&Import Conversion Profiles...'),
                        shortcut="Ctrl+I",
                        tip=self.tr('Import Conversion Profiles'),
                        callback=self.import_profiles),

                   'restore_profile_action':
                   dict(icon=QIcon(':/icons/default-profile.png'),
                        text=self.tr('&Restore the Default '
                                     'Conversion Profiles'),
                        tip=self.tr('Restore the Default Conversion Profiles'),
                        callback=self.restore_profiles),

                   'play_input_media_file_action':
                   dict(icon=QIcon(':/icons/video-player-input.png'),
                        text=self.tr('Play Input Video File'),
                        callback=self.play_input_media_file),

                   'play_output_media_file_action':
                   dict(icon=QIcon(':/icons/video-player-output.png'),
                        text=self.tr('Play Output Video File'),
                        callback=self.play_output_media_file),

                   'clear_media_list_action':
                   dict(icon=QIcon(':/icons/clear-list.png'),
                        text=self.tr('Clear &List'),
                        shortcut="Ctrl+Del",
                        tip=self.tr('Remove all Video Files from the '
                                    'List of Conversion Tasks'),
                        callback=self.clear_media_list),

                   'remove_media_file_action':
                   dict(icon=QIcon(':/icons/remove-file.png'),
                        text=self.tr('&Remove File'),
                        shortcut="Del",
                        tip=self.tr('Remove Selected Video File from the '
                                    'List of Conversion Tasks'),
                        callback=self.remove_media_file),

                   'convert_action':
                   dict(icon=QIcon(':/icons/convert.png'),
                        text=self.tr('&Convert'),
                        shortcut="Ctrl+R",
                        tip=self.tr('Start Conversion Process'),
                        callback=self.start_encoding),

                   'stop_action':
                   dict(icon=QIcon(':/icons/stop.png'),
                        text=self.tr('&Stop'),
                        shortcut="Ctrl+P",
                        tip=self.tr('Stop Video File Conversion'),
                        callback=self.stop_file_encoding),

                   'stop_all_action':
                   dict(icon=QIcon(':/icons/stop-all.png'),
                        text=self.tr('S&top All'),
                        shortcut="Ctrl+A",
                        tip=self.tr('Stop all Video Conversion Tasks'),
                        callback=self.stop_all_files_encoding),

                   'about_action':
                   dict(text=self.tr('&About') + ' ' + APP_NAME,
                        tip=self.tr('About') + ' ' + APP_NAME + ' ' + VERSION,
                        callback=self.about),

                   'help_content_action':
                   dict(icon=QIcon(':/icons/about.png'),
                        text=self.tr('&Contents'),
                        shortcut="Ctrl+H",
                        tip=self.tr('Help Contents'),
                        callback=self.help_content),

                   'changelog_action':
                   dict(icon=QIcon(':/icons/changelog.png'),
                        text=self.tr('Changelog'),
                        tip=self.tr('Changelog'),
                        callback=self.changelog),

                   'ffmpeg_doc_action':
                   dict(icon=QIcon(':/icons/ffmpeg.png'),
                        text=self.tr('&Ffmpeg Documentation'),
                        shortcut="Ctrl+L",
                        tip=self.tr('Open Ffmpeg On-Line Documentation'),
                        callback=self.ffmpeg_doc),

                   'videomorph_web_action':
                   dict(icon=QIcon(':/logo/videomorph.png'),
                        text=APP_NAME + ' ' + self.tr('&Web Page'),
                        shortcut="Ctrl+V",
                        tip=self.tr('Open') + ' ' + APP_NAME + ' ' + self.tr(
                            'Web Page'),
                        callback=self.videomorph_web),

                   'exit_action':
                   dict(icon=QIcon(':/icons/exit.png'),
                        text=self.tr('E&xit'),
                        shortcut="Ctrl+Q",
                        tip=self.tr('Exit') + ' ' + APP_NAME + ' ' + VERSION,
                        callback=self.close),

                   'info_action':
                   dict(text=self.tr('Properties...'),
                        tip=self.tr('Show Video Properties'),
                        callback=self.show_video_info)}

        for action in actions:
            self.__dict__[action] = self._action_factory(**actions[action])

    def _create_context_menu(self):
        first_separator = QAction(self)
        first_separator.setSeparator(True)
        second_separator = QAction(self)
        second_separator.setSeparator(True)
        self.tasks_table.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.tasks_table.addAction(self.open_media_file_action)
        self.tasks_table.addAction(self.open_media_dir_action)
        self.tasks_table.addAction(first_separator)
        self.tasks_table.addAction(self.remove_media_file_action)
        self.tasks_table.addAction(self.clear_media_list_action)
        self.tasks_table.addAction(second_separator)
        self.tasks_table.addAction(self.play_input_media_file_action)
        self.tasks_table.addAction(self.play_output_media_file_action)
        self.tasks_table.addAction(self.info_action)

    def _create_main_menu(self):
        """Create main app menu."""
        # File menu
        self.file_menu = self.menuBar().addMenu(self.tr('&File'))
        self.file_menu.addAction(self.open_media_file_action)
        self.file_menu.addAction(self.open_media_dir_action)
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
        self.help_menu.addAction(self.help_content_action)
        self.help_menu.addAction(self.changelog_action)
        self.help_menu.addAction(self.videomorph_web_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.ffmpeg_doc_action)
        self.help_menu.addSeparator()
        self.help_menu.addAction(self.about_action)

    def _create_toolbar(self):
        """Create a toolbar and add it to the interface."""
        self.tool_bar = QToolBar(self)
        # Add actions to the tool bar
        self.tool_bar.addAction(self.open_media_file_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.clear_media_list_action)
        self.tool_bar.addAction(self.remove_media_file_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.convert_action)
        self.tool_bar.addAction(self.stop_action)
        self.tool_bar.addAction(self.stop_all_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.exit_action)
        self.tool_bar.setIconSize(QSize(28, 28))
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        # Add the toolbar to main window
        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)

    def _create_status_bar(self):
        """Create app status bar."""
        self.statusBar().showMessage(self.tr('Ready'))

    def _create_progress_dialog(self):
        label = QLabel()
        label.setAlignment(Qt.AlignLeft)
        progress_dlg = QProgressDialog(parent=self)
        progress_dlg.setFixedSize(500, 100)
        progress_dlg.setWindowTitle(self.tr('Adding Video Files...'))
        progress_dlg.setCancelButtonText(self.tr('Cancel'))
        progress_dlg.setLabel(label)
        progress_dlg.setModal(True)
        progress_dlg.setMinimum(0)
        progress_dlg.setMinimumDuration(0)
        progress_dlg.setMaximum(0)
        progress_dlg.setValue(0)

        return progress_dlg

    def _update_edit_triggers(self):
        """Toggle Edit triggers on task table."""
        if (int(self.tasks_table.currentColumn()) == COLUMNS.QUALITY and not
                self.conversion_lib.converter_is_running):
            self.tasks_table.setEditTriggers(QAbstractItemView.AllEditTriggers)
        else:
            self.tasks_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            if int(self.tasks_table.currentColumn()) == COLUMNS.NAME:
                self.play_input_media_file()

        self._update_ui_when_playing(row=self.tasks_table.currentIndex().row())

    @staticmethod
    def _get_settings_file():
        return QSettings(join_path(SYS_PATHS.config, 'config.ini'),
                         QSettings.IniFormat)

    def _create_initial_settings(self):
        """Create initial settings file."""
        if not exists(join_path(SYS_PATHS.config, 'config.ini')):
            self._write_app_settings(pos=QPoint(100, 50),
                                     size=QSize(1096, 510),
                                     profile_index=0,
                                     preset_index=0)

    def _load_app_settings(self):
        """Read the app settings."""
        self._create_initial_settings()
        settings = self._get_settings_file()
        pos = settings.value("pos", QPoint(600, 200), type=QPoint)
        size = settings.value("size", QSize(1096, 510), type=QSize)
        self.resize(size)
        self.move(pos)
        if 'profile_index' and 'preset_index' in settings.allKeys():
            profile = settings.value('profile_index')
            preset = settings.value('preset_index')
            self.profiles_combo.setCurrentIndex(int(profile))
            self.quality_combo.setCurrentIndex(int(preset))
        if 'output_dir' in settings.allKeys():
            directory = str(settings.value('output_dir'))
            output_dir = directory if isdir(directory) else QDir.homePath()
            self.output_edit.setText(output_dir)
        if 'source_dir' in settings.allKeys():
            self.source_dir = str(settings.value('source_dir'))

    def _write_app_settings(self, **app_settings):
        """Write app settings on exit.

        Args:
            app_settings (OrderedDict): OrderedDict to collect all app settings
        """
        settings_file = self._get_settings_file()

        settings = OrderedDict(
            pos=self.pos(),
            size=self.size(),
            profile_index=self.profiles_combo.currentIndex(),
            preset_index=self.quality_combo.currentIndex(),
            source_dir=self.source_dir,
            output_dir=self.output_edit.text())

        if app_settings:
            settings.update(app_settings)

        for key, setting in settings.items():
            settings_file.setValue(key, setting)

    def _show_message_box(self, type_, title, msg):
        QMessageBox(type_, title, msg, QMessageBox.Ok, self).show()

    def about(self):
        """Show About dialog."""
        about_dlg = AboutVMDialog(parent=self)
        about_dlg.exec_()

    def changelog(self):
        """Show the changelog dialog."""
        changelog_dlg = ChangelogDialog(parent=self)
        changelog_dlg.exec_()

    def ffmpeg_doc(self):
        """Open ffmpeg documentation page."""
        self._open_url(url='https://ffmpeg.org/documentation.html')

    def videomorph_web(self):
        """Open VideoMorph Web page."""
        self._open_url(url='http://videomorph.webmisolutions.com')

    def show_video_info(self):
        """Show video info on the Info Panel."""
        position = self.tasks_table.currentRow()
        info_dlg = InfoDialog(parent=self,
                              position=position,
                              media_list=self.media_list)
        info_dlg.show()

    def notify(self, file_name):
        """Notify when conversion finished."""
        file_name = ''.join(('"', file_name, '"'))
        msg = file_name + ': ' + self.tr('Successfully converted')
        self.tray_icon.showMessage(APP_NAME, msg,
                                   QSystemTrayIcon.Information, 2000)
        if exists(join_path(BASE_DIR, VM_PATHS.sounds)):
            sound = join_path(BASE_DIR, VM_PATHS.sounds, 'successful.wav')
        else:
            sound = join_path(SYS_PATHS.sounds, 'successful.wav')
        launcher = launcher_factory()
        launcher.sound_notify(sound)

    @staticmethod
    def _open_url(url):
        """Open URL."""
        launcher = launcher_factory()
        launcher.open_with_user_browser(url=url)

    @staticmethod
    def help_content():
        """Open ffmpeg documentation page."""
        if LOCALE == 'es_ES':
            file_name = 'manual_es.pdf'
        else:
            file_name = 'manual_en.pdf'

        file_path = join_path(SYS_PATHS.help, file_name)
        if isfile(file_path):
            url = join_path('file:', file_path)
        else:
            url = join_path('file:', BASE_DIR, VM_PATHS.help, file_name)

        launcher = launcher_factory()
        launcher.open_with_user_browser(url=url)

    @staticmethod
    def shutdown_machine():
        """Shutdown machine when conversion is finished."""
        launcher = launcher_factory()
        qApp.closeAllWindows()
        launcher.shutdown_machine()

    def populate_profiles_combo(self):
        """Populate profiles combobox."""
        # Clear combobox content
        self.profiles_combo.clear()
        # Populate the combobox with new data

        profile_names = self.profile.get_xml_profile_qualities(LOCALE).keys()
        for i, profile_name in enumerate(profile_names):
            self.profiles_combo.addItem(profile_name)
            icon = QIcon(':/formats/{0}.png'.format(profile_name))
            self.profiles_combo.setItemIcon(i, icon)

    def populate_quality_combo(self, combo):
        """Populate target quality combobox.

        Args:
            combo (QComboBox): List all available presets
        """
        current_profile = self.profiles_combo.currentText()
        if current_profile != '':
            combo.clear()
            combo.addItems(
                self.profile.get_xml_profile_qualities(
                    LOCALE)[current_profile])

            if self.tasks_table.rowCount():
                self._update_media_files_status()
            self.profile.update(new_quality=self.quality_combo.currentText())

    def output_directory(self):
        """Choose output directory."""
        directory = self._select_directory(
            dialog_title=self.tr('Choose Output Directory'),
            source_dir=self.output_edit.text())

        if directory:
            self.output_edit.setText(directory)
            self._on_modify_conversion_option()

    def closeEvent(self, event):
        """Things to do on close."""
        # Close communication and kill the encoding process
        if self.conversion_lib.converter_is_running:
            # ask for confirmation
            user_answer = QMessageBox.question(
                self,
                APP_NAME,
                self.tr('There are on Going Conversion Tasks.'
                        ' Are you Sure you Want to Exit?'),
                QMessageBox.Yes | QMessageBox.No)

            if user_answer == QMessageBox.Yes:
                # Disconnect the finished signal
                self.conversion_lib.converter_finished_disconnect(
                    connected=self._finish_file_encoding)
                self.conversion_lib.kill_converter()
                self.conversion_lib.close_converter()
                self.media_list.delete_running_file_output(
                    output_dir=self.output_edit.text(),
                    tagged_output=self.tag_chb.checkState())
                # Save settings
                self._write_app_settings()
                event.accept()
            else:
                event.ignore()
        else:
            # Save settings
            self._write_app_settings()
            event.accept()

    def _fill_media_list(self, files_paths):
        """Fill MediaList object with _MediaFile objects."""
        progress_dlg = self._create_progress_dialog()

        for i, element in enumerate(self.media_list.populate(files_paths)):
            if not i:  # First element yielded
                progress_dlg.setMaximum(element)
            else:  # Second and on...
                progress_dlg.setLabelText(self.tr('Adding File: ') + element)
                progress_dlg.setValue(i)

            if progress_dlg.wasCanceled():
                break

        progress_dlg.close()

        if self.media_list.not_added_files:
            msg = self.tr('Invalid Video File Information for:') + ' \n - ' + \
                  '\n - '.join(self.media_list.not_added_files) + '\n' + \
                  self.tr('File not Added to the List of Conversion Tasks')
            self._show_message_box(
                type_=QMessageBox.Critical,
                title=self.tr('Error!'),
                msg=msg)

            if not self.media_list.length:
                self._update_ui_when_no_file()
            else:
                self.update_ui_when_ready()

    def _load_files(self, source_dir=QDir.homePath()):
        """Load video files."""
        files_paths = self._select_files(
            dialog_title=self.tr('Select Video Files'),
            files_filter=self.tr('Video Files') + ' ' +
            '(' + VIDEO_FILTERS + ')',
            source_dir=source_dir)

        return files_paths

    def _insert_table_item(self, item_text, row, column):
        item = QTableWidgetItem()
        item.setText(item_text)
        if column == COLUMNS.NAME:
            item.setIcon(QIcon(':/icons/video-in-list.png'))
        self.tasks_table.setItem(row, column, item)

    def _create_table(self):
        self.tasks_table.setRowCount(self.media_list.length)
        # Call converter_is_running only once
        converter_is_running = self.conversion_lib.converter_is_running
        for row in range(self.tasks_table.rowCount()):
            self._insert_table_item(
                item_text=self.media_list.get_file_name(position=row,
                                                        with_extension=True),
                row=row, column=COLUMNS.NAME)

            self._insert_table_item(
                item_text=str(write_time(
                    self.media_list.get_file_info(
                        position=row,
                        info_param='duration'))),
                row=row, column=COLUMNS.DURATION)

            self._insert_table_item(
                item_text=str(self.quality_combo.currentText()),
                row=row, column=COLUMNS.QUALITY)

            if converter_is_running:
                if row > self.media_list.position:
                    self._insert_table_item(item_text=self.tr('To Convert'),
                                            row=row, column=COLUMNS.PROGRESS)
            else:
                self._insert_table_item(item_text=self.tr('To Convert'),
                                        row=row, column=COLUMNS.PROGRESS)

    def add_media_files(self, *files):
        """Add video files to conversion list.

        Args:
            files (list): List of video file paths
        """
        # Update tool buttons so you can convert, or add_file, or clear...
        # only if there is not a conversion process running
        if self.conversion_lib.converter_is_running:
            self._update_ui_when_converter_running()
        else:
            # Update the files status
            self._set_media_status()
            # Update ui
            self.update_ui_when_ready()

        self._fill_media_list(files)

        self._create_table()

        # After adding files to the list, recalculate the list duration
        self.media_list_duration = self.media_list.duration

    def play_input_media_file(self):
        """Play the input video using an available video player."""
        row = self.tasks_table.currentIndex().row()
        self._play_media_file(file_path=self.media_list.get_file_path(row))
        self._update_ui_when_playing(row)

    def _get_output_path(self, row):
        path = self.media_list.get_file(row).get_output_path(
            output_dir=self.output_edit.text(),
            tagged_output=self.tag_chb.checkState())
        return path

    def play_output_media_file(self):
        """Play the output video using an available video player."""
        row = self.tasks_table.currentIndex().row()
        path = self._get_output_path(row)
        self._play_media_file(file_path=path)
        self._update_ui_when_playing(row)

    def _play_media_file(self, file_path):
        """Play a video using an available video player."""
        try:
            self.conversion_lib.run_player(file_path=file_path)
        except PlayerNotFoundError:
            self._show_message_box(
                type_=QMessageBox.Critical,
                title=self.tr('Error!'),
                msg=self.tr('No Video Player Found in your System'))

    def open_media_files(self):
        """Add media files to the list of conversion tasks."""
        files_paths = self._load_files(source_dir=self.source_dir)
        # If no file is selected then return
        if files_paths is None:
            return

        self.add_media_files(*files_paths)

    def open_media_dir(self):
        """Add media files from a directory recursively."""
        directory = self._select_directory(
            dialog_title=self.tr('Select Directory'),
            source_dir=self.source_dir)

        if not directory:
            return

        try:
            media_files = search_directory_recursively(directory)
            self.source_dir = directory
            self.add_media_files(*media_files)
        except FileNotFoundError:
            self._show_message_box(
                type_=QMessageBox.Critical,
                title=self.tr('Error!'),
                msg=self.tr('No Video Files Found in:' + ' ' + directory))

    def remove_media_file(self):
        """Remove selected media file from the list."""
        file_row = self.tasks_table.currentItem().row()

        msg_box = QMessageBox(
            QMessageBox.Warning,
            self.tr('Warning!'),
            self.tr('Remove Video File from the List of Conversion Tasks?'),
            QMessageBox.NoButton, self)

        msg_box.addButton(self.tr("&Yes"), QMessageBox.AcceptRole)
        msg_box.addButton(self.tr("&No"), QMessageBox.RejectRole)

        if msg_box.exec_() == QMessageBox.AcceptRole:
            # Delete file from table
            self.tasks_table.removeRow(file_row)
            # Remove file from self.media_list
            self.media_list.delete_file(position=file_row)
            self.media_list.position = None
            self.media_list_duration = self.media_list.duration

        # If all files are deleted... update the interface
        if not self.tasks_table.rowCount():
            self._reset_options_check_boxes()
            self._update_ui_when_no_file()

    def add_customized_profile(self):
        """Show dialog for adding conversion profiles."""
        add_profile_dlg = AddProfileDialog(parent=self)
        add_profile_dlg.exec_()

    def _export_import_profiles(self, func, path, msg_info):
        try:
            func(path)
        except PermissionError:
            self._show_message_box(
                type_=QMessageBox.Critical,
                title=self.tr('Error!'),
                msg=self.tr('Can not Write to Selected Directory'))
        else:
            self._show_message_box(type_=QMessageBox.Information,
                                   title=self.tr('Information!'),
                                   msg=msg_info)

    def _select_directory(self, dialog_title, source_dir=QDir.homePath()):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly

        directory = QFileDialog.getExistingDirectory(self,
                                                     dialog_title,
                                                     source_dir,
                                                     options=options)
        return directory

    def export_profiles(self):
        """Export conversion profiles."""
        directory = self._select_directory(
            dialog_title=self.tr('Export to Directory'))

        if directory:
            msg_info = self.tr('Conversion Profiles Successfully Exported!')
            self._export_import_profiles(
                func=self.profile.export_xml_profiles,
                path=directory, msg_info=msg_info)

    def import_profiles(self):
        """Import conversion profiles."""
        file_path = self._select_files(
            dialog_title=self.tr('Select a Profiles File'),
            files_filter=self.tr('Profiles Files ') + '(*.xml)',
            single_file=True)

        if file_path:
            msg_info = self.tr('Conversion Profiles Successfully Imported!')

            self._export_import_profiles(
                func=self.profile.import_xml_profiles,
                path=file_path, msg_info=msg_info)
            self.populate_profiles_combo()
            self.profile.update(new_quality=self.quality_combo.currentText())

    def restore_profiles(self):
        """Restore default profiles."""
        msg_box = QMessageBox(
            QMessageBox.Warning,
            self.tr('Warning!'),
            self.tr('Do you Really Want to Restore the '
                    'Default Conversion Profiles?'),
            QMessageBox.NoButton, self)

        msg_box.addButton(self.tr("&Yes"), QMessageBox.AcceptRole)
        msg_box.addButton(self.tr("&No"), QMessageBox.RejectRole)

        if msg_box.exec_() == QMessageBox.AcceptRole:
            self.profile.restore_default_profiles()
            self.populate_profiles_combo()
            self.profile.update(new_quality=self.quality_combo.currentText())

    def _select_files(self, dialog_title, files_filter,
                      source_dir=QDir.homePath(), single_file=False):
        # Validate source_dir
        source_directory = source_dir if isdir(source_dir) else QDir.homePath()

        # Select media files and store their path
        if single_file:
            files_paths, _ = QFileDialog.getOpenFileName(self,
                                                         dialog_title,
                                                         source_directory,
                                                         files_filter)
        else:
            files_paths, _ = QFileDialog.getOpenFileNames(self,
                                                          dialog_title,
                                                          source_directory,
                                                          files_filter)

        if files_paths:
            # Update the source directory
            if not single_file:
                self.source_dir = dirname(files_paths[0])
        else:
            return None

        return files_paths

    def clear_media_list(self):
        """Clear media conversion list with user confirmation."""
        msg_box = QMessageBox(
            QMessageBox.Warning,
            self.tr('Warning!'),
            self.tr('Remove all Conversion Tasks from the List?'),
            QMessageBox.NoButton, self)

        msg_box.addButton(self.tr("&Yes"), QMessageBox.AcceptRole)
        msg_box.addButton(self.tr("&No"), QMessageBox.RejectRole)

        if msg_box.exec_() == QMessageBox.AcceptRole:
            # If user says YES clear table of conversion tasks
            self.tasks_table.clearContents()
            self.tasks_table.setRowCount(0)
            # Clear MediaList so it contains no element
            self.media_list.clear()
            # Update UI
            self._reset_options_check_boxes()
            self._update_ui_when_no_file()

    def start_encoding(self):
        """Start the encoding process."""
        self._update_ui_when_converter_running()

        self.media_list.position += 1
        self.timer.operation_start_time = 0.0

        if self.media_list.running_file_status == STATUS.todo:
            try:
                # Fist build the conversion command
                conversion_cmd = self.media_list.running_file_conversion_cmd(
                    target_quality=self.tasks_table.item(
                        self.media_list.position,
                        COLUMNS.QUALITY).text(),
                    output_dir=self.output_edit.text(),
                    tagged_output=self.tag_chb.checkState(),
                    subtitle=bool(self.subtitle_chb.checkState()))
                # Then pass it to the _converter
                self.conversion_lib.start_converter(cmd=conversion_cmd)
            except PermissionError:
                self._show_message_box(
                    type_=QMessageBox.Critical,
                    title=self.tr('Error!'),
                    msg=self.tr('Can not Write to Selected Directory'))
                self._update_ui_when_error_on_conversion()
            except FileNotFoundError:
                self._show_message_box(
                    type_=QMessageBox.Critical,
                    title=self.tr('Error!'),
                    msg=(self.tr('Input Video File:') + ' ' +
                         self.media_list.running_file_name(
                             with_extension=True) + ' ' +
                         self.tr('not Found')))
                self._update_ui_when_error_on_conversion()
            # except FileExistsError:
            #     self._show_message_box(
            #         type_=QMessageBox.Critical,
            #         title=self.tr('Error!'),
            #         msg=(self.tr('Video File:') + ' ' +
            #              self.media_list.running_file_output_name(
            #                  output_dir=self.output_edit.text(),
            #                  tagged_output=self.tag_chb.checkState()) + ' ' +
            #              self.tr('Already Exists in '
            #                      'Output Directory. Please, Change the '
            #                      'Output Directory')))
            #     self._update_ui_when_error_on_conversion()
        else:
            self._end_encoding_process()

    def stop_file_encoding(self):
        """Stop file encoding process and continue with the list."""
        # Terminate the file encoding
        self.conversion_lib.stop_converter()
        # Set _MediaFile.status attribute
        self.media_list.running_file_status = STATUS.stopped
        # Delete the file when conversion is stopped by the user
        self.media_list.delete_running_file_output(
            output_dir=self.output_edit.text(),
            tagged_output=self.tag_chb.checkState())
        # Update the list duration and partial time for total progress bar
        self.timer.reset_progress_times()
        self.media_list_duration = self.media_list.duration

    def stop_all_files_encoding(self):
        """Stop the conversion process for all the files in list."""
        # Delete the file when conversion is stopped by the user
        self.conversion_lib.stop_converter()
        self.media_list.delete_running_file_output(
            output_dir=self.output_edit.text(),
            tagged_output=self.tag_chb.checkState())
        for media_file in self.media_list:
            # Set _MediaFile.status attribute
            if media_file.status != STATUS.done:
                media_file.status = STATUS.stopped
                self.media_list.position = self.media_list.index(media_file)
                self.tasks_table.item(
                    self.media_list.position,
                    COLUMNS.PROGRESS).setText(self.tr('Stopped!'))

        # Update the list duration and partial time for total progress bar
        self.timer.reset_progress_times()
        self.media_list_duration = self.media_list.duration

    def _finish_file_encoding(self):
        """Finish the file encoding process."""
        if self.media_list.running_file_status != STATUS.stopped:
            file_name = self.media_list.running_file_name(with_extension=True)
            self.notify(file_name)
            # Close and kill the converterprocess
            self.conversion_lib.close_converter()
            # Check if the process finished OK
            if (self.conversion_lib.converter_exit_status() ==
                    QProcess.NormalExit):
                # When finished a file conversion...
                self.tasks_table.item(
                    self.media_list.position,
                    COLUMNS.PROGRESS).setText(self.tr('Done!'))
                self.media_list.running_file_status = STATUS.done
                self.operation_pb.setProperty("value", 0)
                if self.delete_chb.checkState():
                    self.media_list.delete_running_file_input()
        else:
            # If the process was stopped
            if not self.conversion_lib.converter_is_running:
                self.tasks_table.item(
                    self.media_list.position,
                    COLUMNS.PROGRESS).setText(self.tr('Stopped!'))
        # Attempt to end the conversion process
        self._end_encoding_process()

    def _end_encoding_process(self):
        """End up the encoding process."""
        # Test if encoding process is finished
        if self.media_list.is_exhausted:

            if self.conversion_lib.error is not None:
                self._show_message_box(
                    type_=QMessageBox.Critical,
                    title='Error!',
                    msg=self.tr('The Conversion Library has '
                                'Failed with Error:') + ' ' +
                    self.conversion_lib.error)
                self.conversion_lib.error = None
            elif not self.media_list.all_stopped:
                if self.shutdown_chb.checkState():
                    self.shutdown_machine()
                    return
                self._show_message_box(
                    type_=QMessageBox.Information,
                    title=self.tr('Information!'),
                    msg=self.tr('Encoding Process Successfully Finished!'))
            else:
                self._show_message_box(
                    type_=QMessageBox.Information,
                    title=self.tr('Information!'),
                    msg=self.tr('Encoding Process Stopped by the User!'))

            self.setWindowTitle(self.title)
            self.statusBar().showMessage(self.tr('Ready'))
            self._reset_options_check_boxes()
            # Reset all progress related variables
            self._reset_progress_bars()
            self.timer.reset_progress_times()
            self.media_list_duration = self.media_list.duration
            self.timer.process_start_time = 0.0
            # Reset the position
            self.media_list.position = None
            # Update tool buttons
            self._update_ui_when_problem()
        else:
            self.start_encoding()

    def _reset_progress_bars(self):
        """Reset the progress bars."""
        self.operation_pb.setProperty("value", 0)
        self.total_pb.setProperty("value", 0)

    def _ready_read(self):
        """Is called when the conversion process emit a new output."""
        self.reader.update_read(
            process_output=self.conversion_lib.read_converter_output())

        self._update_conversion_progress()

    def _update_conversion_progress(self):
        """Read the encoding output from the converter stdout."""
        # Initialize the process time
        if not self.timer.process_start_time:
            self.timer.init_process_start_time()

        # Initialize the operation time
        if not self.timer.operation_start_time:
            self.timer.init_operation_start_time()

        # Return if no time read
        if not self.reader.has_time_read:
            # Catch the library errors only before time_read
            self.conversion_lib.catch_errors()
            return

        self.timer.update_time(op_time_read_sec=self.reader.time)

        self.timer.update_cum_times()

        file_duration = float(self.media_list.running_file_info('duration'))

        operation_progress = self.timer.operation_progress(
            file_duration=file_duration)

        process_progress = self.timer.process_progress(
            list_duration=self.media_list_duration)

        self._update_progress(op_progress=operation_progress,
                              pr_progress=process_progress)

        self._update_status_bar()

        self._update_main_window_title(op_progress=operation_progress)

    def _update_progress(self, op_progress, pr_progress):
        """Update operation progress in tasks list & operation progress bar."""
        # Update operation progress bar
        self.operation_pb.setProperty("value", op_progress)
        # Update operation progress in tasks list
        self.tasks_table.item(self.media_list.position, 3).setText(
            str(op_progress) + "%")
        self.total_pb.setProperty("value", pr_progress)

    def _update_main_window_title(self, op_progress):
        """Update the main window title."""
        running_file_name = self.media_list.running_file_name(
            with_extension=True)

        self.setWindowTitle(str(op_progress) + '%' + '-' +
                            '[' + running_file_name + ']' +
                            ' - ' + APP_NAME + ' ' + VERSION)

    def _update_status_bar(self):
        """Update the status bar while converting."""
        file_duration = float(self.media_list.running_file_info('duration'))

        self.statusBar().showMessage(
            self.tr('Converting: {m}\t\t\t '
                    'At: {br}\t\t\t '
                    'Operation Remaining Time: {ort}\t\t\t '
                    'Total Elapsed Time: {tet}').format(
                        m=self.media_list.running_file_name(
                            with_extension=True),
                        br=self.reader.bitrate,
                        ort=self.timer.operation_remaining_time(
                            file_duration=file_duration),
                        tet=write_time(self.timer.process_cum_time)))

    def _update_media_files_status(self):
        """Update file status."""
        # Current item
        item = self.tasks_table.currentItem()
        if item is not None:
            # Update target_quality in table
            self.tasks_table.item(item.row(), COLUMNS.QUALITY).setText(
                str(self.quality_combo.currentText()))

            # Update table Progress field if file is: Done or Stopped
            self.update_table_progress_column(row=item.row())

            # Update file Done or Stopped status
            self.media_list.set_file_status(position=item.row(),
                                            status=STATUS.todo)

        else:
            self._update_all_table_rows(column=COLUMNS.QUALITY,
                                        value=self.quality_combo.currentText())

            self._set_media_status()

        # Update total duration of the new tasks list
        self.media_list_duration = self.media_list.duration
        # Update the interface
        self.update_ui_when_ready()

    def _update_all_table_rows(self, column, value):
        rows = self.tasks_table.rowCount()
        if rows:
            for row in range(rows):
                self.tasks_table.item(row, column).setText(
                    str(value))
                self.update_table_progress_column(row)

    def update_table_progress_column(self, row):
        """Update the progress column of conversion task list."""
        if self.media_list.get_file_status(row) != STATUS.todo:
            self.tasks_table.item(
                row,
                COLUMNS.PROGRESS).setText(self.tr('To Convert'))

    def _reset_options_check_boxes(self):
        self.delete_chb.setChecked(False)
        self.tag_chb.setChecked(False)
        self.subtitle_chb.setChecked(False)
        self.subtitle_chb.setChecked(False)

    def _set_media_status(self):
        """Update media files state of conversion."""
        for media_file in self.media_list:
            media_file.status = STATUS.todo
        self.media_list.position = None

    def _on_modify_conversion_option(self):
        if self.media_list.length:
            self.update_ui_when_ready()
            self._set_media_status()
            self._update_all_table_rows(column=COLUMNS.PROGRESS,
                                        value=self.tr('To Convert'))
            self.media_list_duration = self.media_list.duration

    def _update_ui(self, **i_vars):
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
                         import_profile=True,
                         restore_profile=True,
                         output_dir=True,
                         subtitles_chb=True,
                         delete_chb=True,
                         tag_chb=True,
                         shutdown_chb=True,
                         play_input=True,
                         play_output=True,
                         info=True)

        variables.update(i_vars)

        self.open_media_file_action.setEnabled(variables['add'])
        self.convert_action.setEnabled(variables['convert'])
        self.clear_media_list_action.setEnabled(variables['clear'])
        self.remove_media_file_action.setEnabled(variables['remove'])
        self.stop_action.setEnabled(variables['stop'])
        self.stop_all_action.setEnabled(variables['stop_all'])
        self.quality_combo.setEnabled(variables['presets'])
        self.profiles_combo.setEnabled(variables['profiles'])
        self.add_profile_action.setEnabled(variables['add_costume_profile'])
        self.import_profile_action.setEnabled(variables['import_profile'])
        self.restore_profile_action.setEnabled(variables['restore_profile'])
        self.output_btn.setEnabled(variables['output_dir'])
        self.subtitle_chb.setEnabled(variables['subtitles_chb'])
        self.delete_chb.setEnabled(variables['delete_chb'])
        self.tag_chb.setEnabled(variables['tag_chb'])
        self.shutdown_chb.setEnabled(variables['shutdown_chb'])
        self.play_input_media_file_action.setEnabled(variables['play_input'])
        self.play_output_media_file_action.setEnabled(variables['play_output'])
        self.info_action.setEnabled(variables['info'])
        self.tasks_table.setCurrentItem(None)

    def _update_ui_when_no_file(self):
        """User cannot perform any action but to add files to list."""
        self._update_ui(clear=False,
                        remove=False,
                        convert=False,
                        stop=False,
                        stop_all=False,
                        profiles=False,
                        presets=False,
                        subtitles_chb=False,
                        delete_chb=False,
                        tag_chb=False,
                        shutdown_chb=False,
                        play_input=False,
                        play_output=False,
                        info=False)

    def update_ui_when_ready(self):
        """Update UI when app is ready to start conversion."""
        self._update_ui(stop=False,
                        stop_all=False,
                        remove=False,
                        play_input=False,
                        play_output=False,
                        info=False)

    def _update_ui_when_playing(self, row):
        if self.conversion_lib.converter_is_running:
            self._update_ui_when_converter_running()
        elif self.media_list.get_file_status(row) == STATUS.todo:
            self.update_ui_when_ready()
        else:
            self._update_ui_when_problem()

    def _update_ui_when_problem(self):
        self._update_ui(convert=False,
                        stop=False,
                        stop_all=False,
                        remove=False,
                        play_input=False,
                        play_output=False,
                        info=False)

    def _update_ui_when_converter_running(self):
        self._update_ui(presets=False,
                        profiles=False,
                        subtitles_chb=False,
                        add_costume_profile=False,
                        import_profile=False,
                        restore_profile=False,
                        convert=False,
                        clear=False,
                        remove=False,
                        output_dir=False,
                        delete_chb=False,
                        tag_chb=False,
                        play_input=False,
                        play_output=False,
                        info=False)

    def _update_ui_when_error_on_conversion(self):
        self.timer.reset_progress_times()
        self.media_list_duration = self.media_list.duration
        self.media_list.position = None
        self._reset_progress_bars()
        self.setWindowTitle(self.title)
        self._reset_options_check_boxes()
        self.update_ui_when_ready()

    def _enable_context_menu_action(self):
        if not self.conversion_lib.converter_is_running:
            self.remove_media_file_action.setEnabled(True)

        self.play_input_media_file_action.setEnabled(True)

        path = self._get_output_path(row=self.tasks_table.currentIndex().row())
        # Only enable the menu if output file exist and if it not .mp4,
        # cause .mp4 files doesn't run until conversion is finished
        self.play_output_media_file_action.setEnabled(
            exists(path) and self.profiles_combo.currentText() != 'MP4')
        self.info_action.setEnabled(bool(self.media_list.length))
