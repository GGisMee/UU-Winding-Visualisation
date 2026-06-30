# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['obfuscated_src/winding/main.py'],
    pathex=['obfuscated_src'],
    binaries=[],
    datas=[('/home/gustavg/Projects/uu_winding/.venv/lib/python3.14/site-packages/customtkinter', 'customtkinter'), ('obfuscated_src/winding/assets', 'assets')],
    hiddenimports=['pyarmor_runtime_000000', 'winding.main', 'winding.config', 'winding.gui.theme', 'winding.gui.analytics', 'winding.gui.app', 'winding.gui.console', 'winding.gui.components', 'winding.gui.language', 'winding.gui.canvas', 'winding.gui.content', 'winding.models.simulation', 'winding.models.magnets', 'winding.models.export', 'winding.snippets.magnet_functions', 'tomllib', 'customtkinter', 'tkinter', 'tkinter.filedialog', 'matplotlib', 'matplotlib.figure', 'matplotlib.backends.backend_tkagg', 'matplotlib.backends.backend_pdf', 'matplotlib.image', 'matplotlib.pyplot', 'numpy', 'tomli_w', 'PIL', 'PIL.Image', 'PIL._tkinter_finder', 'zipfile', 'tempfile', 'csv', 'textwrap', 'io', 'datetime', 'pathlib', 'traceback'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='WindingSimulator',
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
