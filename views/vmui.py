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

from functools import partial

from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QToolButton

from videomorph import APP_NAME
from videomorph import VERSION
from . import videomorph_qrc
from .vmwidgets import TasksListTable


class VMUi(QMainWindow):
    """VideoMorph Main Window class."""

    def __init__(self, handler):
        """Class initializer."""
        super().__init__()
        self.vmh = handler
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.title = APP_NAME + ' ' + VERSION
        self.icon = self._get_app_icon()
        self._setup_ui()
        # self._create_initial_settings()
        # self._read_app_settings()

    def _setup_ui(self):
        """Setup UI."""
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
        # self.update_ui_when_no_file()

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
        """Create the system tray icon."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(icon)
        self.tray_icon.setContextMenu(self._create_sys_tray_menu())
        self.tray_icon.show()

    def _create_sys_tray_menu(self):
        """Create system tray menu."""
        tray_icon_menu = QMenu(self)
        tray_icon_menu.addAction(self.load_media_files_action)
        tray_icon_menu.addAction(self.load_media_dir_action)
        tray_icon_menu.addSeparator()
        tray_icon_menu.addAction(self.clear_media_list_action)
        tray_icon_menu.addSeparator()
        tray_icon_menu.addAction(self.convert_action)
        tray_icon_menu.addAction(self.stop_all_action)
        tray_icon_menu.addSeparator()
        tray_icon_menu.addAction(self.exit_action)
        return tray_icon_menu

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
            self.vmh.on_profiles_combo_item_changed, self.quality_combo))
        # self.quality_combo.activated.connect(self._update_media_files_status)
        settings_layout.addWidget(self.quality_combo)

        options_label = QLabel(self.tr('Other Options:'))
        settings_layout.addWidget(options_label)

        sub_tip = self.tr('Insert Subtitles if Available in Source Directory')
        self.subtitle_chb = QCheckBox(self.tr('Insert Subtitles if Available'),
                                      statusTip=sub_tip,
                                      toolTip=sub_tip)
        # self.subtitle_chb.clicked.connect(self._on_modify_conversion_option)
        settings_layout.addWidget(self.subtitle_chb)

        del_text = self.tr('Delete Input Video Files when Finished')
        self.delete_chb = QCheckBox(del_text,
                                    statusTip=del_text,
                                    toolTip=del_text)
        # self.delete_chb.clicked.connect(self._on_modify_conversion_option)
        settings_layout.addWidget(self.delete_chb)

        tag_text = self.tr('Use Format Tag in Output Video File Name')
        tag_tip_text = (tag_text + '. ' +
                        self.tr('Useful when Converting a '
                                'Video File to Multiples Formats'))
        self.tag_chb = QCheckBox(tag_text,
                                 statusTip=tag_tip_text,
                                 toolTip=tag_tip_text)
        # self.tag_chb.clicked.connect(self._on_modify_conversion_option)
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
        # self.tasks_table.cellPressed.connect(self._enable_context_menu_action)
        # self.tasks_table.doubleClicked.connect(self.vmh.on_tasks_list_double_clicked)
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
        # self.output_btn.clicked.connect(self.output_directory)
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
        actions = {'load_media_files_action':
                   dict(icon=QIcon(':/icons/video-file.png'),
                        text=self.tr('&Add Files...'),
                        shortcut="Ctrl+O",
                        tip=self.tr('Add Video Files to the '
                                    'List of Conversion Tasks'),
                        callback=self.vmh.on_load_media_files),

                   'load_media_dir_action':
                   dict(icon=QIcon(':/icons/add-folder.png'),
                        text=self.tr('Add &Directory...'),
                        shortcut="Ctrl+D",
                        tip=self.tr('Add all the Video Files in a Directory '
                                    'to the List of Conversion Tasks'),
                        callback=self.vmh.on_load_media_dir),

                   'add_profile_action':
                   dict(icon=QIcon(':/icons/add-profile.png'),
                        text=self.tr('&Add Customized Profile...'),
                        shortcut="Ctrl+F",
                        tip=self.tr('Add Customized Profile'),
                        callback=self.vmh.on_add_customized_profile),

                   'export_profile_action':
                   dict(icon=QIcon(':/icons/export.png'),
                        text=self.tr('&Export Conversion Profiles...'),
                        shortcut="Ctrl+E",
                        tip=self.tr('Export Conversion Profiles'),
                        callback=self.vmh.on_export_profiles),

                   'import_profile_action':
                   dict(icon=QIcon(':/icons/import.png'),
                        text=self.tr('&Import Conversion Profiles...'),
                        shortcut="Ctrl+I",
                        tip=self.tr('Import Conversion Profiles'),
                        callback=self.vmh.on_import_profiles),

                   'restore_profile_action':
                   dict(icon=QIcon(':/icons/default-profile.png'),
                        text=self.tr('&Restore the Default '
                                     'Conversion Profiles'),
                        tip=self.tr('Restore the Default Conversion Profiles'),
                        callback=self.vmh.on_restore_profiles),

                   'play_input_media_file_action':
                   dict(icon=QIcon(':/icons/video-player-input.png'),
                        text=self.tr('Play Input Video File'),
                        callback=self.vmh.on_play_input_media_file),

                   'play_output_media_file_action':
                   dict(icon=QIcon(':/icons/video-player-output.png'),
                        text=self.tr('Play Output Video File'),
                        callback=self.vmh.on_play_output_media_file),

                   'clear_media_list_action':
                   dict(icon=QIcon(':/icons/clear-list.png'),
                        text=self.tr('Clear &List'),
                        shortcut="Ctrl+Del",
                        tip=self.tr('Remove all Video Files from the '
                                    'List of Conversion Tasks'),
                        callback=self.vmh.on_clear_media_list),

                   'remove_media_file_action':
                   dict(icon=QIcon(':/icons/remove-file.png'),
                        text=self.tr('&Remove File'),
                        shortcut="Del",
                        tip=self.tr('Remove Selected Video File from the '
                                    'List of Conversion Tasks'),
                        callback=self.vmh.on_remove_media_file),

                   'convert_action':
                   dict(icon=QIcon(':/icons/convert.png'),
                        text=self.tr('&Convert'),
                        shortcut="Ctrl+R",
                        tip=self.tr('Start Conversion Process'),
                        callback=self.vmh.on_start_encoding),

                   'stop_action':
                   dict(icon=QIcon(':/icons/stop.png'),
                        text=self.tr('&Stop'),
                        shortcut="Ctrl+P",
                        tip=self.tr('Stop Video File Conversion'),
                        callback=self.vmh.on_stop_file_encoding),

                   'stop_all_action':
                   dict(icon=QIcon(':/icons/stop-all.png'),
                        text=self.tr('S&top All'),
                        shortcut="Ctrl+A",
                        tip=self.tr('Stop all Video Conversion Tasks'),
                        callback=self.vmh.on_stop_all_files_encoding),

                   'about_action':
                   dict(text=self.tr('&About') + ' ' + APP_NAME,
                        tip=self.tr('About') + ' ' + APP_NAME + ' ' + VERSION,
                        callback=self.vmh.on_about_action_clicked),

                   'help_content_action':
                   dict(icon=QIcon(':/icons/about.png'),
                        text=self.tr('&Contents'),
                        shortcut="Ctrl+H",
                        tip=self.tr('Help Contents'),
                        callback=self.vmh.on_help_content),

                   'changelog_action':
                   dict(icon=QIcon(':/icons/changelog.png'),
                        text=self.tr('Changelog'),
                        tip=self.tr('Changelog'),
                        callback=self.vmh.on_changelog_action_clicked),

                   'ffmpeg_doc_action':
                   dict(icon=QIcon(':/icons/ffmpeg.png'),
                        text=self.tr('&Ffmpeg Documentation'),
                        shortcut="Ctrl+L",
                        tip=self.tr('Open Ffmpeg On-Line Documentation'),
                        callback=self.vmh.on_ffmpeg_doc_action_clicked),

                   'videomorph_web_action':
                   dict(icon=QIcon(':/logo/videomorph.png'),
                        text=APP_NAME + ' ' + self.tr('&Web Page'),
                        shortcut="Ctrl+V",
                        tip=self.tr('Open') + ' ' + APP_NAME + ' ' + self.tr(
                            'Web Page'),
                        callback=self.vmh.on_videomorph_web_action_clicked),

                   'exit_action':
                   dict(icon=QIcon(':/icons/exit.png'),
                        text=self.tr('E&xit'),
                        shortcut="Ctrl+Q",
                        tip=self.tr('Exit') + ' ' + APP_NAME + ' ' + VERSION,
                        callback=self.close),

                   'info_action':
                   dict(text=self.tr('Properties...'),
                        tip=self.tr('Show Video Properties'),
                        callback=self.vmh.on_show_video_info_action_clicked)}

        for action in actions:
            self.__dict__[action] = self._action_factory(**actions[action])

    def _create_context_menu(self):
        first_separator = QAction(self)
        first_separator.setSeparator(True)
        second_separator = QAction(self)
        second_separator.setSeparator(True)
        self.tasks_table.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.tasks_table.addAction(self.load_media_files_action)
        self.tasks_table.addAction(self.load_media_dir_action)
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
        self.file_menu.addAction(self.load_media_files_action)
        self.file_menu.addAction(self.load_media_dir_action)
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
        self.tool_bar.addAction(self.load_media_files_action)
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

    def _get_app_icon(self):
        """Set window icon."""
        icon = QIcon()
        icon.addPixmap(QPixmap(':/icons/videomorph.ico'))
        return icon
