#!/bin/bash

if [ -d dist ]
then
    rm -rfv dist
fi

python3 setup.py bdist

cd dist

tar -xvf ./videomorph*.tar.gz

cp -v -a ./usr ../videomorph_0.7_all

cd ..

# Build the DEB package
dpkg -b videomorph_0.7_all/
cp -v -a videomorph_0.7_all.deb dist

# Build a tar.gz to be install with python3 setup.py install command
python3 setup.py sdist


# Clean
rm -rfv build
rm videomorph_0.7_all.deb
cd videomorph_0.7_all
rm -rfv usr
cd ../dist
rm -rfv usr
rm videomorph-0.7.linux*