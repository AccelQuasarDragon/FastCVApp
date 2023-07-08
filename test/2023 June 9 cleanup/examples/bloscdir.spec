# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

#def get_blosc2_path():
#    import blosc2
#    blosc2_path = blosc2.__path__[0]
#    return blosc2_path

a = Analysis(
    ['blosctest3.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['blosc2'],
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

#blosc2_tree = Tree(get_blosc2_path(), prefix='blosc2', excludes=["*.pyc"])
#a.datas += blosc2_tree
#a.binaries = filter(lambda x: 'blosc' not in x[0], a.binaries)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='bloscdir',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='bloscdir',
)
