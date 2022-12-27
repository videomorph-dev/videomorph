# -*- coding: utf-8 -*-
#
# File name: addprofile.py
#
#   VideoMorph - A PyQt6 frontend to ffmpeg.
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

"""This module provides the dialog for VideoMorph customized profiles."""

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtWidgets import (QDialog, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QSpacerItem, QDialogButtonBox,
                             QMessageBox, QCompleter)

from videomorph.converter import LOCALE
from videomorph.converter import VALID_VIDEO_EXT
from videomorph.converter.profile import (ProfileBlankNameError,
                                          ProfileBlankPresetError,
                                          ProfileBlankParamsError,
                                          ProfileExtensionError)


class AddProfileDialog(QDialog):
    """Dialog for adding customized video conversion profiles."""

    def __init__(self, parent=None):
        super(AddProfileDialog, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle(self.tr("Add Customized Profile"))
        self.resize(399, 295)

        self.layout_widget = QWidget(self)
        self.layout_widget.setGeometry(QtCore.QRect(20, 20, 361, 257))

        self.vertical_layout_4 = QVBoxLayout(self.layout_widget)

        self.vertical_layout = QVBoxLayout()

        self.label = QLabel(self.layout_widget)
        self.label.setText(self.tr('Pr&ofile Name:'))
        self.vertical_layout.addWidget(self.label)

        self.le_profile_name = QLineEdit(self.layout_widget)
        self.le_profile_name.setPlaceholderText(self.tr('(e.g. MP4)'))
        profile_name_model = QCompleter(
            self.parent.profile.get_xml_profile_qualities(LOCALE).keys())
        profile_name_model.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.le_profile_name.setCompleter(profile_name_model)
        self.vertical_layout.addWidget(self.le_profile_name)

        self.vertical_layout_4.addLayout(self.vertical_layout)

        self.vertical_layout_2 = QVBoxLayout()

        self.label_2 = QLabel(self.layout_widget)
        self.label_2.setText(self.tr(
            "&Target Quality Name:"))
        self.vertical_layout_2.addWidget(self.label_2)

        self.le_preset_name = QLineEdit(self.layout_widget)
        self.le_preset_name.setPlaceholderText(
            self.tr('(e.g. MP4 Widescreen (16:9))'))
        self.vertical_layout_2.addWidget(self.le_preset_name)

        self.vertical_layout_4.addLayout(self.vertical_layout_2)

        self.vertical_layout_3 = QVBoxLayout()

        self.label_3 = QLabel(self.layout_widget)
        self.label_3.setText(self.tr(
            "&Command Line Parameters for Target Quality:"))
        self.vertical_layout_3.addWidget(self.label_3)

        self.le_params = QLineEdit(self.layout_widget)
        self.vertical_layout_3.addWidget(self.le_params)

        self.vertical_layout_4.addLayout(self.vertical_layout_3)

        self.vertical_layout_5 = QVBoxLayout()

        self.label_4 = QLabel(self.layout_widget)
        self.label_4.setText(self.tr(
            "Output File &Extension:"))
        self.vertical_layout_5.addWidget(self.label_4)

        self.le_extension = QLineEdit(self.layout_widget)
        self.le_extension.setPlaceholderText(self.tr('(e.g. .mp4)'))
        extensions_model = QCompleter(VALID_VIDEO_EXT)
        extensions_model.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.le_extension.setCompleter(extensions_model)
        self.vertical_layout_5.addWidget(self.le_extension)

        self.vertical_layout_4.addLayout(self.vertical_layout_5)

        spacer_item = QSpacerItem(20, 48,
                                  QtWidgets.QSizePolicy.Minimum,
                                  QtWidgets.QSizePolicy.Expanding)
        self.vertical_layout_4.addItem(spacer_item)

        self.button_box = QDialogButtonBox(self.layout_widget)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.vertical_layout_4.addWidget(self.button_box)

        self.label.setBuddy(self.le_profile_name)
        self.label_2.setBuddy(self.le_preset_name)
        self.label_3.setBuddy(self.le_params)
        self.label_4.setBuddy(self.le_extension)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        QtCore.QMetaObject.connectSlotsByName(self)

    def accept(self):
        """Accept the dialog result."""
        try:
            self.parent.profile.add_xml_profile(
                profile_name=self.le_profile_name.text(),
                preset=self.le_preset_name.text(),
                params=self.le_params.text(),
                extension=self.le_extension.text()
            )
        except ProfileBlankNameError:
            QMessageBox.critical(
                self, self.tr('Error!'),
                self.tr("Profile Name can't be Left Blank")
            )
            self.le_profile_name.setFocus()
        except ProfileBlankPresetError:
            QMessageBox.critical(
                self, self.tr('Error!'),
                self.tr("Target Quality Name can't be Left Blank")
            )
            self.le_preset_name.setFocus()
        except ProfileBlankParamsError:
            QMessageBox.critical(
                self, self.tr('Error!'),
                self.tr("Command Line Parameters can't be Left Blank")
            )
            self.le_params.setFocus()
        except ProfileExtensionError:
            QMessageBox.critical(
                self, self.tr('Error!'),
                self.tr("Output File Extension can't be Left Blank, it "
                        "must start with a dot (.) and should be a Valid "
                        "Video Extension")
            )
            self.le_extension.setFocus()
        else:
            self.parent.populate_profiles_combo()
            self.parent.profile.update(
                new_quality=self.parent.cb_quality.currentText())
            QDialog.accept(self)
