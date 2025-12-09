"""This module provides customized widgets for VideoMorph."""

from functools import partial
from typing import Any, List, Optional
from urllib.request import url2pathname

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHeaderView,
    QItemDelegate,
    QTableWidget,
)

from videomorph.converter.constants import STATUS, VALID_VIDEO_EXT
from videomorph.forms import COLUMNS
from videomorph.forms.ui_state import AppState


class TasksListTable(QTableWidget):
    """Customized class to provide Tasks List Table."""

    def __init__(self, parent: Optional[Any], window: Any) -> None:
        """Class initializer."""
        super(TasksListTable, self).__init__(parent)
        self._window = window

        self.setColumnCount(4)
        self.setRowCount(0)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        if (header := self.horizontalHeader()) is not None:
            header.setSectionResizeMode(COLUMNS.NAME, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(COLUMNS.DURATION, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(COLUMNS.QUALITY, QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(COLUMNS.PROGRESS, QHeaderView.ResizeMode.ResizeToContents)
        self.setHorizontalHeaderLabels(
            [
                self.tr("Video Name"),
                self.tr("Duration"),
                self.tr("Target Quality"),
                self.tr("Progress"),
            ]
        )
        tasks_text = self.tr("List of Conversion Tasks")
        self.setStatusTip(tasks_text)
        self.setToolTip(tasks_text)

        # Create a combo box for Target update
        self.setItemDelegate(TargetQualityDelegate(parent=self._window))

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: Any) -> None:
        """Drag Enter Event."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event: Any) -> None:
        """Drag Move Event."""
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.DropAction.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: Any) -> None:
        """Drop Event."""
        files: List[str] = []

        for url in event.mimeData().urls():
            extension = ".{0}".format(url.path().split(".")[-1]).lower()
            if extension in VALID_VIDEO_EXT:
                file_path = url2pathname(url.path())
                files.append(file_path)

        if files:
            self._window.add_tasks(*files)
            event.accept()
        else:
            event.ignore()


class TargetQualityDelegate(QItemDelegate):
    """Combobox to select the target quality from the task list."""

    def __init__(self, parent: Optional[Any] = None) -> None:
        """Class initializer."""
        super(TargetQualityDelegate, self).__init__(parent)
        self.parent = parent

    def createEditor(self, parent: Any, option: Any, index: Any) -> Optional[Any]:
        """Create a ComboBox to edit the Target Quality."""
        if index.column() == COLUMNS.QUALITY:
            editor = QComboBox(parent)
            self.parent.populate_quality_combo(combo=editor)
            editor.activated.connect(partial(self.update, editor, index))
            return editor

        return QItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor: Any, index: Any) -> None:
        """Set Target Quality."""
        text = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        if index.column() == COLUMNS.QUALITY:
            i = editor.findText(text)
            if i == -1:
                i = 0
            editor.setCurrentIndex(i)
        else:
            QItemDelegate.setEditorData(self, editor, index)

        self.parent.tasks_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

    def update(self, editor: Any, index: Any) -> None:
        """Update several things in the interface."""
        self.parent.update_table_progress_column(row=index.row())
        self.parent.manager.set_task_status(position=index.row(), status=STATUS.todo)
        self.parent.task_list_duration = self.parent.manager.get_total_duration()
        self.parent.set_ui_state(AppState.READY)
        self.parent.tasks_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
