import PyInstaller.__main__
import customtkinter
import os
import subprocess
import shutil
import sys
import glob

# Dynamisk separator (; på Windows, : på Linux)
sep = os.pathsep

# Get path to customtkinter to include its assets (themes, fonts, etc.)
customtkinter_path = os.path.dirname(customtkinter.__file__)

# 1. Obfuscate the code with PyArmor
print("Obfuscating source code with PyArmor...")
shutil.rmtree("obfuscated_src", ignore_errors=True)

# Generate obfuscated code into the 'obfuscated_src' directory
subprocess.run([sys.executable, "-m", "pyarmor.cli", "gen", "-O", "obfuscated_src", "-r", "src/winding"], check=True)

# Copy the assets folder since PyArmor only obfuscates and copies .py files
shutil.copytree("src/winding/assets", "obfuscated_src/winding/assets")

# 2. Build the obfuscated code using PyInstaller
print("Building executable with PyInstaller...")

runtime_pkg = os.path.basename(glob.glob("obfuscated_src/pyarmor_runtime_*")[0])

# Because PyArmor obfuscates imports, PyInstaller can't auto-detect them.
# We manually collect all our modules as hidden imports to guarantee inclusion.
hidden_imports = []
for root, dirs, files in os.walk("src/winding"):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            mod = path.replace("src/", "").replace(os.sep, ".").replace(".py", "")
            hidden_imports.extend(['--hidden-import', mod])

# Add critical third-party and standard library dependencies that PyInstaller misses
hidden_imports.extend([
    '--hidden-import', 'tomllib',  
    '--hidden-import', 'customtkinter',
    '--hidden-import', 'tkinter',
    '--hidden-import', 'tkinter.filedialog',
    '--hidden-import', 'matplotlib',
    '--hidden-import', 'matplotlib.figure',
    '--hidden-import', 'matplotlib.backends.backend_tkagg',
    '--hidden-import', 'matplotlib.backends.backend_pdf',
    '--hidden-import', 'matplotlib.image',
    '--hidden-import', 'matplotlib.pyplot',
    '--hidden-import', 'numpy',
    '--hidden-import', 'tomli_w',
    '--hidden-import', 'PIL',
    '--hidden-import', 'PIL.Image',
    '--hidden-import', 'PIL._tkinter_finder',
    '--hidden-import', 'zipfile',
    '--hidden-import', 'tempfile',
    '--hidden-import', 'csv',
    '--hidden-import', 'textwrap',
    '--hidden-import', 'io',
    '--hidden-import', 'datetime',
    '--hidden-import', 'pathlib',
    '--hidden-import', 'traceback',
])

pyinstaller_args = [
    'obfuscated_src/winding/main.py',
    '--name=WindingSimulator',
    '--onefile',
    '--windowed',
    f'--add-data={customtkinter_path}{sep}customtkinter',  # Använder sep här
    f'--add-data=obfuscated_src/winding/assets{sep}assets',
    '--paths=obfuscated_src',
    f'--hidden-import={runtime_pkg}',
    '--clean',
] + hidden_imports

PyInstaller.__main__.run(pyinstaller_args)

# 3. Clean up the temporary obfuscated source
shutil.rmtree("obfuscated_src", ignore_errors=True)

print("Build complete! Check the 'dist' directory for the highly secure executable.")
