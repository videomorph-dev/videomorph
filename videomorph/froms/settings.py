# -*- coding: utf-8 -*-
#
# File _name: settings.py
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

"""This module provides a dialog to make some settings."""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog


class SettingsDialog(QDialog):
    """Dialog to define the conversion library to use."""

    def __init__(self, parent=None):
        """Class initializer."""
        super(SettingsDialog, self).__init__(parent)
        self.parent = parent

        self.setWindowTitle(self.tr('Settings'))
        self.setModal(True)
        self.resize(200, 170)

        self.main_layout = QtWidgets.QVBoxLayout()

        self.group_box = QtWidgets.QGroupBox()
        self.group_box.setTitle(self.tr('Conversion Library'))

        self.group_layout = QtWidgets.QVBoxLayout(self.group_box)

        self.radio_btn_ffmpeg = QtWidgets.QRadioButton(self.group_box)
        self.radio_btn_ffmpeg.setText(self.tr('Use Ffmpeg Library'))

        self.radio_btn_avconv = QtWidgets.QRadioButton(self.group_box)
        self.radio_btn_avconv.setText(self.tr('Use Avconv Library'))

        self.group_layout.addWidget(self.radio_btn_ffmpeg)
        self.group_layout.addWidget(self.radio_btn_avconv)

        self.main_layout.addWidget(self.group_box)

        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel |
                                           QtWidgets.QDialogButtonBox.Ok)

        self.main_layout.addWidget(self.button_box)
        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.accept)
        self.setLayout(self.main_layout)
