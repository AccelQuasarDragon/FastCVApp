# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['examples/example_cannyedge.py'],
    pathex=[],
    binaries=[],
    datas=[('FastCVApp.py', '.'), ('examples//creativecommonsmedia//','examples//creativecommonsmedia')],
    hiddenimports=[],
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
    name='CannyEdgeMAC',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
# https://pyinstaller.org/en/stable/spec-files.html#spec-file-options-for-a-macos-bundle
app = BUNDLE(
    exe,
    name='CannyEdgeMAC.app',
    icon=None,
    bundle_identifier=None,
)
