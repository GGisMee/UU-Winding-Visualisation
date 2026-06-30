# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['obfuscated_src/winding/main.py'],
    pathex=['obfuscated_src'],
    binaries=[],
    datas=[('/home/gustavg/Projects/uu_winding/.venv/lib/python3.14/site-packages/customtkinter', 'customtkinter'), ('obfuscated_src/winding/assets', 'winding/assets')],
    hiddenimports=['pyarmor_runtime_000000', 'winding.config', 'winding.main', 'winding.gui.theme', 'winding.gui.analytics', 'winding.gui.app', 'winding.gui.content', 'winding.gui.console', 'winding.gui.components', 'winding.gui.canvas', 'winding.gui.language', 'winding.models.simulation', 'winding.models.magnets', 'winding.models.export', 'winding.snippets.magnet_functions', 'customtkinter', 'tkinter', 'matplotlib', 'matplotlib.figure', 'matplotlib.backends.backend_tkagg', 'matplotlib.pyplot', 'numpy', 'scipy'],
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
