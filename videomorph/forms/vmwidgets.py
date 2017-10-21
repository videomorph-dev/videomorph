# -*- coding: utf-8 -*-

# File name: vmwidgets.py
#
# Copyright (C) 2017 Leodanis Pozo Ramos <lpozor78@gmail.com>
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

"""This module provides customized widgets for VideoMorph."""

from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QItemDelegate
from PyQt5.QtWidgets import QComboBox

from . import COLUMNS
from videomorph.converter import STATUS
from videomorph.converter import VALID_VIDEO_EXT


class TasksListTable(QTableWidget):
    """Customized class to provide Tasks List Table."""

    def __init__(self, parent, window):
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
        if event.mimeData().hasFormat('text/plain'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasFormat('text/plain'):
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        files = []

        for url in event.mimeData().urls():
            extension = '.{0}'.format(url.path().split('.')[-1])
            if extension in VALID_VIDEO_EXT:
                files.append(url.path())

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
        else:
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
        # Update table Progress field if file is: Done or Stopped
        self.parent.update_table_progress_column(row=index.row())

        # Update file status
        self.parent.media_list.set_file_status(position=index.row(),
                                               status=STATUS.todo)
        # Update total duration of the new tasks list
        self.parent.total_duration = self.parent.media_list.duration

        # Update the interface
        self.parent.update_interface(clear=False,
                                     stop=False,
                                     stop_all=False,
                                     remove=False,
                                     play_input=False,
                                     play_output=False)

        self.parent.tb_tasks.setEditTriggers(QAbstractItemView.NoEditTriggers)
