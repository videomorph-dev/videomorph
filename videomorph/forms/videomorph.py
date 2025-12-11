from functools import partial
from pathlib import Path

from PyQt6.QtCore import (
    QCoreApplication,
    QDir,
    QPoint,
    QProcess,
    QSettings,
    QSize,
    Qt,
)
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QProgressDialog,
    QSizePolicy,
    QTableWidgetItem,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from videomorph import __app_name__, __version__
from videomorph.converter.constants import (
    LOCALE,
    STATUS,
    VIDEO_FILTERS,
)
from videomorph.converter.launchers import launcher_factory
from videomorph.converter.manager import ConversionManager
from videomorph.converter.paths import path_manager
from videomorph.converter.profile import Profile
from videomorph.converter.tasklist import TaskList
from videomorph.converter.utils import search_directory_recursively, write_time
from videomorph.forms import COLUMNS
from videomorph.forms import videomorph_qrc as _videomorph_qrc
from videomorph.forms.about import AboutVMDialog
from videomorph.forms.actions import ACTION_SPECS
from videomorph.forms.changelog import ChangelogDialog
from videomorph.forms.info import InfoDialog
from videomorph.forms.settings import SettingsManager
from videomorph.forms.ui_state import UI_STATE_CONFIG, AppState
from videomorph.forms.vmwidgets import TasksListTable

_ = _videomorph_qrc  # Ensure Qt resources are registered.


class VideoMorphMW(QMainWindow):
    """VideoMorph Main Window class."""

    def __init__(self):
        super(VideoMorphMW, self).__init__()
        self.title = __app_name__ + " " + __version__
        self.icon = self._get_app_icon()
        self.source_dir = QDir.homePath()
        self.task_list_duration = 0.0
        self.settings_manager = SettingsManager()

        self._setup_ui()
        self._setup_model()
        self.populate_profiles_combo()
        self._load_app_settings()

    def _setup_model(self):
        self.manager = ConversionManager(output_dir=self.output_edit.text())
        self.manager.task_started.connect(self._on_task_started)
        self.manager.task_finished.connect(self._on_task_finished)
        self.manager.all_finished.connect(self._on_all_finished)
        self.manager.error.connect(self._on_conversion_error)
        self.manager.progress_updated.connect(self._on_progress_updated)
        self.manager.time_updated.connect(self._on_time_updated)

        warning_msg = self.manager.consume_profile_warning()
        if warning_msg:
            self._show_message_box(QMessageBox.Icon.Warning, warning_msg)

    def _setup_ui(self):
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
        self._create_context_menu()
        self.set_ui_state(AppState.EMPTY)

    @staticmethod
    def _get_app_icon():
        icon = QIcon()
        icon.addPixmap(QPixmap(":/icons/videomorph.ico"))
        return icon

    def _create_general_layout(self):
        general_layout = QHBoxLayout(self.central_widget)
        settings_layout = QVBoxLayout()
        settings_layout.addWidget(self._group_settings())
        conversion_layout = QVBoxLayout()
        conversion_layout.addWidget(self._group_tasks_list())
        conversion_layout.addWidget(self._group_output_directory())
        conversion_layout.addWidget(self._group_progress())
        general_layout.addLayout(settings_layout)
        general_layout.addLayout(conversion_layout)

    def _group_settings(self):
        settings_gb = QGroupBox(self.central_widget)
        settings_gb.setTitle(self.tr("Conversion Options"))
        size_policy = QSizePolicy(
            QSizePolicy.Policy.Fixed,
            QSizePolicy.Policy.Preferred,
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(settings_gb.sizePolicy().hasHeightForWidth())
        settings_gb.setSizePolicy(size_policy)

        settings_layout = QVBoxLayout()

        convert_label = QLabel(self.tr("Target Format:"))
        settings_layout.addWidget(convert_label)

        profile_tip = self.tr("Select a Video Format")
        self.profiles_combo = QComboBox(
            settings_gb,
            statusTip=profile_tip,
            toolTip=profile_tip,
        )
        self.profiles_combo.setMinimumSize(QSize(200, 0))
        self.profiles_combo.setIconSize(QSize(22, 22))
        settings_layout.addWidget(self.profiles_combo)

        quality_label = QLabel(self.tr("Target Quality:"))
        settings_layout.addWidget(quality_label)

        preset_tip = self.tr("Select a Video Target Quality")
        self.quality_combo = QComboBox(
            settings_gb,
            statusTip=preset_tip,
            toolTip=preset_tip,
        )
        self.quality_combo.setMinimumSize(QSize(200, 0))
        self.profiles_combo.currentIndexChanged.connect(
            partial(self.populate_quality_combo, self.quality_combo)
        )
        self.quality_combo.activated.connect(self._update_media_files_status)
        settings_layout.addWidget(self.quality_combo)

        options_label = QLabel(self.tr("Other Options:"))
        settings_layout.addWidget(options_label)

        sub_tip = self.tr("Insert Subtitles if Available in Source Directory")
        self.subtitle_chb = QCheckBox(
            self.tr("Insert Subtitles if Available"),
            statusTip=sub_tip,
            toolTip=sub_tip,
        )
        self.subtitle_chb.setChecked(
            False
        )  # Ensure unchecked by default - user must opt-in
        self.subtitle_chb.clicked.connect(self._on_modify_conversion_option)
        settings_layout.addWidget(self.subtitle_chb)

        del_text = self.tr("Delete Input Video Files when Finished")
        self.delete_chb = QCheckBox(del_text, statusTip=del_text, toolTip=del_text)
        self.delete_chb.setChecked(False)  # Ensure unchecked by default for safety
        self.delete_chb.clicked.connect(self._on_delete_checkbox_clicked)
        settings_layout.addWidget(self.delete_chb)

        tag_text = self.tr("Use Format Tag in Output Video File Name")
        tag_tip_text = (
            tag_text
            + ". "
            + self.tr("Useful when Converting a " "Video File to Multiples Formats")
        )
        self.tag_chb = QCheckBox(tag_text, statusTip=tag_tip_text, toolTip=tag_tip_text)
        self.tag_chb.setChecked(False)  # Ensure unchecked by default - user must opt-in
        self.tag_chb.clicked.connect(self._on_modify_conversion_option)
        settings_layout.addWidget(self.tag_chb)

        shutdown_text = self.tr("Shutdown Computer when Conversion Finished")
        self.shutdown_chb = QCheckBox(
            shutdown_text,
            statusTip=shutdown_text,
            toolTip=shutdown_text,
        )
        settings_layout.addWidget(self.shutdown_chb)
        settings_layout.addStretch()

        settings_gb.setLayout(settings_layout)

        return settings_gb

    def _group_tasks_list(self):
        tasks_gb = QGroupBox(self.central_widget)
        tasks_text = self.tr("List of Conversion Tasks")
        tasks_gb.setTitle(tasks_text)
        size_policy = QSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred
        )
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(tasks_gb.sizePolicy().hasHeightForWidth())
        tasks_gb.setSizePolicy(size_policy)

        tasks_layout = QVBoxLayout()

        self.tasks_table = TasksListTable(parent=tasks_gb, window=self)
        self.tasks_table.cellPressed.connect(self._enable_context_menu_action)
        # Connect to selection change to update remove action state
        self.tasks_table.itemSelectionChanged.connect(self._on_table_selection_changed)
        self.tasks_table.doubleClicked.connect(self._update_edit_triggers)
        tasks_layout.addWidget(self.tasks_table)
        tasks_gb.setLayout(tasks_layout)

        return tasks_gb

    def _group_output_directory(self):
        output_dir_gb = QGroupBox(self.central_widget)
        output_dir_gb.setTitle(self.tr("Output Folder"))

        output_dir_layout = QHBoxLayout(output_dir_gb)

        outputdir_tip = self.tr("Choose the Output Folder")
        self.output_edit = QLineEdit(
            str(QDir.homePath()),
            statusTip=outputdir_tip,
            toolTip=outputdir_tip,
        )
        self.output_edit.setReadOnly(True)
        output_dir_layout.addWidget(self.output_edit)

        outputbtn_tip = self.tr("Choose the Output Folder")
        self.output_btn = QToolButton(
            output_dir_gb,
            statusTip=outputbtn_tip,
            toolTip=outputbtn_tip,
        )
        self.output_btn.setIcon(QIcon(":/icons/output-folder.png"))
        self.output_btn.clicked.connect(self.output_directory)
        output_dir_layout.addWidget(self.output_btn)

        output_dir_gb.setLayout(output_dir_layout)

        return output_dir_gb

    def _group_progress(self):
        progress_gb = QGroupBox(self.central_widget)
        progress_gb.setTitle(self.tr("Progress"))

        progress_layout = QVBoxLayout()

        progress_label = QLabel(self.tr("Operation Progress"))
        progress_layout.addWidget(progress_label)

        self.operation_pb = QProgressBar()
        self.operation_pb.setProperty("value", 0)
        progress_layout.addWidget(self.operation_pb)

        total_progress_label = QLabel(self.tr("Total Progress"))
        progress_layout.addWidget(total_progress_label)

        self.total_pb = QProgressBar()
        self.total_pb.setProperty("value", 0)
        progress_layout.addWidget(self.total_pb)

        progress_gb.setLayout(progress_layout)

        return progress_gb

    def _create_actions(self):
        for spec in ACTION_SPECS:
            text = self.tr(spec["text"])
            if spec.get("format_title"):
                text = text.format(app=__app_name__, title=self.title)
            action = QAction(text, self)
            if icon_path := spec.get("icon"):
                action.setIcon(QIcon(icon_path))
            if shortcut := spec.get("shortcut"):
                action.setShortcut(shortcut)
            if tip := spec.get("tip"):
                tip_text = self.tr(tip)
                if spec.get("format_title"):
                    tip_text = tip_text.format(app=__app_name__, title=self.title)
                action.setToolTip(tip_text)
                action.setStatusTip(tip_text)
            action.triggered.connect(getattr(self, spec["callback"]))
            setattr(self, spec["attr"], action)

    def _create_context_menu(self):
        first_separator = QAction(self)
        first_separator.setSeparator(True)
        second_separator = QAction(self)
        second_separator.setSeparator(True)
        self.tasks_table.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        self.tasks_table.addAction(getattr(self, "open_media_file_action"))
        self.tasks_table.addAction(getattr(self, "open_media_dir_action"))
        self.tasks_table.addAction(first_separator)
        self.tasks_table.addAction(getattr(self, "remove_media_file_action"))
        self.tasks_table.addAction(getattr(self, "clear_media_list_action"))
        self.tasks_table.addAction(second_separator)
        self.tasks_table.addAction(getattr(self, "play_input_media_file_action"))
        self.tasks_table.addAction(getattr(self, "play_output_media_file_action"))
        self.tasks_table.addAction(getattr(self, "info_action"))

    def _create_main_menu(self):
        """Create main app menu."""
        # File menu
        self.file_menu = self.menuBar().addMenu(self.tr("&File"))
        self.file_menu.addAction(getattr(self, "open_media_file_action"))
        self.file_menu.addAction(getattr(self, "open_media_dir_action"))
        self.file_menu.addSeparator()
        self.file_menu.addAction(getattr(self, "exit_action"))
        # Edit menu
        self.edit_menu = self.menuBar().addMenu(self.tr("&Edit"))
        self.edit_menu.addAction(getattr(self, "clear_media_list_action"))
        self.edit_menu.addAction(getattr(self, "remove_media_file_action"))
        # Conversion menu
        self.conversion_menu = self.menuBar().addMenu(self.tr("&Conversion"))
        self.conversion_menu.addAction(getattr(self, "convert_action"))
        self.conversion_menu.addSeparator()
        self.conversion_menu.addAction(getattr(self, "stop_action"))
        self.conversion_menu.addAction(getattr(self, "stop_all_action"))
        # Help menu
        self.help_menu = self.menuBar().addMenu(self.tr("&Help"))
        self.help_menu.addAction(getattr(self, "help_content_action"))
        self.help_menu.addAction(getattr(self, "changelog_action"))
        self.help_menu.addAction(getattr(self, "videomorph_web_action"))
        self.help_menu.addSeparator()
        self.help_menu.addAction(getattr(self, "ffmpeg_doc_action"))
        self.help_menu.addSeparator()
        self.help_menu.addAction(getattr(self, "about_action"))

    def _create_toolbar(self):
        """Create a toolbar and add it to the interface."""
        self.tool_bar = QToolBar(self)
        # Add actions to the tool bar
        self.tool_bar.addAction(getattr(self, "open_media_file_action"))
        self.tool_bar.addAction(getattr(self, "open_media_dir_action"))
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(getattr(self, "clear_media_list_action"))
        self.tool_bar.addAction(getattr(self, "remove_media_file_action"))
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(getattr(self, "convert_action"))
        self.tool_bar.addAction(getattr(self, "stop_action"))
        self.tool_bar.addAction(getattr(self, "stop_all_action"))
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(getattr(self, "exit_action"))
        self.tool_bar.setIconSize(QSize(28, 28))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        # Add the toolbar to main window
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tool_bar)

    def _create_status_bar(self):
        """Create app status bar."""
        status_bar = self.statusBar()
        if status_bar is not None:
            status_bar.showMessage(self.tr("Ready"))

    def _create_progress_dialog(self):
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        progress_dlg = QProgressDialog(parent=self)
        progress_dlg.setFixedSize(500, 100)
        progress_dlg.setWindowTitle(self.tr("Adding Videos..."))
        progress_dlg.setCancelButtonText(self.tr("Cancel"))
        progress_dlg.setLabel(label)
        progress_dlg.setWindowModality(Qt.WindowModality.ApplicationModal)
        progress_dlg.setMinimumDuration(100)
        QCoreApplication.processEvents()
        return progress_dlg

    def _update_edit_triggers(self):
        """Toggle Edit triggers on task table."""
        if (
            int(self.tasks_table.currentColumn()) == COLUMNS.QUALITY
            and not self.manager.is_running
        ):
            self.tasks_table.setEditTriggers(
                QAbstractItemView.EditTrigger.AllEditTriggers
            )
        else:
            self.tasks_table.setEditTriggers(
                QAbstractItemView.EditTrigger.NoEditTriggers
            )
            if int(self.tasks_table.currentColumn()) == COLUMNS.NAME:
                self.play_video()

        self._update_ui_when_playing(row=self.tasks_table.currentIndex().row())

    def _load_app_settings(self):
        """Read the app settings."""
        settings = self.settings_manager.read()

        self.move(settings.pos)
        self.resize(settings.size)
        self.profiles_combo.setCurrentIndex(settings.profile_index)
        self.quality_combo.setCurrentIndex(settings.preset_index)
        self.output_edit.setText(settings.output_dir)
        self.manager.output_dir = settings.output_dir
        self.source_dir = settings.source_dir

    def _write_app_settings(self):
        """Write app settings on exit."""
        self.settings_manager.write(
            pos=self.pos(),
            size=self.size(),
            profile_index=self.profiles_combo.currentIndex(),
            preset_index=self.quality_combo.currentIndex(),
            source_dir=self.source_dir,
            output_dir=self.output_edit.text(),
        )

    def _dialog_title(self, icon: QMessageBox.Icon) -> str:
        """Return a consistent title for message boxes."""
        if icon == QMessageBox.Icon.Critical:
            return self.tr("Error!")
        if icon == QMessageBox.Icon.Warning:
            return self.tr("Warning!")
        return self.tr("Info!")

    def _show_message_box(
        self,
        icon: QMessageBox.Icon,
        message: str,
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
    ) -> QMessageBox.StandardButton:
        """Show a modal message box with consistent styling."""
        msg_box = QMessageBox(icon, self._dialog_title(icon), message, buttons, self)
        return msg_box.exec()

    def about(self):
        """Show About dialog."""
        about_dlg = AboutVMDialog(parent=self)
        about_dlg.exec()

    def changelog(self):
        """Show the changelog dialog."""
        changelog_dlg = ChangelogDialog(parent=self)
        changelog_dlg.exec()

    def ffmpeg_doc(self):
        """Open ffmpeg documentation page."""
        self._open_url(url="https://ffmpeg.org/documentation.html")

    def videomorph_web(self):
        """Open VideoMorph Web page."""
        self._open_url(url="https://videomorph-dev.github.io/videomorph/")

    @staticmethod
    def _open_url(url):
        """Open URL."""
        launcher = launcher_factory()
        launcher.open_with_user_browser(url=url)

    def show_video_info(self):
        """Show video info on the Info Panel."""
        position = self.tasks_table.currentRow()
        info_dlg = InfoDialog(parent=self, position=position, manager=self.manager)
        info_dlg.show()

    def notify(self):
        """Notify when conversion finished."""
        sound_path = path_manager.resource_path("sounds", "successful.wav")
        if sound_path.exists():
            launcher = launcher_factory()
            launcher.sound_notify(str(sound_path))

    @staticmethod
    def help_content():
        """Open VideoMorph documentation manual."""
        # Check if manual exists in system paths first
        manual = path_manager.manual_path(LOCALE)
        if manual and manual.exists():
            url = manual.as_uri()
        else:
            url = "https://videomorph-dev.github.io/videomorph/"

        launcher = launcher_factory()
        launcher.open_with_user_browser(url=url)

    @staticmethod
    def shutdown_machine():
        """Shutdown machine when conversion is finished."""
        launcher = launcher_factory()
        QApplication.instance().closeAllWindows()
        launcher.shutdown_machine()

    def populate_profiles_combo(self):
        """Populate profiles combobox."""
        # Clear combobox content
        self.profiles_combo.clear()
        # Populate the combobox with new data

        profile_names = self.manager.get_profile_qualities().keys()
        for i, profile_name in enumerate(profile_names):
            self.profiles_combo.addItem(profile_name)
            icon = QIcon(":/formats/{0}.png".format(profile_name))
            self.profiles_combo.setItemIcon(i, icon)

    def populate_quality_combo(self, combo):
        """Populate target quality combobox.

        Args:
            combo (QComboBox): List all available presets
        """
        current_profile = self.profiles_combo.currentText()
        if current_profile != "":
            combo.clear()
            combo.addItems(self.manager.get_profile_qualities()[current_profile])

            if self.tasks_table.rowCount():
                self._update_media_files_status()
            self.manager.update_profile(new_quality=self.quality_combo.currentText())

    def output_directory(self):
        """Choose output directory."""
        directory = self._select_directory(
            dialog_title=self.tr("Choose Output Folder"),
            source_dir=self.output_edit.text(),
        )

        if directory:
            self.output_edit.setText(directory)
            self.manager.output_dir = directory
            self._on_modify_conversion_option()

    def closeEvent(self, event):
        """Things to do on close."""
        # Close communication and kill the encoding process
        if self.manager.is_running:
            # ask for confirmation
            user_answer = self._show_message_box(
                QMessageBox.Icon.Warning,
                self.tr(
                    "There are ongoing conversion tasks. Are you sure you want to exit?"
                ),
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if user_answer == QMessageBox.StandardButton.Yes:
                self.manager.kill_converter()
                if not self.manager.delete_running_file_output(
                    tagged=self.tag_chb.isChecked()
                ):
                    output_path = self.manager.get_task_output_path(
                        position=self.manager.current_task_position,
                        tagged=self.tag_chb.isChecked(),
                    )
                    self._show_message_box(
                        QMessageBox.Icon.Warning,
                        self.tr(
                            "Could not delete the output file:\n{0}\n\n"
                            "The file may be in use by another application."
                        ).format(output_path),
                    )
                # Save settings
                self._write_app_settings()
                QCoreApplication.exit(0)
            else:
                event.ignore()
        else:
            # Save settings
            self._write_app_settings()
            QCoreApplication.exit(0)

    def add_task(self, video_path):
        """Add a conversion task to the list."""
        if self.manager.add_task(video_path):
            self._update_task_list()

    def _update_task_list(self):
        """Update the list of conversion tasks."""
        row = self.tasks_table.rowCount()
        self.tasks_table.setRowCount(row + 1)
        self._insert_table_item(
            text=self.manager.get_task_file_name(position=row, with_extension=True),
            row=row,
            column=COLUMNS.NAME,
        )

        item_text = write_time(
            self.manager.get_task_file_info(position=row, info_param="duration")
        )

        self._insert_table_item(item_text, row=row, column=COLUMNS.DURATION)

        self._insert_table_item(
            text=str(self.quality_combo.currentText()),
            row=row,
            column=COLUMNS.QUALITY,
        )

        self._insert_table_item(
            text=self.tr("To Convert"), row=row, column=COLUMNS.PROGRESS
        )

    def _insert_table_item(self, text, row, column):
        item = QTableWidgetItem()
        item.setText(text)
        if column == COLUMNS.NAME:
            item.setIcon(QIcon(":/icons/video-in-list.png"))
        self.tasks_table.setItem(row, column, item)

    def add_tasks(self, *files):
        """Add video files to conversion list.

        Args:
            files (list): List of video file paths
        """
        max_value = len(files)
        progress_dlg = self._create_progress_dialog()
        progress_dlg.setMaximum(max_value)

        for i, file in enumerate(files):
            progress_dlg.setLabelText(self.tr("Adding Video: ") + file)
            progress_dlg.setValue(i)
            QApplication.processEvents()  # Keep UI responsive during I/O

            if progress_dlg.wasCanceled():
                break

            self.add_task(file)
            QApplication.processEvents()  # Process events after each file

        progress_dlg.setValue(max_value)
        progress_dlg.close()

        if self.manager.not_added_files:
            msg = (
                self.tr("Invalid Video Information for:")
                + " \n - "
                + "\n - ".join(self.manager.not_added_files)
                + "\n"
                + self.tr("Video not Added to the List of Conversion Tasks")
            )
            self._show_message_box(QMessageBox.Icon.Critical, msg)

            if not self.manager.task_count:
                self.set_ui_state(AppState.EMPTY)
            else:
                self.set_ui_state(AppState.READY)

        # Update tool buttons so you can convert, or add_file, or clear...
        # only if there is not a conversion process running
        if self.manager.is_running:
            self.set_ui_state(AppState.RUNNING)
        else:
            # Update the files status
            self._set_media_status()
            # Update ui
            self.set_ui_state(AppState.READY)

        # After adding files to the list, recalculate the list duration
        self.task_list_duration = self.manager.get_total_duration(step=0)

    def play_video(self):
        """Play a video using an available video player."""
        row = self.tasks_table.currentIndex().row()
        video_path = self.manager.get_task_file_path(row)
        self._play_media_file(file_path=video_path)
        self._update_ui_when_playing(row)

    def _get_output_path(self, row):
        path = self.manager.get_task_output_path(
            position=row, tagged=self.tag_chb.isChecked()
        )
        return path

    def _play_media_file(self, file_path):
        """Play a video using an available video player."""
        try:
            self.manager.run_player(file_path=file_path)
        except FileNotFoundError:
            self._show_message_box(
                QMessageBox.Icon.Critical,
                self.tr("No video player was found on this system."),
            )

    def open_media_files(self):
        """Add media files to the list of conversion tasks."""
        files_paths = self._load_files(source_dir=self.source_dir)
        # If no file is selected then return
        if files_paths is None:
            return

        self.add_tasks(*files_paths)

    def _load_files(self, source_dir=QDir.homePath()):
        """Load video files."""
        # Use custom dialog with cleaner filter display
        files_paths = self._select_files(
            dialog_title=self.tr("Select Videos"),
            source_dir=source_dir,
        )

        return files_paths

    def open_media_dir(self):
        """Add media files from a directory recursively."""
        directory = self._select_directory(
            dialog_title=self.tr("Select a Folder"), source_dir=self.source_dir
        )

        if not directory:
            return

        try:
            media_files = search_directory_recursively(directory)
            self.source_dir = directory
            self.add_tasks(*media_files)
        except FileNotFoundError:
            self._show_message_box(
                QMessageBox.Icon.Critical,
                self.tr("No videos were found in: {0}").format(directory),
            )

    def remove_media_file(self):
        """Remove selected media file from the list."""
        current_item = self.tasks_table.currentItem()
        if current_item is None:
            return  # No item selected, nothing to remove

        file_row = current_item.row()

        msg_box = QMessageBox(
            QMessageBox.Icon.Warning,
            self._dialog_title(QMessageBox.Icon.Warning),
            self.tr("Remove the selected video from the list?"),
            QMessageBox.StandardButton.NoButton,
            self,
        )

        yes_button = msg_box.addButton(
            self.tr("&Yes"), QMessageBox.ButtonRole.AcceptRole
        )
        msg_box.addButton(self.tr("&No"), QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()
        if msg_box.clickedButton() == yes_button:
            # Delete file from table
            self.tasks_table.removeRow(file_row)
            # Remove file from self.media_list
            self.manager.remove_task(position=file_row)
            self.manager.current_task_position = None
            self.task_list_duration = self.manager.get_total_duration()

        # If all files are deleted... update the interface
        if not self.tasks_table.rowCount():
            self._reset_options_check_boxes()
            self.set_ui_state(AppState.EMPTY)

    def _remove_completed_task_from_ui(self):
        """Remove the currently finished task from the table and model."""
        current_row = self.manager.current_task_position
        if current_row < 0 or current_row >= self.tasks_table.rowCount():
            return

        self.tasks_table.removeRow(current_row)
        self.manager.remove_task(current_row)
        self.manager.current_task_position = current_row - 1
        self.task_list_duration = self.manager.get_total_duration()

        if not self.tasks_table.rowCount():
            self._reset_options_check_boxes()
            self.set_ui_state(AppState.EMPTY)

    def _select_directory(self, dialog_title, source_dir=QDir.homePath()):
        options = (
            QFileDialog.Option.DontResolveSymlinks
            | QFileDialog.Option.ShowDirsOnly
            | QFileDialog.Option.DontUseNativeDialog  # Fix for macOS crash
        )

        directory = QFileDialog.getExistingDirectory(
            self, dialog_title, source_dir, options=options
        )
        return directory

    def _select_files(
        self,
        dialog_title,
        source_dir=QDir.homePath(),
    ):
        # Validate source_dir
        source_path = Path(source_dir)
        source_directory = str(source_path) if source_path.is_dir() else QDir.homePath()

        # Create a custom file dialog for cleaner appearance
        dialog = QFileDialog(self, dialog_title, source_directory)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)

        # Set up filter with all video extensions but cleaner display
        all_video_filter = f"Video Files ({VIDEO_FILTERS})"
        dialog.setNameFilter(all_video_filter)

        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            files_paths = dialog.selectedFiles()
            if files_paths:
                self.source_dir = str(Path(files_paths[0]).parent)
                return files_paths

        return None

    def clear_media_list(self):
        """Clear the list of media files."""
        # If no file is in the list then return
        if not self.tasks_table.rowCount():
            return

        msg_box = QMessageBox(
            QMessageBox.Icon.Warning,
            self._dialog_title(QMessageBox.Icon.Warning),
            self.tr("Remove all videos from the list?"),
            QMessageBox.StandardButton.NoButton,
            self,
        )

        yes_button = msg_box.addButton(
            self.tr("&Yes"), QMessageBox.ButtonRole.AcceptRole
        )
        msg_box.addButton(self.tr("&No"), QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()
        if msg_box.clickedButton() == yes_button:
            # Delete all files from table
            self.tasks_table.setRowCount(0)
            # Clear the media list
            self.manager.clear_tasks()
            # Update the interface
            self.set_ui_state(AppState.EMPTY)
            # Reset all the options check boxes
            self._reset_options_check_boxes()
            self.task_list_duration = 0.0

    def start_encoding(self):
        """Start the encoding process."""
        self.set_ui_state(AppState.RUNNING)

        options = {
            "target_quality": self.tasks_table.item(
                0,
                COLUMNS.QUALITY,  # We might need to handle per-row quality if supported, but for now it seems global or per-row
            ).text(),  # Wait, quality is per row in the table, but usually set globally from combo.
            # The original code read it from the table item at task_list.position.
            # Since we iterate, we might need to pass a way for manager to get quality per task,
            # or just pass the global one if they are all updated.
            # Original: self.tasks_table.item(self.converter.task_list.position, COLUMNS.QUALITY).text()
            # The manager doesn't know about the table.
            # We should probably update the profile/task with the quality BEFORE starting.
            # But the manager takes options.
            # Let's pass the current combo text as default, but the manager might need to read from task?
            # Actually, TaskList.running_task_conversion_cmd takes target_quality.
            # If we want per-task quality, we should probably update the Task object to store it.
            # For now, let's assume the combo box value is what we want, OR
            # we can update the manager to read from the task if we move quality to Task.
            # BUT, the original code read from the TABLE.
            # Let's stick to the original behavior: The UI controls the quality.
            # We can pass the quality_combo text.
            "target_quality": self.quality_combo.currentText(),
            "tagged": self.tag_chb.isChecked(),
            "subtitle": self.subtitle_chb.isChecked(),
            "replace_source": self.delete_chb.isChecked(),
        }

        self.manager.start(options)

    def stop_file_encoding(self):
        """Stop file encoding process and continue with the list."""
        self.manager.stop()

    def stop_all_files_encoding(self):
        """Stop the conversion process for all the files in list."""
        self.manager.stop_all()

    def _on_task_started(self, position):
        """Handle task started signal."""
        self.set_ui_state(AppState.RUNNING)
        self.tasks_table.item(position, COLUMNS.PROGRESS).setText(
            self.tr("Converting...")
        )

    def _on_task_finished(self, position, status):
        """Handle task finished signal."""
        if status == STATUS.done:
            self.tasks_table.item(position, COLUMNS.PROGRESS).setText(self.tr("Done!"))
            if self.delete_chb.isChecked():
                self._remove_completed_task_from_ui()
        elif status == STATUS.stopped:
            self.tasks_table.item(position, COLUMNS.PROGRESS).setText(
                self.tr("Stopped!")
            )

    def _on_all_finished(self):
        """Handle all tasks finished."""
        if self.shutdown_chb.isChecked() and not self.manager.all_tasks_stopped:
            self.shutdown_machine()
            return

        if self.manager.all_tasks_done:
            self.set_ui_state(AppState.DONE)
            self.notify()
            self._show_message_box(
                QMessageBox.Icon.Information,
                self.tr("Conversion process successfully finished."),
            )
        else:
            self.set_ui_state(AppState.READY)
            if self.manager.all_tasks_stopped:
                self._show_message_box(
                    QMessageBox.Icon.Information,
                    self.tr("Conversion process stopped by the user."),
                )

        self.setWindowTitle(self.title)
        self.statusBar().showMessage(self.tr("Ready"))
        self._reset_options_check_boxes()
        self._reset_progress_bars()

    def _on_conversion_error(self, message):
        """Handle conversion error."""
        self._show_message_box(QMessageBox.Icon.Critical, message)
        self.set_ui_state(AppState.READY)

    def _on_progress_updated(self, op_progress, pr_progress):
        """Handle progress updates."""
        self.operation_pb.setProperty("value", op_progress)
        self.total_pb.setProperty("value", pr_progress)

        if self.manager.current_task_position is not None:
            self.tasks_table.item(self.manager.current_task_position, 3).setText(
                str(op_progress) + "%"
            )

        # Update window title
        running_file_name = self.manager.get_running_file_name(with_extension=True)
        self.setWindowTitle(f"{op_progress}%-[{running_file_name}] - {self.title}")

    def _on_time_updated(self, name, bitrate, remaining, elapsed):
        """Handle time updates for status bar."""
        self.statusBar().showMessage(
            self.tr(
                "Converting: {m}\t\t\t "
                "At: {br}\t\t\t "
                "Operation Remaining Time: {ort}\t\t\t "
                "Total Elapsed Time: {tet}"
            ).format(
                m=name,
                br=bitrate,
                ort=remaining,
                tet=elapsed,
            )
        )

    def _reset_progress_bars(self):
        """Reset the progress bars."""
        self.operation_pb.setProperty("value", 0)
        self.total_pb.setProperty("value", 0)

    def _update_media_files_status(self):
        """Update file status."""
        # Current item
        item = self.tasks_table.currentItem()
        if item is not None:
            # Update target_quality in table
            self.tasks_table.item(item.row(), COLUMNS.QUALITY).setText(
                str(self.quality_combo.currentText())
            )

            # Update table Progress field if file is: Done or Stopped
            self.update_table_progress_column(row=item.row())

            # Update file Done or Stopped status
            self.manager.set_task_status(position=item.row(), status=STATUS.todo)

        else:
            self._update_all_table_rows(
                column=COLUMNS.QUALITY, value=self.quality_combo.currentText()
            )

            self._set_media_status()

        # Update total duration of the new tasks list
        self.task_list_duration = self.manager.get_total_duration()
        # Update the interface
        self.set_ui_state(AppState.READY)

    def _update_all_table_rows(self, column, value):
        rows = self.tasks_table.rowCount()
        if rows:
            for row in range(rows):
                self.tasks_table.item(row, column).setText(str(value))
                self.update_table_progress_column(row)

    def update_table_progress_column(self, row):
        """Update the progress column of conversion task list."""
        self.tasks_table.item(row, COLUMNS.PROGRESS).setText(self.tr("To Convert"))

    def _reset_options_check_boxes(self):
        self.delete_chb.setChecked(False)
        self.tag_chb.setChecked(False)
        self.subtitle_chb.setChecked(False)
        self.subtitle_chb.setChecked(False)
        self.shutdown_chb.setChecked(False)  # Reset shutdown option for safety

    def _set_media_status(self):
        """Update media files state of conversion."""

    def _set_media_status(self):
        """Update media files state of conversion."""
        self.manager.reset_all_tasks_status()

    def _on_modify_conversion_option(self):
        if self.manager.task_count:
            self.set_ui_state(AppState.READY)
            self._set_media_status()
            self._update_all_table_rows(
                column=COLUMNS.PROGRESS, value=self.tr("To Convert")
            )
            self.task_list_duration = self.manager.get_total_duration()

    def _on_delete_checkbox_clicked(self):
        """Handle delete checkbox clicks with safety confirmation."""
        if self.delete_chb.isChecked():
            # Show a warning dialog when user tries to enable file deletion
            msg_box = QMessageBox(
                QMessageBox.Icon.Warning,
                self._dialog_title(QMessageBox.Icon.Warning),
                self.tr(
                    "This will PERMANENTLY DELETE the original video files "
                    "after conversion! This action CANNOT be undone.\n\n"
                    "Are you absolutely sure you want to enable this option?"
                ),
                QMessageBox.StandardButton.NoButton,
                self,
            )

            msg_box.addButton(
                self.tr("&Yes, Delete Original Files"),
                QMessageBox.ButtonRole.AcceptRole,
            )
            msg_box.addButton(
                self.tr("&No, Keep Original Files"),
                QMessageBox.ButtonRole.RejectRole,
            )

            msg_box.exec()
            clicked_button = msg_box.clickedButton()
            if clicked_button is None:
                self.delete_chb.setChecked(False)
                return

            button_role = msg_box.buttonRole(clicked_button)

            # If user chooses No (or closes), uncheck the box
            if button_role != QMessageBox.ButtonRole.AcceptRole:
                self.delete_chb.setChecked(False)
                return

        # If we get here, either unchecking or user confirmed deletion
        self._on_modify_conversion_option()

    def set_ui_state(self, state: AppState):
        """Update the interface status based on the application state.

        Args:
            state (AppState): The current state of the application.
        """
        config = UI_STATE_CONFIG[state]

        self.open_media_file_action.setEnabled(config["add"])
        self.convert_action.setEnabled(config["convert"])
        self.clear_media_list_action.setEnabled(config["clear"])
        self.remove_media_file_action.setEnabled(config["remove"])
        self.stop_action.setEnabled(config["stop"])
        self.stop_all_action.setEnabled(config["stop_all"])
        self.quality_combo.setEnabled(config["presets"])
        self.profiles_combo.setEnabled(config["profiles"])
        self.output_btn.setEnabled(config["output_dir"])
        self.subtitle_chb.setEnabled(config["subtitles_chb"])
        self.delete_chb.setEnabled(config["delete_chb"])
        self.tag_chb.setEnabled(config["tag_chb"])
        self.shutdown_chb.setEnabled(config["shutdown_chb"])
        self.play_input_media_file_action.setEnabled(config["play_input"])
        self.play_output_media_file_action.setEnabled(config["play_output"])
        self.info_action.setEnabled(config["info"])

    def _update_ui_when_playing(self, row):
        if self.manager.is_running:
            self.set_ui_state(AppState.RUNNING)
        elif self.manager.get_task_status(row) == STATUS.todo:
            self.set_ui_state(AppState.READY)
        else:
            self.set_ui_state(AppState.STOPPED)

    def _update_ui_when_error_on_conversion(self):
        self.manager.reset_progress()
        self.task_list_duration = self.manager.get_total_duration()
        self.manager.current_task_position = None
        self._reset_progress_bars()
        self.setWindowTitle(self.title)
        self._reset_options_check_boxes()
        self.set_ui_state(AppState.READY)

    def _enable_context_menu_action(self):
        if not self.manager.is_running:
            # Only enable if an item is actually selected
            has_selection = self.tasks_table.currentItem() is not None
            self.remove_media_file_action.setEnabled(has_selection)

        self.play_input_media_file_action.setEnabled(True)

        path = self._get_output_path(row=self.tasks_table.currentIndex().row())
        path_exists = Path(path).exists() if path else False
        # Only enable the menu if output file exist and if it not .mp4,
        # cause .mp4 files doesn't run until conversion is finished
        self.play_output_media_file_action.setEnabled(
            path_exists and self.profiles_combo.currentText() != "MP4"
        )
        self.info_action.setEnabled(bool(self.manager.task_count))

    def _on_table_selection_changed(self):
        """Handle table selection changes to update remove action state."""
        # Only enable remove action if an item is selected and conversion is not running
        has_selection = self.tasks_table.currentItem() is not None
        can_remove = has_selection and not self.manager.is_running
        self.remove_media_file_action.setEnabled(can_remove)
