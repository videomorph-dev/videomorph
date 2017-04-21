#!/bin/bash
# VideoMorph installation script

depends="ffmpeg avconv python3 python3-pyqt5"

for dep in $depends
do
    if ! dpkg-query -l "$dep" | grep "ii" &> /dev/null
    then
        apt-get install "$dep"
    fi
done

python3 setup.py install
