#!/usr/bin/python3

from distutils.core import setup

setup(
    name='videomorph',
    version='0.3',
    description='Small Video Converter based on ffmpeg, Python 3 and Qt5, focused on usability.',
    author='Ozkar L. Garcell',
    author_email='codeshard@openmailbox.org',
    url='https://github.com/codeshard/videomorph',
    license='Apache License, Version 2.0',
    packages=['videomorph', 'videomorph/converter'],
    data_files=[('/usr/share/applications',['share/videomorph.desktop']),
            ('/usr/share/icons',['share/videomorph.png']),
            ('/usr/share/videomorph',[
                'videomorph/translations/videomorph_es.qm',
                'videomorph/translations/videomorph_es.ts',
                ]),
            ('/usr/share/videomorph/images',[
                'videomorph/images/videomorph.png']),
            ('/usr/share/doc/videomorph', ['README.md','LICENSE','AUTHORS'])],
        scripts = ["bin/videomorph"]
        )
