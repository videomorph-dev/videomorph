# -*- coding: utf-8 -*-

# File name: uihandler.py
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

"""This module provides VideoMorph UI Handler class."""

import sys
from pathlib import Path

from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import qApp

from .vmui import VMUi
from videomorph import BASE_DIR
from videomorph import VM_PATHS
from videomorph import SYS_PATHS
from videomorph.console import run_on_console
from videomorph import LOCALE
from videomorph.platformdeps import launcher_factory
from views import COLUMNS
from views.about import AboutVMDialog
from views.changelog import ChangelogDialog
from views.info import InfoDialog
from vmcore.controller import VMController


class UiHandler:
    """VideoMorph UI Handler Class."""

    def __init__(self):
        """Class initializer."""
        self.app = QApplication(sys.argv)

        # Setup app translator
        app_translator = QTranslator()
        i18n_dir = Path(BASE_DIR, VM_PATHS.i18n)
        i18n_file = i18n_dir.joinpath(
            ''.join(('videomorph_', LOCALE[:2], '.qm')))
        if i18n_file.exists():
            translator = i18n_dir.joinpath(
                'videomorph_{0}'.format(LOCALE)).__str__()
            app_translator.load(translator)
            self.app.installTranslator(app_translator)
        self.view = VMUi(self)
        self.vmc = VMController()

    def run_app(self):
        """Run the app."""
        no_library_msg = self.view.tr('Ffmpeg Library not Found'
                                      ' in your System')

        # Check for conversion library and run
        # if self.conversion_lib.library_path:
        #     if len(sys.argv) > 1:  # If it is running from console
        #         run_on_console(self.app, self.view)
        #     else:  # Or is running on GUI
        #         self.view.show()
        #         sys.exit(self.app.exec_())
        # else:
        #     msg_box = QMessageBox(
        #         QMessageBox.Critical,
        #         self.view.tr('Error!'),
        #         no_library_msg,
        #         QMessageBox.NoButton, self.view)
        #     msg_box.addButton("&Ok", QMessageBox.AcceptRole)
        #     if msg_box.exec_() == QMessageBox.AcceptRole:
        #         qApp.closeAllWindows()
        #
        # For testing only
        self.view.show()
        sys.exit(self.app.exec_())

    # EVENTS

    def on_about_action_clicked(self):
        """Show About dialog."""
        about_dlg = AboutVMDialog(parent=self.view)
        about_dlg.exec_()

    def on_show_video_info_action_clicked(self):
        """Show video info on the Info Panel."""
        pass
        # position = self.tasks_table.currentRow()
        # info_dlg = InfoDialog(parent=self,
        #                       position=position,
        #                       media_list=self.vc.media_list)
        # info_dlg.show()

    def on_changelog_action_clicked(self):
        """Show the changelog dialog."""
        changelog_dlg = ChangelogDialog(parent=self.view)
        changelog_dlg.exec_()

    def on_ffmpeg_doc_action_clicked(self):
        """Open ffmpeg documentation page."""
        self._open_url(url='https://ffmpeg.org/documentation.html')

    def on_videomorph_web_action_clicked(self):
        """Open VideoMorph Web page."""
        self._open_url(url='http://videomorph.webmisolutions.com')

    def on_tasks_list_double_clicked(self):
        """Toggle Edit triggers on task table."""
        pass
        # if (int(self.view.tasks_table.currentColumn()) == COLUMNS.QUALITY and not
        # self.conversion_lib.converter_is_running):
        #     self.view.tasks_table.setEditTriggers(
        #         QAbstractItemView.AllEditTriggers)
        # else:
        #     self.view.tasks_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #     if int(self.view.tasks_table.currentColumn()) == COLUMNS.NAME:
        #         self.view.play_input_media_file()
        #
        # self.view.update_ui_when_playing(
        #     row=self.view.tasks_table.currentIndex().row())

    def on_profiles_combo_item_changed(self, combo):
        """Update quality combo box on profile combo changes."""
        pass
        # qualities = self.profile.get_xml_profile_qualities(LOCALE)
        # self.view.populate_quality_combo(combo, qualities)
        # self.profile.update(new_quality=self.view.quality_combo.currentText())

    @staticmethod
    def _open_url(url):
        """Open URL."""
        launcher = launcher_factory()
        launcher.open_with_user_browser(url=url)

    # def _create_progress_dialog(self):
    #     label = QLabel()
    #     label.setAlignment(Qt.AlignLeft)
    #     progress_dlg = QProgressDialog(parent=self)
    #     progress_dlg.setFixedSize(500, 100)
    #     progress_dlg.setWindowTitle(self.tr('Adding Video Files...'))
    #     progress_dlg.setCancelButtonText(self.tr('Cancel'))
    #     progress_dlg.setLabel(label)
    #     progress_dlg.setModal(True)
    #     progress_dlg.setMinimum(0)
    #     progress_dlg.setMinimumDuration(0)
    #     progress_dlg.setMaximum(0)
    #     progress_dlg.setValue(0)
    #
    #     return progress_dlg
    #
    # @staticmethod
    # def _get_settings_file():
    #     return QSettings(join_path(SYS_PATHS.config, 'config.ini'),
    #                      QSettings.IniFormat)
    #
    # def _create_initial_settings(self):
    #     """Create initial settings file."""
    #     if not exists(join_path(SYS_PATHS.config, 'config.ini')):
    #         self._write_app_settings(pos=QPoint(100, 50),
    #                                  size=QSize(1096, 510),
    #                                  profile_index=0,
    #                                  preset_index=0)
    #
    # def _read_app_settings(self):
    #     """Read the app settings."""
    #     settings = self._get_settings_file()
    #     pos = settings.value("pos", QPoint(600, 200), type=QPoint)
    #     size = settings.value("size", QSize(1096, 510), type=QSize)
    #     self.resize(size)
    #     self.move(pos)
    #     if 'profile_index' and 'preset_index' in settings.allKeys():
    #         profile = settings.value('profile_index')
    #         preset = settings.value('preset_index')
    #         self.profiles_combo.setCurrentIndex(int(profile))
    #         self.quality_combo.setCurrentIndex(int(preset))
    #     if 'output_dir' in settings.allKeys():
    #         directory = str(settings.value('output_dir'))
    #         output_dir = directory if isdir(directory) else QDir.homePath()
    #         self.output_edit.setText(output_dir)
    #     if 'source_dir' in settings.allKeys():
    #         self.source_dir = str(settings.value('source_dir'))
    #
    # def _write_app_settings(self, **app_settings):
    #     """Write app settings on exit.
    #
    #     Args:
    #         app_settings (OrderedDict): OrderedDict to collect all app settings
    #     """
    #     settings_file = self._get_settings_file()
    #
    #     settings = OrderedDict(
    #         pos=self.pos(),
    #         size=self.size(),
    #         profile_index=self.profiles_combo.currentIndex(),
    #         preset_index=self.quality_combo.currentIndex(),
    #         source_dir=self.vmh.source_dir,
    #         output_dir=self.output_edit.text())
    #
    #     if app_settings:
    #         settings.update(app_settings)
    #
    #     for key, setting in settings.items():
    #         settings_file.setValue(key, setting)
    #
    # def _show_message_box(self, type_, title, msg):
    #     QMessageBox(type_, title, msg, QMessageBox.Ok, self).show()
    #
    # def notify(self, file_name):
    #     """Notify when conversion finished."""
    #     file_name = ''.join(('"', file_name, '"'))
    #     msg = file_name + ': ' + self.tr('Successfully converted')
    #     self.tray_icon.showMessage(APP_NAME, msg,
    #                                QSystemTrayIcon.Information, 2000)
    #     if exists(join_path(BASE_DIR, VM_PATHS.sounds)):
    #         sound = join_path(BASE_DIR, VM_PATHS.sounds, 'successful.wav')
    #     else:
    #         sound = join_path(SYS_PATHS.sounds, 'successful.wav')
    #     launcher = launcher_factory()
    #     launcher.sound_notify(sound)
    #
    @staticmethod
    def on_help_content():
        """Open ffmpeg documentation page."""
        if LOCALE == 'es_ES':
            file_name = 'manual_es.pdf'
        else:
            file_name = 'manual_en.pdf'

        file_path = Path(SYS_PATHS.help, file_name)

        if not file_path.is_file():
            file_path = Path(BASE_DIR, VM_PATHS.help, file_name)

        url = ''.join(('file:', file_path.__str__()))

        launcher = launcher_factory()
        launcher.open_with_user_browser(url=url)
    #
    # @staticmethod
    # def shutdown_machine():
    #     """Shutdown machine when conversion is finished."""
    #     launcher = launcher_factory()
    #     qApp.closeAllWindows()
    #     launcher.shutdown_machine()
    #
    # def populate_profiles_combo(self):
    #     """Populate profiles combobox."""
    #     # Clear combobox content
    #     self.profiles_combo.clear()
    #     # Populate the combobox with new data
    #
    #     profile_names = self.vmh.profile.get_xml_profile_qualities(LOCALE).keys()
    #     for i, profile_name in enumerate(profile_names):
    #         self.profiles_combo.addItem(profile_name)
    #         icon = QIcon(':/formats/{0}.png'.format(profile_name))
    #         self.profiles_combo.setItemIcon(i, icon)
    #
    # def populate_quality_combo(self, combo, qualities):
    #     """Populate target quality combobox.
    #
    #     Args:
    #         combo (QComboBox): List all available presets
    #     """
    #     current_profile = self.profiles_combo.currentText()
    #     if current_profile != '':
    #         combo.clear()
    #         combo.addItems(qualities[current_profile])
    #
    #         if self.tasks_table.rowCount():
    #             self._update_media_files_status()
    #
    # def output_directory(self):
    #     """Choose output directory."""
    #     directory = self._select_directory(
    #         dialog_title=self.tr('Choose Output Directory'),
    #         source_dir=self.output_edit.text())
    #
    #     if directory:
    #         self.output_edit.setText(directory)
    #         self._on_modify_conversion_option()
    #
    # def closeEvent(self, event):
    #     """Things to do on close."""
    #     # Close communication and kill the encoding process
    #     if self.vmh.conversion_lib.converter_is_running:
    #         # ask for confirmation
    #         user_answer = QMessageBox.question(
    #             self,
    #             APP_NAME,
    #             self.tr('There are on Going Conversion Tasks.'
    #                     ' Are you Sure you Want to Exit?'),
    #             QMessageBox.Yes | QMessageBox.No)
    #
    #         if user_answer == QMessageBox.Yes:
    #             # Disconnect the finished signal
    #             self.vmh.conversion_lib.converter_finished_disconnect(
    #                 connected=self._finish_file_encoding)
    #             self.vmh.conversion_lib.kill_converter()
    #             self.vmh.conversion_lib.close_converter()
    #             self.vmh.media_list.delete_running_file_output(
    #                 output_dir=self.output_edit.text(),
    #                 tagged_output=self.tag_chb.checkState())
    #             # Save settings
    #             self._write_app_settings()
    #             event.accept()
    #         else:
    #             event.ignore()
    #     else:
    #         # Save settings
    #         self._write_app_settings()
    #         event.accept()
    #
    # def _fill_media_list(self, files_paths):
    #     """Fill MediaList object with _MediaFile objects."""
    #     progress_dlg = self._create_progress_dialog()
    #
    #     for i, element in enumerate(self.vmh.media_list.populate(files_paths)):
    #         if not i:  # First element yielded
    #             progress_dlg.setMaximum(element)
    #         else:  # Second and on...
    #             progress_dlg.setLabelText(self.tr('Adding File: ') + element)
    #             progress_dlg.setValue(i)
    #
    #         if progress_dlg.wasCanceled():
    #             break
    #
    #     progress_dlg.close()
    #
    #     if self.vmh.media_list.not_added_files:
    #         msg = self.tr('Invalid Video File Information for:') + ' \n - ' + \
    #               '\n - '.join(self.vmh.media_list.not_added_files) + '\n' + \
    #               self.tr('File not Added to the List of Conversion Tasks')
    #         self._show_message_box(
    #             type_=QMessageBox.Critical,
    #             title=self.tr('Error!'),
    #             msg=msg)
    #
    #         if not self.vmh.media_list.length:
    #             self.update_ui_when_no_file()
    #         else:
    #             self.update_ui_when_ready()
    #
    # def _load_files(self, source_dir=QDir.homePath()):
    #     """Load video files."""
    #     files_paths = self._select_files(
    #         dialog_title=self.tr('Select Video Files'),
    #         files_filter=self.tr('Video Files') + ' ' +
    #         '(' + VIDEO_FILTERS + ')',
    #         source_dir=source_dir)
    #
    #     return files_paths
    #
    # def _insert_table_item(self, item_text, row, column):
    #     item = QTableWidgetItem()
    #     item.setText(item_text)
    #     if column == COLUMNS.NAME:
    #         item.setIcon(QIcon(':/icons/video-in-list.png'))
    #     self.tasks_table.setItem(row, column, item)
    #
    # def _create_table(self):
    #     self.tasks_table.setRowCount(self.vmh.media_list.length)
    #     # Call converter_is_running only once
    #     converter_is_running = self.vmh.conversion_lib.converter_is_running
    #     for row in range(self.tasks_table.rowCount()):
    #         self._insert_table_item(
    #             item_text=self.vmh.media_list.get_file_name(position=row,
    #                                                         with_extension=True),
    #             row=row, column=COLUMNS.NAME)
    #
    #         self._insert_table_item(
    #             item_text=str(write_time(
    #                 self.vmh.media_list.get_file_info(
    #                     position=row,
    #                     info_param='duration'))),
    #             row=row, column=COLUMNS.DURATION)
    #
    #         self._insert_table_item(
    #             item_text=str(self.quality_combo.currentText()),
    #             row=row, column=COLUMNS.QUALITY)
    #
    #         if converter_is_running:
    #             if row > self.vmh.media_list.position:
    #                 self._insert_table_item(item_text=self.tr('To Convert'),
    #                                         row=row, column=COLUMNS.PROGRESS)
    #         else:
    #             self._insert_table_item(item_text=self.tr('To Convert'),
    #                                     row=row, column=COLUMNS.PROGRESS)
    #
    # def add_media_files(self, *files):
    #     """Add video files to conversion list.
    #
    #     Args:
    #         files (list): List of video file paths
    #     """
    #     # Update tool buttons so you can convert, or add_file, or clear...
    #     # only if there is not a conversion process running
    #     if self.vmh.conversion_lib.converter_is_running:
    #         self.update_ui_when_converter_running()
    #     else:
    #         # Update the files status
    #         self._set_media_status()
    #         # Update ui
    #         self.update_ui_when_ready()
    #
    #     self._fill_media_list(files)
    #
    #     self._create_table()
    #
    #     # After adding files to the list, recalculate the list duration
    #     self.vmh.media_list_duration = self.vmh.media_list.duration
    #
    def on_play_input_media_file(self):
        """Play the input video using an available video player."""
        pass
    #     row = self.tasks_table.currentIndex().row()
    #     self._play_media_file(file_path=self.vmh.media_list.get_file_path(row))
    #     self.update_ui_when_playing(row)
    #
    # def _get_output_path(self, row):
    #     path = self.vmh.media_list.get_file(row).get_output_path(
    #         output_dir=self.output_edit.text(),
    #         tagged_output=self.tag_chb.checkState())
    #     return path
    #
    def on_play_output_media_file(self):
        """Play the output video using an available video player."""
        pass
    #     row = self.tasks_table.currentIndex().row()
    #     path = self._get_output_path(row)
    #     self._play_media_file(file_path=path)
    #     self.update_ui_when_playing(row)
    #
    # def _play_media_file(self, file_path):
    #     """Play a video using an available video player."""
    #     try:
    #         self.vmh.conversion_lib.run_player(file_path=file_path)
    #     except PlayerNotFoundError:
    #         self._show_message_box(
    #             type_=QMessageBox.Critical,
    #             title=self.tr('Error!'),
    #             msg=self.tr('No Video Player Found in your System'))
    #
    def on_load_media_files(self):
        """Add media files to the list of conversion tasks."""
        pass
        # files_paths = self._load_files(source_dir=self.source_dir)
    #     # If no file is selected then return
    #     if files_paths is None:
    #         return
    #
    #     self.add_media_files(*files_paths)
    #
    def on_load_media_dir(self):
        """Add media files from a directory recursively."""
        pass
    #     directory = self._select_directory(
    #         dialog_title=self.tr('Select Directory'),
    #         source_dir=self.source_dir)
    #
    #     if not directory:
    #         return
    #
    #     try:
    #         media_files = search_directory_recursively(directory)
    #         self.source_dir = directory
    #         self.add_media_files(*media_files)
    #     except FileNotFoundError:
    #         self._show_message_box(
    #             type_=QMessageBox.Critical,
    #             title=self.tr('Error!'),
    #             msg=self.tr('No Video Files Found in:' + ' ' + directory))
    #
    def on_remove_media_file(self):
        """Remove selected media file from the list."""
        pass
    #     file_row = self.tasks_table.currentItem().row()
    #
    #     msg_box = QMessageBox(
    #         QMessageBox.Warning,
    #         self.tr('Warning!'),
    #         self.tr('Remove Video File from the List of Conversion Tasks?'),
    #         QMessageBox.NoButton, self)
    #
    #     msg_box.addButton(self.tr("&Yes"), QMessageBox.AcceptRole)
    #     msg_box.addButton(self.tr("&No"), QMessageBox.RejectRole)
    #
    #     if msg_box.exec_() == QMessageBox.AcceptRole:
    #         # Delete file from table
    #         self.tasks_table.removeRow(file_row)
    #         # Remove file from self.vc.media_list
    #         self.vmh.media_list.delete_file(position=file_row)
    #         self.vmh.media_list.position = None
    #         self.vmh.media_list_duration = self.vmh.media_list.duration
    #
    #     # If all files are deleted... update the interface
    #     if not self.tasks_table.rowCount():
    #         self._reset_options_check_boxes()
    #         self.update_ui_when_no_file()
    #
    def on_add_customized_profile(self):
        """Show dialog for adding conversion profiles."""
        pass
    #     add_profile_dlg = AddProfileDialog(parent=self)
    #     add_profile_dlg.exec_()
    #
    # def _export_import_profiles(self, func, path, msg_info):
    #     try:
    #         func(path)
    #     except PermissionError:
    #         self._show_message_box(
    #             type_=QMessageBox.Critical,
    #             title=self.tr('Error!'),
    #             msg=self.tr('Can not Write to Selected Directory'))
    #     else:
    #         self._show_message_box(type_=QMessageBox.Information,
    #                                title=self.tr('Information!'),
    #                                msg=msg_info)
    #
    # def _select_directory(self, dialog_title, source_dir=QDir.homePath()):
    #     options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
    #
    #     directory = QFileDialog.getExistingDirectory(self,
    #                                                  dialog_title,
    #                                                  source_dir,
    #                                                  options=options)
    #     return directory
    #
    def on_export_profiles(self):
        """Export conversion profiles."""
        pass
    #     directory = self._select_directory(
    #         dialog_title=self.tr('Export to Directory'))
    #
    #     if directory:
    #         msg_info = self.tr('Conversion Profiles Successfully Exported!')
    #         self._export_import_profiles(
    #             func=self.vmh.profile.export_xml_profiles,
    #             path=directory, msg_info=msg_info)
    #
    def on_import_profiles(self):
        """Import conversion profiles."""
        pass
    #     file_path = self._select_files(
    #         dialog_title=self.tr('Select a Profiles File'),
    #         files_filter=self.tr('Profiles Files ') + '(*.xml)',
    #         single_file=True)
    #
    #     if file_path:
    #         msg_info = self.tr('Conversion Profiles Successfully Imported!')
    #
    #         self._export_import_profiles(
    #             func=self.vmh.profile.import_xml_profiles,
    #             path=file_path, msg_info=msg_info)
    #         self.populate_profiles_combo()
    #         self.vmh.profile.update(new_quality=self.quality_combo.currentText())
    #
    def on_restore_profiles(self):
        """Restore default profiles."""
        pass
    #     msg_box = QMessageBox(
    #         QMessageBox.Warning,
    #         self.tr('Warning!'),
    #         self.tr('Do you Really Want to Restore the '
    #                 'Default Conversion Profiles?'),
    #         QMessageBox.NoButton, self)
    #
    #     msg_box.addButton(self.tr("&Yes"), QMessageBox.AcceptRole)
    #     msg_box.addButton(self.tr("&No"), QMessageBox.RejectRole)
    #
    #     if msg_box.exec_() == QMessageBox.AcceptRole:
    #         self.vmh.profile.restore_default_profiles()
    #         self.populate_profiles_combo()
    #         self.vmh.profile.update(new_quality=self.quality_combo.currentText())
    #
    # def _select_files(self, dialog_title, files_filter,
    #                   source_dir=QDir.homePath(), single_file=False):
    #     # Validate source_dir
    #     source_directory = source_dir if isdir(source_dir) else QDir.homePath()
    #
    #     # Select media files and store their path
    #     if single_file:
    #         files_paths, _ = QFileDialog.getOpenFileName(self,
    #                                                      dialog_title,
    #                                                      source_directory,
    #                                                      files_filter)
    #     else:
    #         files_paths, _ = QFileDialog.getOpenFileNames(self,
    #                                                       dialog_title,
    #                                                       source_directory,
    #                                                       files_filter)
    #
    #     if files_paths:
    #         # Update the source directory
    #         if not single_file:
    #             self.source_dir = dirname(files_paths[0])
    #     else:
    #         return None
    #
    #     return files_paths
    #
    def on_clear_media_list(self):
        """Clear media conversion list with user confirmation."""
        pass
    #     msg_box = QMessageBox(
    #         QMessageBox.Warning,
    #         self.tr('Warning!'),
    #         self.tr('Remove all Conversion Tasks from the List?'),
    #         QMessageBox.NoButton, self)
    #
    #     msg_box.addButton(self.tr("&Yes"), QMessageBox.AcceptRole)
    #     msg_box.addButton(self.tr("&No"), QMessageBox.RejectRole)
    #
    #     if msg_box.exec_() == QMessageBox.AcceptRole:
    #         # If user says YES clear table of conversion tasks
    #         self.tasks_table.clearContents()
    #         self.tasks_table.setRowCount(0)
    #         # Clear MediaList so it contains no element
    #         self.vmh.media_list.clear()
    #         # Update UI
    #         self._reset_options_check_boxes()
    #         self.update_ui_when_no_file()
    #
    def on_start_encoding(self):
        """Start the encoding process."""
        pass
    #     self.update_ui_when_converter_running()
    #
    #     self.vmh.media_list.position += 1
    #     self.vmh.timer.operation_start_time = 0.0
    #
    #     if self.vmh.media_list.running_file_status == STATUS.todo:
    #         try:
    #             # Fist build the conversion command
    #             conversion_cmd = self.vmh.media_list.running_file_conversion_cmd(
    #                 target_quality=self.tasks_table.item(
    #                     self.vmh.media_list.position,
    #                     COLUMNS.QUALITY).text(),
    #                 output_dir=self.output_edit.text(),
    #                 tagged_output=self.tag_chb.checkState(),
    #                 subtitle=bool(self.subtitle_chb.checkState()))
    #             # Then pass it to the _converter
    #             self.vmh.conversion_lib.start_converter(cmd=conversion_cmd)
    #         except PermissionError:
    #             self._show_message_box(
    #                 type_=QMessageBox.Critical,
    #                 title=self.tr('Error!'),
    #                 msg=self.tr('Can not Write to Selected Directory'))
    #             self.update_ui_when_error_on_conversion()
    #         except FileNotFoundError:
    #             self._show_message_box(
    #                 type_=QMessageBox.Critical,
    #                 title=self.tr('Error!'),
    #                 msg=(self.tr('Input Video File:') + ' ' +
    #                      self.vmh.media_list.running_file_name(
    #                          with_extension=True) + ' ' +
    #                      self.tr('not Found')))
    #             self.update_ui_when_error_on_conversion()
    #         except FileExistsError:
    #             self._show_message_box(
    #                 type_=QMessageBox.Critical,
    #                 title=self.tr('Error!'),
    #                 msg=(self.tr('Video File:') + ' ' +
    #                      self.vmh.media_list.running_file_output_name(
    #                          output_dir=self.output_edit.text(),
    #                          tagged_output=self.tag_chb.checkState()) + ' ' +
    #                      self.tr('Already Exists in '
    #                              'Output Directory. Please, Change the '
    #                              'Output Directory')))
    #             self.update_ui_when_error_on_conversion()
    #     else:
    #         self._end_encoding_process()
    #
    def on_stop_file_encoding(self):
        """Stop file encoding process and continue with the list."""
        pass
    #     # Terminate the file encoding
    #     self.vmh.conversion_lib.stop_converter()
    #     # Set _MediaFile.status attribute
    #     self.vmh.media_list.running_file_status = STATUS.stopped
    #     # Delete the file when conversion is stopped by the user
    #     self.vmh.media_list.delete_running_file_output(
    #         output_dir=self.output_edit.text(),
    #         tagged_output=self.tag_chb.checkState())
    #     # Update the list duration and partial time for total progress bar
    #     self.vmh.timer.reset_progress_times()
    #     self.vmh.media_list_duration = self.vmh.media_list.duration
    #
    def on_stop_all_files_encoding(self):
        """Stop the conversion process for all the files in list."""
        pass
    #     # Delete the file when conversion is stopped by the user
    #     self.vmh.conversion_lib.stop_converter()
    #     self.vmh.media_list.delete_running_file_output(
    #         output_dir=self.output_edit.text(),
    #         tagged_output=self.tag_chb.checkState())
    #     for media_file in self.vmh.media_list:
    #         # Set _MediaFile.status attribute
    #         if media_file.status != STATUS.done:
    #             media_file.status = STATUS.stopped
    #             self.vmh.media_list.position = self.vmh.media_list.index(media_file)
    #             self.tasks_table.item(
    #                 self.vmh.media_list.position,
    #                 COLUMNS.PROGRESS).setText(self.tr('Stopped!'))
    #
    #     # Update the list duration and partial time for total progress bar
    #     self.vmh.timer.reset_progress_times()
    #     self.vmh.media_list_duration = self.vmh.media_list.duration
    #
    # def _end_encoding_process(self):
    #     """End up the encoding process."""
    #     # Test if encoding process is finished
    #     if self.vmh.media_list.is_exhausted:
    #
    #         if self.vmh.conversion_lib.error is not None:
    #             self._show_message_box(
    #                 type_=QMessageBox.Critical,
    #                 title='Error!',
    #                 msg=self.tr('The Conversion Library has '
    #                             'Failed with Error:') + ' ' +
    #                 self.vmh.conversion_lib.error)
    #             self.vmh.conversion_lib.error = None
    #         elif not self.vmh.media_list.all_stopped:
    #             if self.shutdown_chb.checkState():
    #                 self.shutdown_machine()
    #                 return
    #             self._show_message_box(
    #                 type_=QMessageBox.Information,
    #                 title=self.tr('Information!'),
    #                 msg=self.tr('Encoding Process Successfully Finished!'))
    #         else:
    #             self._show_message_box(
    #                 type_=QMessageBox.Information,
    #                 title=self.tr('Information!'),
    #                 msg=self.tr('Encoding Process Stopped by the User!'))
    #
    #         self.setWindowTitle(self.title)
    #         self.statusBar().showMessage(self.tr('Ready'))
    #         self._reset_options_check_boxes()
    #         # Reset all progress related variables
    #         self._reset_progress_bars()
    #         self.vmh.timer.reset_progress_times()
    #         self.vmh.media_list_duration = self.vmh.media_list.duration
    #         self.vmh.timer.process_start_time = 0.0
    #         # Reset the position
    #         self.vmh.media_list.position = None
    #         # Update tool buttons
    #         self.update_ui_when_problem()
    #     else:
    #         self.start_encoding()
    #
    #
    # def _reset_progress_bars(self):
    #     """Reset the progress bars."""
    #     self.operation_pb.setProperty("value", 0)
    #     self.total_pb.setProperty("value", 0)
    #
    # def update_conversion_progress(self):
    #     """Read the encoding output from the converter stdout."""
    #     # Initialize the process time
    #     if not self.vmh.timer.process_start_time:
    #         self.vmh.timer.init_process_start_time()
    #
    #     # Initialize the operation time
    #     if not self.vmh.timer.operation_start_time:
    #         self.vmh.timer.init_operation_start_time()
    #
    #     # Return if no time read
    #     if not self.vmh.reader.has_time_read:
    #         # Catch the library errors only before time_read
    #         self.vmh.conversion_lib.catch_errors()
    #         return
    #
    #     self.vmh.timer.update_time(op_time_read_sec=self.vmh.reader.time)
    #
    #     self.vmh.timer.update_cum_times()
    #
    #     file_duration = float(self.vmh.media_list.running_file_info('duration'))
    #
    #     operation_progress = self.vmh.timer.operation_progress(
    #         file_duration=file_duration)
    #
    #     process_progress = self.vmh.timer.process_progress(
    #         list_duration=self.vmh.media_list_duration)
    #
    #     self._update_progress(op_progress=operation_progress,
    #                           pr_progress=process_progress)
    #
    #     self._update_status_bar()
    #
    #     self._update_main_window_title(op_progress=operation_progress)
    #
    # def _update_progress(self, op_progress, pr_progress):
    #     """Update operation progress in tasks list & operation progress bar."""
    #     # Update operation progress bar
    #     self.operation_pb.setProperty("value", op_progress)
    #     # Update operation progress in tasks list
    #     self.tasks_table.item(self.vmh.media_list.position, 3).setText(
    #         str(op_progress) + "%")
    #     self.total_pb.setProperty("value", pr_progress)
    #
    # def _update_main_window_title(self, op_progress):
    #     """Update the main window title."""
    #     running_file_name = self.vmh.media_list.running_file_name(
    #         with_extension=True)
    #
    #     self.setWindowTitle(str(op_progress) + '%' + '-' +
    #                         '[' + running_file_name + ']' +
    #                         ' - ' + APP_NAME + ' ' + VERSION)
    #
    # def _update_status_bar(self):
    #     """Update the status bar while converting."""
    #     file_duration = float(self.vmh.media_list.running_file_info('duration'))
    #
    #     self.statusBar().showMessage(
    #         self.tr('Converting: {m}\t\t\t '
    #                 'At: {br}\t\t\t '
    #                 'Operation Remaining Time: {ort}\t\t\t '
    #                 'Total Elapsed Time: {tet}').format(
    #                     m=self.vmh.media_list.running_file_name(
    #                         with_extension=True),
    #                     br=self.vmh.reader.bitrate,
    #                     ort=self.vmh.timer.operation_remaining_time(
    #                         file_duration=file_duration),
    #                     tet=write_time(self.vmh.timer.process_cum_time)))
    #
    # def _update_media_files_status(self):
    #     """Update file status."""
    #     # Current item
    #     item = self.tasks_table.currentItem()
    #     if item is not None:
    #         # Update target_quality in table
    #         self.tasks_table.item(item.row(), COLUMNS.QUALITY).setText(
    #             str(self.quality_combo.currentText()))
    #
    #         # Update table Progress field if file is: Done or Stopped
    #         self.update_table_progress_column(row=item.row())
    #
    #         # Update file Done or Stopped status
    #         self.vmh.media_list.set_file_status(position=item.row(),
    #                                             status=STATUS.todo)
    #
    #     else:
    #         self._update_all_table_rows(column=COLUMNS.QUALITY,
    #                                     value=self.quality_combo.currentText())
    #
    #         self._set_media_status()
    #
    #     # Update total duration of the new tasks list
    #     self.vmh.media_list_duration = self.vmh.media_list.duration
    #     # Update the interface
    #     self.update_ui_when_ready()
    #
    # def _update_all_table_rows(self, column, value):
    #     rows = self.tasks_table.rowCount()
    #     if rows:
    #         for row in range(rows):
    #             self.tasks_table.item(row, column).setText(
    #                 str(value))
    #             self.update_table_progress_column(row)
    #
    # def update_table_progress_column(self, row):
    #     """Update the progress column of conversion task list."""
    #     if self.vmh.media_list.get_file_status(row) != STATUS.todo:
    #         self.tasks_table.item(
    #             row,
    #             COLUMNS.PROGRESS).setText(self.tr('To Convert'))
    #
    # def _reset_options_check_boxes(self):
    #     self.delete_chb.setChecked(False)
    #     self.tag_chb.setChecked(False)
    #     self.subtitle_chb.setChecked(False)
    #     self.shutdown_chb.setChecked(False)
    #
    # def _set_media_status(self):
    #     """Update media files state of conversion."""
    #     for media_file in self.vmh.media_list:
    #         media_file.status = STATUS.todo
    #     self.vmh.media_list.position = None
    #
    # def _on_modify_conversion_option(self):
    #     if self.vmh.media_list.length:
    #         self.update_ui_when_ready()
    #         self._set_media_status()
    #         self._update_all_table_rows(column=COLUMNS.PROGRESS,
    #                                     value=self.tr('To Convert'))
    #         self.vmh.media_list_duration = self.vmh.media_list.duration
    #
    # def _update_ui(self, **i_vars):
    #     """Update the interface status.
    #
    #     Args:
    #         i_vars (dict): Dict to collect all the interface variables
    #     """
    #     variables = dict(add=True,
    #                      convert=True,
    #                      clear=True,
    #                      remove=True,
    #                      stop=True,
    #                      stop_all=True,
    #                      presets=True,
    #                      profiles=True,
    #                      add_costume_profile=True,
    #                      import_profile=True,
    #                      restore_profile=True,
    #                      output_dir=True,
    #                      subtitles_chb=True,
    #                      delete_chb=True,
    #                      tag_chb=True,
    #                      shutdown_chb=True,
    #                      play_input=True,
    #                      play_output=True,
    #                      info=True)
    #
    #     variables.update(i_vars)
    #
    #     self.open_media_file_action.setEnabled(variables['add'])
    #     self.convert_action.setEnabled(variables['convert'])
    #     self.clear_media_list_action.setEnabled(variables['clear'])
    #     self.remove_media_file_action.setEnabled(variables['remove'])
    #     self.stop_action.setEnabled(variables['stop'])
    #     self.stop_all_action.setEnabled(variables['stop_all'])
    #     self.quality_combo.setEnabled(variables['presets'])
    #     self.profiles_combo.setEnabled(variables['profiles'])
    #     self.add_profile_action.setEnabled(variables['add_costume_profile'])
    #     self.import_profile_action.setEnabled(variables['import_profile'])
    #     self.restore_profile_action.setEnabled(variables['restore_profile'])
    #     self.output_btn.setEnabled(variables['output_dir'])
    #     self.subtitle_chb.setEnabled(variables['subtitles_chb'])
    #     self.delete_chb.setEnabled(variables['delete_chb'])
    #     self.tag_chb.setEnabled(variables['tag_chb'])
    #     self.shutdown_chb.setEnabled(variables['shutdown_chb'])
    #     self.play_input_media_file_action.setEnabled(variables['play_input'])
    #     self.play_output_media_file_action.setEnabled(variables['play_output'])
    #     self.info_action.setEnabled(variables['info'])
    #     self.tasks_table.setCurrentItem(None)
    #
    # def update_ui_when_no_file(self):
    #     """User cannot perform any action but to add files to list."""
    #     self._update_ui(clear=False,
    #                     remove=False,
    #                     convert=False,
    #                     stop=False,
    #                     stop_all=False,
    #                     profiles=False,
    #                     presets=False,
    #                     subtitles_chb=False,
    #                     delete_chb=False,
    #                     tag_chb=False,
    #                     shutdown_chb=False,
    #                     play_input=False,
    #                     play_output=False,
    #                     info=False)
    #
    # def update_ui_when_ready(self):
    #     """Update UI when app is ready to start conversion."""
    #     self._update_ui(stop=False,
    #                     stop_all=False,
    #                     remove=False,
    #                     play_input=False,
    #                     play_output=False,
    #                     info=False)
    #
    # def update_ui_when_playing(self, row):
    #     if self.vmh.conversion_lib.converter_is_running:
    #         self.update_ui_when_converter_running()
    #     elif self.vmh.media_list.get_file_status(row) == STATUS.todo:
    #         self.update_ui_when_ready()
    #     else:
    #         self.update_ui_when_problem()
    #
    # def update_ui_when_problem(self):
    #     self._update_ui(convert=False,
    #                     stop=False,
    #                     stop_all=False,
    #                     remove=False,
    #                     play_input=False,
    #                     play_output=False,
    #                     info=False)
    #
    # def update_ui_when_converter_running(self):
    #     self._update_ui(presets=False,
    #                     profiles=False,
    #                     subtitles_chb=False,
    #                     add_costume_profile=False,
    #                     import_profile=False,
    #                     restore_profile=False,
    #                     convert=False,
    #                     clear=False,
    #                     remove=False,
    #                     output_dir=False,
    #                     delete_chb=False,
    #                     tag_chb=False,
    #                     play_input=False,
    #                     play_output=False,
    #                     info=False)
    #
    # def update_ui_when_error_on_conversion(self):
    #     self.vmh.timer.reset_progress_times()
    #     self.vmh.media_list_duration = self.vmh.media_list.duration
    #     self.vmh.media_list.position = None
    #     self._reset_progress_bars()
    #     self._set_window_title()
    #     self._reset_options_check_boxes()
    #     self.update_ui_when_ready()
    #
    # def _enable_context_menu_action(self):
    #     if not self.vmh.conversion_lib.converter_is_running:
    #         self.remove_media_file_action.setEnabled(True)
    #
    #     self.play_input_media_file_action.setEnabled(True)
    #
    #     path = self._get_output_path(row=self.tasks_table.currentIndex().row())
    #     # Only enable the menu if output file exist and if it not .mp4,
    #     # cause .mp4 files doesn't run until conversion is finished
    #     self.play_output_media_file_action.setEnabled(
    #         exists(path) and self.profiles_combo.currentText() != 'MP4')
    #     self.info_action.setEnabled(bool(self.vmh.media_list.length))
