# -*- coding: utf-8 -*-
#
# File name: about.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg and avconv.
#   Copyright 2016-2017 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""This module provides a dialog to show changelog."""

from os.path import exists
from os.path import sep

from PyQt5 import QtCore, QtGui, QtWidgets

from videomorph.converter import APP_NAME
from videomorph.converter import BASE_DIR
from videomorph.converter import LINUX_PATHS
from videomorph.converter import VERSION


class ChangelogDialog(QtWidgets.QDialog):
    """Changelog Dialog."""

    def __init__(self, parent=None):
        super(ChangelogDialog, self).__init__(parent)

        self.resize(800, 600)
        self.setWindowTitle(APP_NAME + ' ' + VERSION + ' ' +
                            self.tr('Changelog'))
        size_policy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum,
                                            QtWidgets.QSizePolicy.Minimum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(size_policy)
        self.setMinimumSize(QtCore.QSize(800, 600))
        self.horizontal_layout = QtWidgets.QHBoxLayout(self)
        self.text_edit = QtWidgets.QTextEdit(self)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.text_edit.setFont(font)
        self.text_edit.viewport().setProperty(
            "cursor",
            QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.text_edit.setReadOnly(True)
        self.horizontal_layout.addWidget(self.text_edit)
        self.text_edit.setAlignment(QtCore.Qt.AlignJustify)

        self._generate_changelog()

    def _generate_changelog(self):
        """Return a human readable changelog."""
        if exists(BASE_DIR + '{0}changelog'.format(sep)):
            changelog_file = BASE_DIR + '{0}changelog'.format(sep)
        else:
            changelog_file = (LINUX_PATHS['doc'] + '{0}changelog'.format(sep))

        try:
            with open(changelog_file, 'r', encoding='utf-8') as changelog:
                for i, line in enumerate(changelog):
                    if line.startswith('    * '):
                        if 'Release' in line:
                            line = line.strip('    * ')
                            if i > 2:
                                self.text_edit.append('\n')
                            self.text_edit.append('<b>{0}</b>'.format(line))
                            self.text_edit.append('\n')
                        else:
                            line = line.strip('\n')
                            self.text_edit.append(line)
        except FileNotFoundError:
            pass
