# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

basedir = os.path.join(os.sep, os.getcwd().split(os.path.sep)[0] + os.sep, *os.getcwd().split(os.path.sep)[:-1]) + os.path.sep

a = Analysis(
    ['example_nofiletest.py'],
    pathex=[],
    binaries=[],
    datas=[(basedir + "fastcvapp.py", "."), (basedir + "fcvautils.py", "."), (basedir + "examples//creativecommonsmedia//", "examples//creativecommonsmedia"), (basedir + "fonts", "fonts"), (basedir + "logviewer", "logviewer")],
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='NofileTestMAC',
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
# https://pyinstaller.org/en/stable/spec-files.html#spec-file-options-for-a-macos-bundle
app = BUNDLE(
    exe,
    name='NofileTestMAC.app',
    icon=None,
    bundle_identifier=None,
)