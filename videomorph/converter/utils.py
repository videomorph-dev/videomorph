#!/usr/bin/env python
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


def write_time(_time):
    ## function fix
    #  fixes a number so it always contain two characters
    def fix(string):
        string = str(string)
        if (len(string) == 1):
            return '0'+string
        else:
            return string
    time = int(round(float(_time)))
    hours = int(time / 3600);
    mins = int(time / 60) - hours * 60;
    secs = time - mins * 60 - hours * 3600
    if hours:  ## @return the time in 00h:00m:00s format
        return ':'.join(['{0}h'.format(fix(hours)),
                         '{0}m'.format(fix(mins)),
                         '{0}s'.format(fix(secs))])
    elif mins:  ## @return the time in 00m:00s format
        return ':'.join(['{0}m'.format(fix(mins)),
                         '{0}s'.format(fix(secs))])
    else:  ## @return the time in 0s format
        return secs+'s'
