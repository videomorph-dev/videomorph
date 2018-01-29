# -*- coding: utf-8 -*-
#
# File name: about.py
#
#   VideoMorph - A PyQt5 frontend to ffmpeg.
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

"""This module provides a dialog to show app information."""

from os.path import isfile
from os.path import join as join_path

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QDialog,
                             QDialogButtonBox,
                             QTabWidget,
                             QWidget,
                             QVBoxLayout,
                             QHBoxLayout,
                             QTextEdit,
                             QPlainTextEdit,
                             QSizePolicy,
                             QLabel,
                             QSpacerItem)

from videomorph.converter import APP_NAME
from videomorph.converter import BASE_DIR
from videomorph.converter import SYS_PATHS
from videomorph.converter import VERSION


class AboutVMDialog(QDialog):
    """Dialog to show info about VideoMorph."""
    def __init__(self, parent=None):
        """Class initializer."""
        super(AboutVMDialog, self).__init__(parent)
        self.setWindowTitle(self.tr('About VideoMorph'))
        self.resize(500, 404)
        self.horizontal_layout_3 = QHBoxLayout(self)
        self.vertical_layout_4 = QVBoxLayout()
        self.horizontal_layout_2 = QHBoxLayout()
        self.label = QLabel(self)
        self.label.setMinimumSize(QSize(64, 64))
        self.label.setMaximumSize(QSize(64, 64))
        self.label.setText("")
        self.label.setPixmap(QPixmap(':/logo/videomorph.png'))
        self.label.setScaledContents(True)
        self.horizontal_layout_2.addWidget(self.label)
        self.label_2 = QLabel("<p align=\"center\"><span style=\" "
                              "font-size:20pt; font-weight:600;\">{n}</span>"
                              "</p><p align=\"center\"><span style=\" "
                              "font-size:9pt; font-weight:600;\">version {v}"
                              "</span></p>".format(n=APP_NAME, v=VERSION))
        self.label_2.setMinimumSize(QSize(0, 64))
        self.label_2.setMaximumSize(QSize(16777215, 64))
        self.horizontal_layout_2.addWidget(self.label_2)
        self.vertical_layout_4.addLayout(self.horizontal_layout_2)
        self.tab_widget = QTabWidget(self)
        self.tab = QWidget()
        self.vertical_layout_2 = QVBoxLayout(self.tab)
        self.text_edit_3 = QTextEdit(self.tab)
        self.text_edit_3.setReadOnly(True)
        self.vertical_layout_2.addWidget(self.text_edit_3)
        self.tab_widget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.vertical_layout_3 = QVBoxLayout(self.tab_2)
        self.text_edit_2 = QTextEdit(self.tab_2)
        self.text_edit_2.setReadOnly(True)
        self.vertical_layout_3.addWidget(self.text_edit_2)
        self.tab_widget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.vertical_layout = QVBoxLayout(self.tab_3)
        self.plain_text_edit = QPlainTextEdit(self.tab_3)
        self.plain_text_edit.setReadOnly(True)
        self.vertical_layout.addWidget(self.plain_text_edit)
        self.tab_widget.addTab(self.tab_3, "")
        self.vertical_layout_4.addWidget(self.tab_widget)
        self.horizontal_layout = QHBoxLayout()
        spacer_item = QSpacerItem(40,
                                  20,
                                  QSizePolicy.Expanding,
                                  QSizePolicy.Minimum)
        self.horizontal_layout.addItem(spacer_item)
        self.button_box = QDialogButtonBox(self)
        self.button_box.setOrientation(Qt.Horizontal)
        self.button_box.setStandardButtons(QDialogButtonBox.Ok)
        self.button_box.accepted.connect(self.accept)
        self.horizontal_layout.addWidget(self.button_box)
        self.vertical_layout_4.addLayout(self.horizontal_layout)
        self.horizontal_layout_3.addLayout(self.vertical_layout_4)

        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab),
                                   self.tr("Info"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_2),
                                   self.tr("Credits"))
        self.tab_widget.setTabText(self.tab_widget.indexOf(self.tab_3),
                                   self.tr("License"))

        self.text_edit_2.setHtml(self.tr(
            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600;\">Developers:</span></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Ozkar L. Garcell - Project leader & Publisher</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">&lt;ozkar.garcell@gmail.com&gt;</p>\n"
            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Leodanis Pozo Ramos - Main developer & ArtWork</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">&lt;lpozor78@gmail.org&gt;</p>\n"
            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:600;\"><br /></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600;\">Translators:</span></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Ozkar L. Garcell - en_US, es_ES</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Leodanis Pozo Ramos - en_US, es_ES</p>\n"
            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:600;\"><br /></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600;\">Contributors:</span></p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Carlos Parra Zaldivar - Tester</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Maikel Llamaret Heredia - Tester & ArtWork</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Leonel Salazar Videaux - Tester & Publisher</p>\n"
            "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Osmel Cruz - ArtWork</p>\n"
            "<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt; font-weight:600;\"><br /></p></body></html>"
        ))

        self.text_edit_3.setHtml(self.tr(
            "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
            "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
            "p, li { white-space: pre-wrap; }\n"
            "</style></head><body style=\" font-family:\'Sans Serif\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">An easy to use and lightweight video converter</span></p>\n"
            "<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt; font-weight:600;\"><br /></p>\n"
            "<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:11pt; font-weight:600;\">VideoMorph</span><span style=\" font-size:11pt;\"> is a small GUI front-end for </span><a href=\"http://ffmpeg.org/\"><span style=\" font-size:11pt; text-decoration: underline; color:#2980b9;\">ffmpeg</span></a><span style=\" font-size:11pt;\">, based on code from </span><a href=\"https://github.com/senko/python-video-converter\"><span style=\" font-size:11pt; text-decoration: underline; color:#2980b9;\">python-video-converter</span></a><span style=\" font-size:11pt;\"> and presets idea from </span><a href=\"http://qwinff.github.io/\"><span style=\" font-size:11pt; text-decoration: underline; color:#2980b9;\">QWinFF</span></a><span style=\" font-size:11pt;\">.</span></p>\n"
            "<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:11pt;\"><br /></p>\n"
            "<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><a href=\"https://github.com/videomorph-dev/videomorph\"><span style=\" text-decoration: underline; color:#2980b9;\">https://github.com/videomorph-dev/videomorph</span></a></p></body></html>"
        ))

        self.plain_text_edit.setPlainText(self.get_license_text())

    def get_license_text(self):
        """Get the license text from the license file."""
        doc_license = join_path(SYS_PATHS.doc, 'LICENSE')
        basedir_license = join_path(BASE_DIR, 'LICENSE')
        deb_license = '/usr/share/common-licenses/Apache-2.0'
        if isfile(doc_license):
            license_path = doc_license
        elif isfile(basedir_license):
            license_path = basedir_license
        elif isfile(deb_license):
            license_path = deb_license
        else:
            return (self.tr('See License at:') + '\n\n' +
                    'http://www.apache.org/licenses/LICENSE-2.0')

        with open(license_path, 'r', encoding='UTF-8') as lic:
            return ''.join(lic.readlines())
