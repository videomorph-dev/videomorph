#!/bin/bash
# VideoMorph installation script for Ubuntu

depends="ffmpeg python3 python3-pyqt6 python3-setuptools"

if type dpkg &> /dev/null
then
    for dep in $depends
    do
        if ! dpkg-query -l "$dep" | grep "ii" &> /dev/null
        then
            apt-get install "$dep"
        fi
    done
fi

python3 setup.py install
