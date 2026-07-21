# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Pratikey — macOS .app + DMG

import sys
from pathlib import Path

block_cipher = None

# ── macOS-specific hidden imports ──────────────────────────────
mac_hidden = [
    'pynput.keyboard._darwin',
    'pynput.mouse._darwin',
    'pystray._darwin',
    'AppKit',
    'Foundation',
    'Quartz',
    'objc',
    'PyObjCTools',
    'PyObjCTools.AppHelper',
]

win_hidden = [
    'pynput.keyboard._win32',
    'pynput.mouse._win32',
    'pystray._win32',
]

hidden = mac_hidden if sys.platform == 'darwin' else win_hidden
hidden += ['PIL._tkinter_finder', 'pkg_resources.py2_compat']

a = Analysis(
    ['tray.py'],
    pathex=[str(Path('.').resolve())],
    binaries=[],
    datas=[
        ('config.json',        '.'),
        ('config.schema.json', '.'),
        ('icons',              'icons'),
    ],
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    # tkinter is needed on Windows for the HUD bar — only exclude it on macOS
    excludes=(['tkinter'] if sys.platform == 'darwin' else []) + ['matplotlib', 'numpy', 'scipy'],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Pratikey',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,          # UPX can cause macOS Gatekeeper issues
    console=False,      # No terminal window
    icon='icons/pratikey.icns' if sys.platform == 'darwin' else 'icons/pratikey.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    name='Pratikey',
)

# ── macOS .app bundle ──────────────────────────────────────────
if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='Pratikey.app',
        icon='icons/pratikey.icns',
        bundle_identifier='com.pratikey.app',
        info_plist={
            # Basic identity
            'CFBundleName':               'Pratikey',
            'CFBundleDisplayName':        'Pratikey',
            'CFBundleVersion':            '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleIdentifier':         'com.pratikey.app',
            'CFBundleIconFile':           'pratikey.icns',

            # Tray-only: hide from Dock and App Switcher
            'LSUIElement':                True,

            # High-res screen support
            'NSHighResolutionCapable':    True,

            # Privacy usage descriptions (shown in permission dialogs)
            'NSAppleEventsUsageDescription':
                'Pratikey needs Accessibility access to detect F-key presses system-wide.',

            # Allow running without App Store signing (direct download)
            'LSMinimumSystemVersion':     '10.14',
        },
    )
