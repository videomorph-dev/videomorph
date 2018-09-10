# -*- coding: utf-8 -*-
#
# File name: vmwidgets.py
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

"""This module provides customized widgets for VideoMorph."""

from functools import partial
from urllib.request import url2pathname

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QItemDelegate
from PyQt5.QtWidgets import QComboBox

from videomorph.converter import STATUS
from videomorph.converter import VALID_VIDEO_EXT
from . import COLUMNS


class TasksListTable(QTableWidget):
    """Customized class to provide Tasks List Table."""

    def __init__(self, parent, window):
        """Class initializer."""
        super(TasksListTable, self).__init__(parent)
        self._window = window

        self.setColumnCount(4)
        self.setRowCount(0)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.setHorizontalHeaderLabels(
            [self.tr('File Name'),
             self.tr('Duration'),
             self.tr('Target Quality'),
             self.tr('Progress')])
        tasks_text = self.tr('List of Conversion Tasks')
        self.setStatusTip(tasks_text)
        self.setToolTip(tasks_text)

        # Create a combo box for Target update
        self.setItemDelegate(TargetQualityDelegate(parent=self._window))

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        """Drag Enter Event."""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Drag Move Event."""
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Drop Event."""
        files = []

        for url in event.mimeData().urls():
            extension = '.{0}'.format(url.path().split('.')[-1]).lower()
            if extension in VALID_VIDEO_EXT:
                file_path = url2pathname(url.path())
                files.append(file_path)

        if files:
            self._window.add_media_files(*files)
            event.accept()
        else:
            event.ignore()


class TargetQualityDelegate(QItemDelegate):
    """Combobox to select the target quality from the task list."""

    def __init__(self, parent=None):
        """Class initializer."""
        super(TargetQualityDelegate, self).__init__(parent)
        self.parent = parent

    def createEditor(self, parent, option, index):
        """Create a ComboBox to edit the Target Quality."""
        if index.column() == COLUMNS.QUALITY:
            editor = QComboBox(parent)
            self.parent.populate_quality_combo(combo=editor)
            editor.activated.connect(partial(self.update,
                                             editor,
                                             index))
            return editor

        return QItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        """Set Target Quality."""
        text = index.model().data(index, Qt.DisplayRole)
        if index.column() == COLUMNS.QUALITY:
            i = editor.findText(text)
            if i == -1:
                i = 0
            editor.setCurrentIndex(i)
        else:
            QItemDelegate.setEditorData(self, editor, index)

        self.parent.tb_tasks.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def update(self, editor, index):
        """Update several things in the interface."""
        self.parent.update_table_progress_column(row=index.row())
        self.parent.media_list.set_file_status(position=index.row(),
                                               status=STATUS.todo)
        self.parent.total_duration = self.parent.media_list.duration
        self.parent.update_ui_when_ready()
        self.parent.tb_tasks.setEditTriggers(QAbstractItemView.NoEditTriggers)
