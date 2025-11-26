"""This module provides a dialog to show changelog."""

import gzip
import re

from PyQt6 import QtCore, QtGui, QtWidgets

from videomorph.converter import APP_NAME, VERSION
from videomorph.converter.vmpath import doc_file


class ChangelogDialog(QtWidgets.QDialog):
    """Changelog Dialog."""

    def __init__(self, parent=None):
        super(ChangelogDialog, self).__init__(parent)

        self.resize(800, 600)
        self.setWindowTitle(APP_NAME + " " + VERSION)
        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
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
            "cursor", QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        )
        self.text_edit.setReadOnly(True)
        self.horizontal_layout.addWidget(self.text_edit)
        self.text_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignJustify)

        self._generate_changelog()

    def _generate_changelog(self):
        """Return a human readable changelog."""
        changelog_file = doc_file("changelog.gz")

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
