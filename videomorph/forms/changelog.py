# -*- coding: utf-8 -*-
#
# File name: changelog.py
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

"""This module provides a dialog to show changelog."""

import gzip
import re
from os.path import exists
from os.path import join as join_path

from PyQt5 import QtCore, QtGui, QtWidgets

from videomorph.converter import APP_NAME, BASE_DIR, SYS_PATHS, VERSION


class ChangelogDialog(QtWidgets.QDialog):
    """Changelog Dialog."""

    def __init__(self, parent=None):
        super(ChangelogDialog, self).__init__(parent)

        self.resize(800, 600)
        self.setWindowTitle(
            APP_NAME + " " + VERSION + " " + self.tr("Changelog")
        )
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum
        )
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
            "cursor", QtGui.QCursor(QtCore.Qt.PointingHandCursor)
        )
        self.text_edit.setReadOnly(True)
        self.horizontal_layout.addWidget(self.text_edit)
        self.text_edit.setAlignment(QtCore.Qt.AlignJustify)

        self._generate_changelog()

    def _generate_changelog(self):
        """Return a human readable changelog."""
        changelog_path = join_path(SYS_PATHS["doc"], "changelog.gz")
        if exists(changelog_path):
            changelog_file = changelog_path
        else:
            changelog_file = join_path(BASE_DIR, "changelog.gz")

        line_start_pattern = re.compile(r"\s+\*\s+")

        with gzip.open(changelog_file, "rt", encoding="utf-8") as changelog:
            changes = []
            for line in changelog:
                start = line_start_pattern.match(line)
                if start:
                    line = line.strip("\n" + start.group())
                    if "Release" in line:
                        version = "<b>{0}</b>".format(line)
                        changes.append(version)
                        changes.extend(["<ul>", "</ul>"])
                    else:
                        line = "<li>{0}</li>".format(line)
                        changes.insert(-1, line)

        self.text_edit.setHtml("".join(changes))
