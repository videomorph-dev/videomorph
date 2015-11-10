#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   MediaMorph - A PyQt5 frontend to ffmpeg
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


STATUS = [
    'QUEUED',
    'RUNNING',
    'FINISHED',
    'FAILED'
]


class Task(object):

    """ Class doc """

    def __init__(self, number, input_file, output_file, status, parameters):
        """ Class initializer """
        self.number = number
        self.input_file = input_file
        self.output_file = output_file
        self.task_status = status
        self.params = parameters

    def __repr__(self):
        return ('<Tasks id={n}, input={i}, output={o}, status={s}, params={p}>'.format(n=self.number,i=self.input_file, o=self.output_file, s=self.task_status, p=self.params))

    def __str__(self):
        return self.__repr__()
