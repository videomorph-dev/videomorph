#!/bin/bash

gzip -n -k --best changelog changelog.gz

if [ -d videomorph_1.0_xenial_all/dist ]
then
    rm -rfv videomorph_1.0_xenial_all/dist
fi

python3 setup.py bdist

cd dist

tar -xvf ./videomorph*.tar.gz

cp -v -a ./usr ../videomorph_1.0_xenial_all

cd ..

# Build the DEB package
dpkg -b videomorph_1.0_xenial_all/
cp -v -a videomorph_1.0_xenial_all.deb dist

# Build a tar.gz to be install with python3 setup.py install command
python3 setup.py sdist


# Clean
rm -rfv build
rm videomorph_1.0_xenial_all.deb
cd videomorph_1.0_xenial_all
rm -rfv usr
cd ../dist
rm -rfv usr
rm videomorph-1.0.linux*
cd ..
cp -v -a dist videomorph_1.0_xenial_all
rm -rfv dist
cd videomorph_1.0_xenial_all/dist
echo "This is" $PWD
tar -xvf videomorph-1.0.tar.gz
rm -rfv videomorph-1.0.tar.gz
cd ..
cd ..
cp -v -a install.sh videomorph_1.0_xenial_all/dist/videomorph-1.0
cp -v -a uninstall.sh videomorph_1.0_xenial_all/dist/videomorph-1.0
cd videomorph_1.0_xenial_all/dist
tar -cvf videomorph-1.0.tar.gz videomorph-1.0
rm -rfv videomorph-1.0

# Runnin lintian
lintian -i videomorph_1.0_xenial_all.deb >lintian.log

cd ..
cd ..
rm -rfv changelog.gz
