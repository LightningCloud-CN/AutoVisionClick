# -*- mode: python ; coding: utf-8 -*-

import os, sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect Flask-SocketIO engineio data
added_files = []

# Web static files
static_dir = Path('autovision/web/static')
if static_dir.exists():
    added_files.append((str(static_dir), 'static'))

# Starter templates
tmpl_dir = Path('autovision/resources/starter_templates')
if tmpl_dir.exists():
    added_files.append((str(tmpl_dir), 'starter_templates'))

# Try to collect engineio/socketio JS client
for pkg in ['engineio', 'socketio', 'flask_socketio']:
    try:
        datas = collect_data_files(pkg)
        for (src, dest) in datas:
            added_files.append((src, dest))
    except Exception:
        pass

a = Analysis(
    ['autovision/main.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'flask',
        'flask_socketio',
        'engineio',
        'socketio',
        'engineio.async_drivers.threading',
        'mss',
        'mss.windows',
        'cv2',
        'numpy',
        'PIL',
        'pydirectinput',
        'pynput',
        'pynput.keyboard',
        'pynput.keyboard._win32',
        'pynput.mouse',
        'pynput.mouse._win32',
        'customtkinter',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.simpledialog',
        'ctypes',
        'ctypes.wintypes',
        'json',
        'threading',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'pandas',
        'jedi',
        'IPython',
        'PyQt5',
        'PySide2',
        'PyQt6',
        'PySide6',
    ],
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
    name='AutoVisionClick',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
