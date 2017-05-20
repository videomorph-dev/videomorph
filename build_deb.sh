#!/bin/bash

version="1.0"
ubuntu="xenial"

gzip -n -k --best changelog changelog.gz

if [ -d dist ]
then
    rm -rfv dist/*
else
    mkdir dist
fi

# Create a binary linux distribution
python3 setup.py bdist

# Untar it to videomorph_deb
tar -xvf dist/videomorph*.tar.gz --directory videomorph_deb

# Clean
rm -rfv dist/*

# Remove __pycache__ directories so they are not put into .deb package
rm -rfv $(find videomorph_deb/ -path "*__pycache__*")

# Build the DEB package
dpkg-deb --build videomorph_deb/ "videomorph_""$version""_""$ubuntu""_all.deb"
mv -v "videomorph_""$version""_""$ubuntu""_all.deb" dist

# Some clean up
rm -rfv build videomorph_deb/usr
rm -rfv changelog.gz

# Build a standard python dist to be install with python3 setup.py install command
python3 setup.py sdist

# Include the install.sh an uninstall.sh scritps into the dist
tar -xvf dist/"videomorph-""$version"".tar.gz" --directory dist
rm -rfv dist/"videomorph-""$version"".tar.gz"
cp -v -a install.sh uninstall.sh dist/"videomorph-""$version"
cd dist
tar -cvf "videomorph-""$version".tar.gz "videomorph-""$version"
cd ..
rm -rfv dist/"videomorph-""$version"

# Runnin lintian
lintian -i dist/"videomorph_""$version""_""$ubuntu""_all.deb" >dist/lintian.log
/opt/sublime_text/sublime_text dist/lintian.log
