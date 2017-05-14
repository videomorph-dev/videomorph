#!/bin/bash

# Updating the .ts file and opening it with linguist
pylupdate5 -noobsolete ../../../videomorph/*.py -ts videomorph_es.ts && linguist videomorph_es.ts
