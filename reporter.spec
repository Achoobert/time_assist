# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the project root directory
project_root = Path(SPECPATH)

a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Include context.yml for organization data
        ('context.yml', '.'),
        # Include any existing user_data files as examples
        ('user_data', 'user_data'),
    ],
    hiddenimports=[
        # PyQt5 modules
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'PyQt5.sip',
        # YAML support
        'yaml',
        # Standard library modules that might not be detected
        'subprocess',
        'pathlib',
        'datetime',
        'argparse',
        # Our application modules
        'scripts.github_data',
        'scripts.ui.dashboard',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Reporter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for GUI app (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # macOS specific options
    icon=None,  # Add icon path here when available
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Reporter',
)

# macOS app bundle creation
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='Reporter.app',
        icon=None,  # Add icon path here when available
        bundle_identifier='com.reporter.worktracker',
        info_plist={
            'CFBundleName': 'Reporter',
            'CFBundleDisplayName': 'Reporter - Work Tracker',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
            'LSMinimumSystemVersion': '10.13.0',
            'LSApplicationCategoryType': 'public.app-category.productivity',
            'NSAppleEventsUsageDescription': 'Reporter needs access to system events for GitHub integration.',
            'NSNetworkVolumesUsageDescription': 'Reporter may access network resources for GitHub API calls.',
        },
    )