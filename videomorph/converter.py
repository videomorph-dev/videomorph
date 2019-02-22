# -*- coding: utf-8 -*-

# File name: converter.py
#
# Copyright (C) 2019 Leodanis Pozo Ramos <lpozor78@gmail.com>
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

"""This module provides Converter Class."""


# class Converter:
#     """Converter class."""
#
#     def __init__(self):
#         self.media_list_duration = 0.0
#         self.source_dir = Path().home()
#
#         self.conversion_lib = ConversionLib()
#         self.conversion_lib.setup_converter(
#             reader=self._ready_read,
#             finisher=self._finish_file_encoding,
#             process_channel=QProcess.MergedChannels)
#         self.reader = self.conversion_lib.reader
#         self.timer = self.conversion_lib.timer
#         self.profile = ConversionProfile(
#             prober=self.conversion_lib.prober_path)
#
#         self.media_list = MediaList(profile=self.profile)
