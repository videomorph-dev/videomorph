# -*- mode: python -*-

block_cipher = None


added_files = [('../VERSION', ''),
               ('../changelog.gz', ''),
               ('../LICENSE', ''),
               ('../README.md', ''),
               ('../AUTHORS', ''),
               ('../TODO', ''),
               ('../screenshot.png', ''),
               ('../share/videomorph/profiles/customized.xml', 'share/videomorph/profiles'),
               ('../share/videomorph/profiles/default.xml', 'share/videomorph/profiles'),
               ('../share/doc/videomorph/manual/manual_en.html', 'share/doc/videomorph/manual'),
               ('../share/doc/videomorph/manual/manual_es.html', 'share/doc/videomorph/manual'),
               ('../share/videomorph/translations/videomorph_es.qm', 'share/videomorph/translations'),
               ('../share/icons/videomorph.ico', 'share/icons'),
               ('../ffmpeg-linux64/', 'ffmpeg')]


a = Analysis(['videomorph'],
             pathex=['/home/lpozo/DevSpace/Ozkar/videomorph/bin'],
             binaries=[],
             datas=added_files,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='videomorph',
          debug=False,
          strip=False,
          upx=True,
          console=False,
          icon='../share/icons/videomorph.ico' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='videomorph')
