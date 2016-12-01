#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# File name: gods_finder.py
#
# Copyright '2016' Leodanis Pozo Ramos <lpozo@openmailbox.org>
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import collections
import fileinput
import os


def find_files(path='.', ext='.py'):
    for root, dirs, filenames in os.walk(path):
        for filename in filenames:
            if filename.endswith(ext):
                yield(os.path.join(root, filename))


def is_line(line):
    return True


def has_class(line):
    return line.startswith('class')


def has_function(line):
    return 'def ' in line


COUNTERS = dict(lines=is_line, classes=has_class, functions=has_function)


def find_gods():
    stats = collections.defaultdict(collections.Counter)
    for line in fileinput.input(find_files('..')):
        for key, func in COUNTERS.items():
            if func(line):
                stats[key][fileinput.filename()] += 1

    for filename, lines in stats['lines'].most_common():
        classes = stats['classes'][filename]
        functions = stats['functions'][filename]
        try:
            ratio = "=> {0}:1".format(functions / classes)
        except ZeroDivisionError:
            ratio = "=> n/a"

        print(filename, 'Lines:', lines, 'Functions:', functions,
              'Classes:', classes, 'Ratio:', ratio)

if __name__ == '__main__':
    find_gods()
