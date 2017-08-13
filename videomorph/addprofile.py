# -*- coding: utf-8 -*-
#
# File name: addprofiles.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg and avconv.
#   Copyright 2015-2016 VideoMorph Development Team

#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at

#       http://www.apache.org/licenses/LICENSE-2.0

#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""This module provides the dialog for VideoMorph profiles."""

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QDialog, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QSpacerItem, QDialogButtonBox,
                             QMessageBox)

from .converter import (ProfileBlankNameError,
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
        self.label.setText(self.tr("Pr&ofile Name (e.g. MP4)"))
        self.vertical_layout.addWidget(self.label)

        self.le_profile_name = QLineEdit(self.layout_widget)
        self.vertical_layout.addWidget(self.le_profile_name)

        self.vertical_layout_4.addLayout(self.vertical_layout)

        self.vertical_layout_2 = QVBoxLayout()

        self.label_2 = QLabel(self.layout_widget)
        self.label_2.setText(self.tr(
            "&Target Quality Name (e.g. MP4 Widescreen (16:9))"))
        self.vertical_layout_2.addWidget(self.label_2)

        self.le_preset_name = QLineEdit(self.layout_widget)
        self.vertical_layout_2.addWidget(self.le_preset_name)

        self.vertical_layout_4.addLayout(self.vertical_layout_2)

        self.vertical_layout_3 = QVBoxLayout()

        self.label_3 = QLabel(self.layout_widget)
        self.label_3.setText(self.tr(
            "&Command Line Parameters for Tarrget Quality"))
        self.vertical_layout_3.addWidget(self.label_3)

        self.le_params = QLineEdit(self.layout_widget)
        self.vertical_layout_3.addWidget(self.le_params)

        self.vertical_layout_4.addLayout(self.vertical_layout_3)

        self.vertical_layout_5 = QVBoxLayout()

        self.label_4 = QLabel(self.layout_widget)
        self.label_4.setText(self.tr(
            "Output File &Extension (e.g. .mp4)"))
        self.vertical_layout_5.addWidget(self.label_4)

        self.le_extension = QLineEdit(self.layout_widget)
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
            self.parent.conversion_profile.add_xml_profile(
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
            self.parent.xml_profile.set_xml_root()
            self.parent.populate_profiles_combo()
            QDialog.accept(self)
