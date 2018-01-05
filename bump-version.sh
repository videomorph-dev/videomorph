#!/bin/bash

usage() {
    echo "usage: bump-version.sh <version-id>"
}

if [ $# -ne 1 ]; then
    usage
    exit 1
fi

echo "$1" > VERSION
