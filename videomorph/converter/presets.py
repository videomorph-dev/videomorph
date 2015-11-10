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


class BaseProfile(object):
    """ Class doc """
    profile_name = None
    profile_extension = None
    profile_label = None
    profile_params = None
    

class MP4HQProfile(BaseProfile):
    profile_name = u'MP4'
    profile_extension = u'.mp4'
    profile_label = u'MP4 High Quality'
    profile_params = u'-crf 35.0 -vcodec libx264 -acodec aac -ar 48000 -b:a 128k -coder 1 -flags +loop -cmp +chroma -partitions +parti4x4+partp8x8+partb8x8 -me_method hex -subq 6 -me_range 16 -g 250 -keyint_min 25 -sc_threshold 40 -i_qfactor 0.71 -b_strategy 1 -strict -2 -threads 0'


class MP4VHQProfile(BaseProfile):
    profile_name = u'MP4'
    profile_extension = u'.mp4'
    profile_label = u'MP4 Very High Quality'
    profile_params = u'-crf 25.0 -vcodec libx264 -acodec aac -ar 48000 -b:a 160k -coder 1 -flags +loop -cmp +chroma -partitions +parti4x4+partp8x8+partb8x8 -me_method hex -subq 6 -me_range 16 -g 250 -keyint_min 25 -sc_threshold 40 -i_qfactor 0.71 -b_strategy 1 -strict -2 -threads 0'
    

class MP4SHQProfile(BaseProfile):
    profile_name = u'MP4'
    profile_extension = u'.mp4'
    profile_label = u'MP4 Super High Quality'
    profile_params = u'-crf 15.0 -vcodec libx264 -acodec aac -ar 48000 -b:a 192k -coder 1 -flags +loop -cmp +chroma -partitions +parti4x4+partp8x8+partb8x8 -me_method hex -subq 6 -me_range 16 -g 250 -keyint_min 25 -sc_threshold 40 -i_qfactor 0.71 -b_strategy 1 -strict -2 -threads 0'
    
    
class MP4FSProfile(BaseProfile):
    profile_name = u'MP4'
    profile_extension = u'.mp4'
    profile_label = u'MP4 Fullscreen'
    profile_params = u'-f mp4 -r 29.97 -vcodec libx264 -s 640x480 -b:v 1000k -aspect 4:3 -flags +loop -cmp +chroma -deblockalpha 0 -deblockbeta 0 -maxrate 1500k -bufsize 4M -bt 256k -refs 1 -bf 3 -coder 1 -me_method umh -me_range 16 -subq 7 -partitions +parti4x4+parti8x8+partp8x8+partb8x8 -g 250 -keyint_min 25 -level 30 -qmin 10 -qmax 51 -qcomp 0.6 -sc_threshold 40 -i_qfactor 0.71 -acodec aac -b:a 112k -ar 48000 -ac 2 -strict -2 -threads 0'
    

class MP4WSProfile(BaseProfile):
    profile_name = u'MP4'
    profile_extension = u'.mp4'
    profile_label = u'MP4 Widescreen'
    profile_params = u'-f mp4 -r 29.97 -vcodec libx264 -s 704x384 -b:v 1000k -aspect 16:9 -flags +loop -cmp +chroma -maxrate 1500k -bufsize 4M -bt 256k -refs 1 -bf 3 -coder 1 -me_method umh -me_range 16 -subq 7 -partitions +parti4x4+parti8x8+partp8x8+partb8x8 -g 250 -keyint_min 25 -level 30 -qmin 10 -qmax 51 -qcomp 0.6 -trellis 2 -sc_threshold 40 -i_qfactor 0.71 -acodec aac -b:a 112k -ar 48000 -ac 2 -strict -2 -threads 0'
    
    
class DVDFSProfile(BaseProfile):
    profile_name = u'DVD'
    profile_extension = u'.mpg'
    profile_label = u'DVD Fullscreen'
    profile_params = u'-f dvd -target ntsc-dvd -vcodec mpeg2video -r 29.97 -s 352x480 -aspect 4:3 -b:v 4000k -mbd rd -cmp 2 -subcmp 2 -acodec mp2 -b:a 192k -ar 48000 -ac 2 -threads 0'
    

class DVDWSProfile(BaseProfile):
    profile_name = u'DVD'
    profile_extension = u'.mpg'
    profile_label = u'DVD Widescreen'
    profile_params = u'-f dvd -target ntsc-dvd -vcodec mpeg2video -r 29.97 -s 352x480 -aspect 16:9 -b:v 4000k -mbd rd -cmp 2 -subcmp 2 -acodec mp2 -b:a 192k -ar 48000 -ac 2 -threads 0'


class DVDFSHQProfile(BaseProfile):
    profile_name = u'DVD'
    profile_extension = u'.mpg'
    profile_label = u'DVD Fullscreen High Quality'
    profile_params = u'-f dvd -target ntsc-dvd -r 29.97 -s 720x480 -aspect 4:3 -b:v 8000k -mbd rd -cmp 0 -subcmp 2 -threads 0'
    
    
class DVDWSHQProfile(BaseProfile):
    profile_name = u'DVD'
    profile_extension = u'.mpg'
    profile_label = u'DVD Widescreen High Quality'
    profile_params = u'-f dvd -target ntsc-dvd -r 29.97 -s 720x480 -aspect 16:9 -b:v 8000k -g 12 -mbd rd -cmp 0 -subcmp 2 -threads 0'


class DVDLQProfile(BaseProfile):
    profile_name = u'DVD'
    profile_extension = u'.mpg'
    profile_label = u'DVD Low Quality'
    profile_params = u'-f dvd -target ntsc-dvd -b:v 5000k -r 29.97 -s 720x480 -ar 48000 -b:a 384k -threads 0'
    
    
class VCDHQProfile(BaseProfile):
    profile_name = u'VCD'
    profile_extension = u'.mpg'
    profile_label = u'VCD High Quality'
    profile_params = u'-f vcd -target ntsc-vcd -mbd rd -cmp 0 -subcmp 2 -threads 0'
    
    
class MSAVIProfile(BaseProfile):
    profile_name = u'AVI'
    profile_extension = u'.avi'
    profile_label = u'MS Compatible AVI'
    profile_params = u'-acodec libmp3lame -vcodec msmpeg4 -b:a 192k -b:v 1000k -s 640x480 -ar 44100 -threads 0'
    
    
class XVIDFSProfile(BaseProfile):
    profile_name = u'AVI'
    profile_extension = u'.avi'
    profile_label = u'XVID Fullscreen'
    profile_params = u'-f avi -r 29.97 -vcodec libxvid -vtag XVID -s 640x480 -aspect 4:3 -maxrate 1800k -b:v 1500k -qmin 3 -qmax 5 -bufsize 4096 -mbd 2 -bf 2 -flags +4m -cmp 2 -subcmp 2 -g 300 -acodec libmp3lame -ar 48000 -b:a 128k -ac 2 -threads 0'
    
    
class XVIDWSProfile(BaseProfile):
    profile_name = u'AVI'
    profile_extension = u'.avi'
    profile_label = u'XVID Widescreen'
    profile_params = u'-f avi -r 29.97 -vcodec libxvid -vtag XVID -s 704x384 -aspect 16:9 -maxrate 1800k -b:v 1500k -qmin 3 -qmax 5 -bufsize 4096 -mbd 2 -bf 2 -flags +4m -cmp 2 -subcmp 2 -g 300 -acodec libmp3lame -ar 48000 -b:a 128k -ac 2 -threads 0'


class FLVFSProfile(BaseProfile):
    profile_name = u'FLV'
    profile_extension = u'.flv'
    profile_label = u'FLV Fullscreen'
    profile_params = u'-vcodec flv -f flv -r 29.97 -s 320x240 -aspect 4:3 -b:v 300k -g 160 -cmp dct -subcmp dct -mbd 2 -flags +aic+mv0+mv4 -ac 1 -ar 22050 -b:a 56k -threads 0'


class FLVWSProfile(BaseProfile):
    profile_name = u'FLV'
    profile_extension = u'.flv'
    profile_label = u'FLV Widescreen'
    profile_params = u'-vcodec flv -f flv -r 29.97 -s 320x180 -aspect 16:9 -b:v 300k -g 160 -cmp dct -subcmp dct -mbd 2 -flags +aic+mv0+mv4 -ac 1 -ar 22050 -b:a 56k -threads 0'
    
    
class WMVProfile(BaseProfile):
    profile_name = u'WMV'
    profile_extension = u'.wmv'
    profile_label = u'WMV Generic'
    profile_params = u'-vcodec wmv2 -acodec wmav2 -b:v 1000k -b:a 160k -r 25 -threads 0'

presets_list = [
    MP4HQProfile,
    MP4VHQProfile,
    MP4SHQProfile,
    MP4FSProfile,
    MP4WSProfile,
    DVDFSProfile,
    DVDWSProfile,
    DVDFSHQProfile,
    DVDWSHQProfile,
    DVDLQProfile,
    VCDHQProfile,
    MSAVIProfile,
    XVIDFSProfile,
    XVIDWSProfile,
    FLVFSProfile,
    FLVWSProfile,
    WMVProfile,
]
