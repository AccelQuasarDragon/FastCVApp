# -*- mode: python ; coding: utf-8 -*-
from kivy_deps import sdl2, glew
#reference for adding mediapipe with pyinstaller https://stackoverflow.com/questions/67887088/issues-compiling-mediapipe-with-pyinstaller-on-macos

block_cipher = None

def get_mediapipe_path():
    import mediapipe
    mediapipe_path = mediapipe.__path__[0]
    return mediapipe_path

#assume the file structure is like this:
#FastCVApp
#   \examples <--- this is where spec, example py files are 
#        \creativecommonsmedia  <-- this is where media and .task files are
#basedir = "I:\\CODING\\FastCVApp\\FastCVApp\\" # replace basedir with the location of "FastCVApp" folder
#from pathlib import Path
#import os
#basedir = os.path.join(os.sep, os.getcwd().split(os.path.sep)[0] + os.sep, *Path(__file__).absolute().split(os.path.sep)[:-1])
#cursed as __file__ doesn't work here, just do an os.getcwd() hack...

basedir = os.path.join(os.sep, os.getcwd().split(os.path.sep)[0] + os.sep, *os.getcwd().split(os.path.sep)[:-1]) + os.path.sep
print("file location?", basedir)

a = Analysis(
    ['example_mediapipe.py'],
    pathex=[],
    binaries=[],
    datas=[(basedir + "FastCVApp.py", "."), (basedir + "FCVAutils.py", "."), (basedir + "examples\\creativecommonsmedia\\", "examples\\creativecommonsmedia"), (basedir + "fonts", "fonts"), (basedir + "logviewer", "logviewer")],
    hiddenimports=['kivy', 'blosc2', 'kivy.modules.inspector'], 
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

mediapipe_tree = Tree(get_mediapipe_path(), prefix='mediapipe', excludes=["*.pyc"])
a.datas += mediapipe_tree
a.binaries = filter(lambda x: 'mediapipe' not in x[0], a.binaries)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name='Mediapipe',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
