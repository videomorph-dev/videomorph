#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File name: profiles.py
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

"""This module contains the PRESETS for encoding different video formats."""

from os import cpu_count
from re import compile
from collections import OrderedDict
from xml.etree import ElementTree

CPU_CORES = (cpu_count() - 1 if
             cpu_count() is not None
             else 0)

PARAMS = OrderedDict([('MP4 High Quality', '-crf 35.0 -vcodec libx264 -acodec aac -ar 48000 -b:a 128k -coder 1 -flags +loop -cmp +chroma -partitions +parti4x4+partp8x8+partb8x8 -me_method hex -subq 6 -me_range 16 -g 250 -keyint_min 25 -sc_threshold 40 -i_qfactor 0.71 -b_strategy 1 -strict -2 -threads {0}'.format(CPU_CORES)),
                      ('MP4 Very High Quality', '-crf 25.0 -vcodec libx264 -acodec aac -ar 48000 -b:a 160k -coder 1 -flags +loop -cmp +chroma -partitions +parti4x4+partp8x8+partb8x8 -me_method hex -subq 6 -me_range 16 -g 250 -keyint_min 25 -sc_threshold 40 -i_qfactor 0.71 -b_strategy 1 -strict -2 -threads {0}'.format(CPU_CORES)),
                      ('MP4 Super High Quality', '-crf 15.0 -vcodec libx264 -acodec aac -ar 48000 -b:a 192k -coder 1 -flags +loop -cmp +chroma -partitions +parti4x4+partp8x8+partb8x8 -me_method hex -subq 6 -me_range 16 -g 250 -keyint_min 25 -sc_threshold 40 -i_qfactor 0.71 -b_strategy 1 -strict -2 -threads {0}'.format(CPU_CORES)),
                      ('MP4 Fullscreen (4:3)', '-f mp4 -r 29.97 -vcodec libx264 -s 640x480 -b:v 1000k -aspect 4:3 -flags +loop -cmp +chroma -deblockalpha 0 -deblockbeta 0 -maxrate 1500k -bufsize 4M -bt 256k -refs 1 -bf 3 -coder 1 -me_method umh -me_range 16 -subq 7 -partitions +parti4x4+parti8x8+partp8x8+partb8x8 -g 250 -keyint_min 25 -level 30 -qmin 10 -qmax 51 -qcomp 0.6 -sc_threshold 40 -i_qfactor 0.71 -acodec aac -b:a 112k -ar 48000 -ac 2 -strict -2 -threads {0}'.format(CPU_CORES)),
                      ('MP4 Widescreen (16:9)', '-f mp4 -r 29.97 -vcodec libx264 -s 704x384 -b:v 1000k -aspect 16:9 -flags +loop -cmp +chroma -maxrate 1500k -bufsize 4M -bt 256k -refs 1 -bf 3 -coder 1 -me_method umh -me_range 16 -subq 7 -partitions +parti4x4+parti8x8+partp8x8+partb8x8 -g 250 -keyint_min 25 -level 30 -qmin 10 -qmax 51 -qcomp 0.6 -trellis 2 -sc_threshold 40 -i_qfactor 0.71 -acodec aac -b:a 112k -ar 48000 -ac 2 -strict -2 -threads {0}'.format(CPU_CORES)),
                      ('DVD Fullscreen (4:3)', '-f dvd -target ntsc-dvd -vcodec mpeg2video -r 29.97 -s 352x480 -aspect 4:3 -b:v 4000k -mbd rd -cmp 2 -subcmp 2 -acodec mp2 -b:a 192k -ar 48000 -ac 2 -threads {0}'.format(CPU_CORES)),
                      ('DVD Widescreen (16:9)', '-f dvd -target ntsc-dvd -vcodec mpeg2video -r 29.97 -s 352x480 -aspect 16:9 -b:v 4000k -mbd rd -cmp 2 -subcmp 2 -acodec mp2 -b:a 192k -ar 48000 -ac 2 -threads {0}'.format(CPU_CORES)),
                      ('DVD Fullscreen (4:3) High Quality', '-f dvd -target ntsc-dvd -r 29.97 -s 720x480 -aspect 4:3 -b:v 8000k -mbd rd -cmp 0 -subcmp 2 -threads {0}'.format(CPU_CORES)),
                      ('DVD Widescreen (16:9) High Quality', '-f dvd -target ntsc-dvd -r 29.97 -s 720x480 -aspect 16:9 -b:v 8000k -g 12 -mbd rd -cmp 0 -subcmp 2 -threads {0}'.format(CPU_CORES)),
                      ('DVD Low Quality', '-f dvd -target ntsc-dvd -b:v 5000k -r 29.97 -s 720x480 -ar 48000 -b:a 384k -threads {0}'.format(CPU_CORES)),
                      ('VCD High Quality', '-f vcd -target ntsc-vcd -mbd rd -cmp 0 -subcmp 2 -threads {0}'.format(CPU_CORES)),
                      ('MS Compatible AVI', '-acodec libmp3lame -vcodec msmpeg4 -b:a 192k -b:v 1000k -s 640x480 -ar 44100 -threads {0}'.format(CPU_CORES)),
                      ('XVID Fullscreen (4:3)', '-f avi -r 29.97 -vcodec libxvid -vtag XVID -s 640x480 -aspect 4:3 -maxrate 1800k -b:v 1500k -qmin 3 -qmax 5 -bufsize 4096 -mbd 2 -bf 2 -flags +4m -cmp 2 -subcmp 2 -g 300 -acodec libmp3lame -ar 48000 -b:a 128k -ac 2 -threads {0}'.format(CPU_CORES)),
                      ('XVID Widescreen (16:9)', '-f avi -r 29.97 -vcodec libxvid -vtag XVID -s 704x384 -aspect 16:9 -maxrate 1800k -b:v 1500k -qmin 3 -qmax 5 -bufsize 4096 -mbd 2 -bf 2 -flags +4m -cmp 2 -subcmp 2 -g 300 -acodec libmp3lame -ar 48000 -b:a 128k -ac 2 -threads {0}'.format(CPU_CORES)),
                      ('FLV Fullscreen (4:3)', '-vcodec flv -f flv -r 29.97 -s 320x240 -aspect 4:3 -b:v 300k -g 160 -cmp dct -subcmp dct -mbd 2 -flags +aic+mv0+mv4 -ac 1 -ar 22050 -b:a 56k -threads {0}'.format(CPU_CORES)),
                      ('FLV Widescreen (16:9)', '-vcodec flv -f flv -r 29.97 -s 320x180 -aspect 16:9 -b:v 300k -g 160 -cmp dct -subcmp dct -mbd 2 -flags +aic+mv0+mv4 -ac 1 -ar 22050 -b:a 56k -threads {0}'.format(CPU_CORES)),
                      ('WMV Generic', '-vcodec wmv2 -acodec wmav2 -b:v 1000k -b:a 160k -r 25 -threads {0}'.format(CPU_CORES)),
                      ('WEBM Fullscreen (4:3)', '-f webm -aspect 4:3 -vcodec libvpx -g 120 -level 216 -profile:v 0 -qmax 42 -qmin 10 -rc_buf_aggressivity 0.95 -vb 2M -acodec libvorbis -aq 90 -ac 2 -threads {0}'.format(CPU_CORES)),
                      ('WEBM Widescreen (16:9)', '-f webm -aspect 16:9 -vcodec libvpx -g 120 -level 216 -profile:v 0 -qmax 42 -qmin 10 -rc_buf_aggressivity 0.95 -vb 2M -acodec libvorbis -aq 90 -ac 2 -threads {0}'.format(CPU_CORES))
                      ])


def get_profiles():
    profiles = OrderedDict()
    tree = ElementTree.parse('/home/lpozo/DevSpace/Ozkar/videomorph0.7/videomorph/profiles.xml')
    root = tree.getroot()
    for elem in root:
        profiles[elem.tag] = Profile(extension=elem[0][2].text)

    return profiles


class Profile:
    """Base class for a profile."""

    def __init__(self,
                 extension=None,
                 quality=None,
                 params=None):
        """Class initializer."""
        self.extension = extension
        self.quality = quality
        self.params = params

    @property
    def quality_tag(self):
        """Generate a tag from profile quality string."""
        tag_regex = compile(r'[A-Z]4?')
        tag = ''.join(tag_regex.findall(self.quality))

        return '[' + tag + ']'


PROFILES = get_profiles()
