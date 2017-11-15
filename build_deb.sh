#!/bin/bash

version="1.2"
package_name="videomorph_""$version""_all.deb"
python_version=$(python3 --version | cut -f2 -d " " | cut --fields=1,2 -d ".")

gzip -n --keep --force --best changelog
gzip -n --keep --force --best "share/man/videomorph.1"

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

# Addapt to .deb standard structure
mv -v videomorph_deb/usr/local/* videomorph_deb/usr
rm -rfv videomorph_deb/usr/local
rm -rfv videomorph_deb/usr/share/doc/videomorph/LICENSE
rm -rfv videomorph_deb/usr/share/doc/videomorph/INSTALL
mv videomorph_deb/usr/lib/python"$python_version"/ videomorph_deb/usr/lib/python3

# Clean
rm -rfv dist/*

# Remove __pycache__ directories so they are not put into .deb package
rm -rfv $(find videomorph_deb/ -path "*__pycache__*")

# Change Owner and Group
sudo chown -c --recursive root:root videomorph_deb/usr/
sudo chown -c --recursive root:root videomorph_deb/DEBIAN/postinst
sudo --remove-timestamp

# Build the DEB package
dpkg-deb --build videomorph_deb/ "$package_name"
mv -v "$package_name" dist

# Some clean up
sudo rm -rfv build videomorph_deb/usr
sudo --remove-timestamp

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
lintian -i dist/"$package_name" >dist/lintian.log
/opt/sublime_text/sublime_text dist/lintian.log
