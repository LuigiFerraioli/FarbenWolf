# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

datas = [
    ("resources/LogoIcon.ico", "resources"),
    ("resources/LogoIcon.png", "resources"),
    ("resources/LogoTransparent.png", "resources"),
    ("resources/style.qss", "resources"),
]


a = Analysis(
    ['src/main.py'],
    pathex=[os.path.abspath("src")],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pkg_resources'],
    noarchive=False,
    excludedimports=['pkg_resources']
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='FarbenWolf',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False,
    icon='resources/LogoIcon.ico'
)
