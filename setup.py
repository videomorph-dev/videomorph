#!/usr/bin/env python3
from setuptools import setup, find_packages

from videomorph.videomorph import VERSION

if __name__ == '__main__':
    setup(name='videomorph',
          version=VERSION,
          description='Small Video Converter based on ffmpeg, '
                      'Python 3 and Qt5, focused on usability.',
          author='Ozkar L. Garcell',
          author_email='codeshard@openmailbox.org',
          maintainer='Leodanis Pozo Ramos',
          maintainer_email='lpozo@openmailbox.org',
          url='https://github.com/codeshard/videomorph',
          license='Apache License, Version 2.0',
          packages=find_packages(exclude=['tests', 'docs']),

          data_files=[('/usr/share/applications',
                       ['share/videomorph.desktop']),
                      ('/usr/share/icons',
                       ['share/videomorph.png']),
                      ('/usr/share/videomorph/translations',
                       ['videomorph/translations/videomorph_es.qm',
                      'videomorph/translations/videomorph_es.ts']),
                      ('/usr/share/videomorph/images',
                       ['videomorph/images/videomorph.png']),
                      ('/usr/share/videomorph/stdprofiles',
                       ['videomorph/stdprofiles/profiles.xml']),
                      ('/usr/share/doc/videomorph',
                       ['README.md', 'LICENSE', 'AUTHORS'])],

          scripts=["bin/videomorph"]
          )
