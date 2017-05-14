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

          data_files=[  # Desktop entry
                      ('/usr/share/applications',
                       ['share/applications/videomorph.desktop']),
                        # App icon
                      ('/usr/share/icons',
                       ['share/icons/videomorph.png']),
                        # App translation file
                      ('/usr/share/videomorph/translations',
                       ['share/videomorph/translations/videomorph_es.qm']),
                        # Default conversion profiles
                      ('/usr/share/videomorph/stdprofiles',
                       ['share/videomorph/stdprofiles/profiles.xml']),
                        # Documentation files
                      ('/usr/share/doc/videomorph',
                       ['README.md', 'LICENSE', 'AUTHORS',
                        'copyright', 'changelog.Debian', 'TODO'])],

          scripts=['bin/videomorph']
          )
