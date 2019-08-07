# -*- coding: utf-8 -*-
#
# File name: info.py
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

from os.path import basename

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QGroupBox,
                             QGridLayout, QSpacerItem)

from videomorph.converter.utils import write_size
from videomorph.converter.utils import write_time


class InfoDialog(QtWidgets.QDialog):
    """Changelog Dialog."""

    def __init__(self, parent=None, position=0, task_list=None):
        super(InfoDialog, self).__init__(parent)
        self.position = position
        self.task_list = task_list

        self.central_widget = QtWidgets.QWidget(self)
        self.resize(300, 400)
        self.setWindowTitle(self.tr('Properties'))

        whole_layout = QVBoxLayout(self.central_widget)

        gb_general = QGroupBox(self.central_widget)
        gb_general.setTitle(self.tr('General'))

        general_layout = QVBoxLayout(gb_general)

        general_grid = QGridLayout()
        general_grid.setColumnStretch(1, 1)

        label_file_name = QLabel(gb_general)
        label_file_name.setText(self.tr('File Name:'))

        self.label_file_name_value = QLabel(gb_general)
        self.label_file_name_value.setText("")

        label_size = QLabel(gb_general)
        label_size.setText(self.tr('Size:'))

        self.label_size_value = QLabel(gb_general)
        self.label_size_value.setText("")

        label_duration = QLabel(gb_general)
        label_duration.setText(self.tr('Duration:'))

        self.label_duration_value = QLabel(gb_general)
        self.label_duration_value.setText("")

        label_format_name = QLabel(gb_general)
        label_format_name.setText(self.tr('Format Name:'))

        self.label_format_name_value = QLabel(gb_general)
        self.label_format_name_value.setText("")

        label_format_long_name = QLabel(gb_general)
        label_format_long_name.setText(self.tr('Format Long Name:'))

        self.label_format_long_name_value = QLabel(gb_general)
        self.label_format_long_name_value.setText("")

        general_grid.addWidget(label_file_name, 0, 0, 1, 1)
        general_grid.addWidget(self.label_file_name_value, 0, 1, 1, 1)
        general_grid.addWidget(label_size, 1, 0, 1, 1)
        general_grid.addWidget(self.label_size_value, 1, 1, 1, 1)
        general_grid.addWidget(label_duration, 2, 0, 1, 1)
        general_grid.addWidget(self.label_duration_value, 2, 1, 1, 1)
        general_grid.addWidget(label_format_name, 3, 0, 1, 1)
        general_grid.addWidget(self.label_format_name_value, 3, 1, 1, 1)
        general_grid.addWidget(label_format_long_name, 4, 0, 1, 1)
        general_grid.addWidget(self.label_format_long_name_value, 4, 1, 1, 1)

        general_layout.addLayout(general_grid)

        gb_video = QGroupBox(self.central_widget)
        gb_video.setTitle(self.tr('Video'))
        video_layout = QVBoxLayout(gb_video)
        video_grid = QGridLayout()
        video_grid.setColumnStretch(1, 1)

        label_bit_rate = QLabel(gb_video)
        label_bit_rate.setText(self.tr('Bit Rate:'))

        self.label_bit_rate_value = QLabel(gb_video)
        self.label_bit_rate_value.setText("")

        label_width = QLabel(gb_video)
        label_width.setText(self.tr('Width:'))

        self.label_width_value = QLabel(gb_video)
        self.label_width_value.setText("")

        label_height = QLabel(gb_video)
        label_height.setText(self.tr('Height:'))

        self.label_height_value = QLabel(gb_video)
        self.label_height_value.setText("")

        label_codec_long_name = QLabel(gb_video)
        label_codec_long_name.setText(self.tr('Codec Long Name:'))

        self.label_codec_long_name_value = QLabel(gb_video)
        self.label_codec_long_name_value.setText("")

        label_codec_name = QLabel(gb_video)
        label_codec_name.setText(self.tr('Codec Name:'))

        self.label_codec_name_value = QLabel(gb_video)
        self.label_codec_name_value.setText("")

        video_grid.addWidget(label_bit_rate, 2, 0, 1, 1)
        video_grid.addWidget(self.label_bit_rate_value, 2, 1, 1, 1)
        video_grid.addWidget(label_width, 3, 0, 1, 1)
        video_grid.addWidget(self.label_width_value, 3, 1, 1, 1)
        video_grid.addWidget(label_height, 4, 0, 1, 1)
        video_grid.addWidget(self.label_height_value, 4, 1, 1, 1)
        video_grid.addWidget(label_codec_long_name, 1, 0, 1, 1)
        video_grid.addWidget(self.label_codec_long_name_value, 1, 1, 1, 1)
        video_grid.addWidget(label_codec_name, 0, 0, 1, 1)
        video_grid.addWidget(self.label_codec_name_value, 0, 1, 1, 1)

        video_layout.addLayout(video_grid)

        gb_audio = QGroupBox(self.central_widget)
        gb_audio.setTitle(self.tr('Audio'))

        audio_layout = QVBoxLayout(gb_audio)

        audio_grid = QGridLayout()
        audio_grid.setColumnStretch(1, 1)

        label_acodec_name = QLabel(gb_audio)
        label_acodec_name.setText(self.tr('Codec Name:'))

        self.label_acodec_name_value = QLabel(gb_audio)
        self.label_acodec_name_value.setText("")

        label_acodec_long_name = QLabel(gb_audio)
        label_acodec_long_name.setText(self.tr('Codec Long Name:'))

        self.label_acodec_long_name_value = QLabel(gb_audio)
        self.label_acodec_long_name_value.setText("")

        audio_grid.addWidget(label_acodec_name, 0, 0, 1, 1)
        audio_grid.addWidget(self.label_acodec_name_value, 0, 1, 1, 1)
        audio_grid.addWidget(label_acodec_long_name, 1, 0, 1, 1)
        audio_grid.addWidget(self.label_acodec_long_name_value, 1, 1, 1, 1)

        audio_layout.addLayout(audio_grid)

        whole_layout.addWidget(gb_general)
        whole_layout.addWidget(gb_video)
        whole_layout.addWidget(gb_audio)

        self.ok_button = QPushButton()
        self.ok_button.setText('OK')
        self.ok_button.clicked.connect(self.close)
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addSpacerItem(
            QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding,
                        QtWidgets.QSizePolicy.Minimum))
        button_layout.addWidget(self.ok_button)
        whole_layout.addLayout(button_layout)
        self._show_video_info(self.position)

        self.setMinimumSize(whole_layout.minimumSize())

    def _show_video_info(self, position):
        """Show video info on the Info Panel."""
        task = self.task_list.get_task(position)
        file_path = task.video.format_info['filename']
        filename = basename(file_path)
        self.label_file_name_value.setText(filename)
        self.label_size_value.setText(
            write_size(task.video.format_info['size']))
        self.label_duration_value.setText(
            write_time(task.video.format_info['duration']))
        self.label_format_name_value.setText(
            task.video.format_info['format_name'])
        self.label_format_long_name_value.setText(
            task.video.format_info['format_long_name'])

        self.label_codec_name_value.setText(
            task.video.video_info['codec_name'])
        self.label_codec_long_name_value.setText(
            task.video.video_info['codec_long_name'])
        self.label_bit_rate_value.setText(
            task.video.video_info['bit_rate'])
        self.label_width_value.setText(task.video.video_info['width'])
        self.label_height_value.setText(task.video.video_info['height'])
        self.label_acodec_name_value.setText(
            task.video.audio_info['codec_name'])
        self.label_acodec_long_name_value.setText(
            task.video.audio_info['codec_long_name'])
