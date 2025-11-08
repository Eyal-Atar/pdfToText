# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PDF Processor
Optimized for Windows distribution
"""

block_cipher = None

a = Analysis(
    ['pdf_batch_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('pdf_batch_processor.py', '.')],
    hiddenimports=[
        'pdfplumber',
        'PIL',
        'PIL._tkinter_finder',
        'bidi',
        'bidi.algorithm',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.simpledialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PyQt5',
        'PyQt6',
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
    name='PDF_Processor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed application (no console)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon file here if available
)

