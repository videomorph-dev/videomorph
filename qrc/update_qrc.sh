#!/bin/bash

# Generate the videomorph_qrc.py file from videomorph.qrc
pyrcc5 -o ../videomorph/videomorph_qrc.py videomorph.qrc
