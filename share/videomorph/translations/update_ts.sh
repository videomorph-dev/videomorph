#!/bin/bash

# Updating the .ts file and opening it with linguist
pylupdate5 -noobsolete videomorph.pro && linguist videomorph_es.ts
