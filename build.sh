#!/bin/bash

python3 setup.py bdist

cd dist

tar -xvf ./videomorph*.tar.gz

cp cp -v -a ./usr ../videomorph_0.7_all

cd ..

dpkg -b videomorph_0.7_all/

# Clean
rm -R dist
rm -R build
cd videomorph_0.7_all
rm -R usr