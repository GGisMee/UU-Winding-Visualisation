import PyInstaller.__main__
import customtkinter
import os
import subprocess
import shutil
import sys
import glob

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
    '--hidden-import', 'customtkinter',
    '--hidden-import', 'tkinter',
    '--hidden-import', 'matplotlib',
    '--hidden-import', 'matplotlib.figure',
    '--hidden-import', 'matplotlib.backends.backend_tkagg',
    '--hidden-import', 'matplotlib.pyplot',
    '--hidden-import', 'numpy',
    '--hidden-import', 'scipy',
])

pyinstaller_args = [
    'obfuscated_src/winding/main.py',
    '--name=WindingSimulator',
    '--onefile',
    '--windowed',  # Prevent console window from appearing on Windows
    f'--add-data={customtkinter_path}:customtkinter',  # Include CTk assets
    '--add-data=obfuscated_src/winding/assets:winding/assets',
    '--paths=obfuscated_src',
    f'--hidden-import={runtime_pkg}',
    '--clean',
] + hidden_imports

# Fix path separator for Windows vs Linux/Mac
if sys.platform == 'win32':
    pyinstaller_args = [arg.replace(':', ';') if arg.startswith('--add-data') else arg for arg in pyinstaller_args]

PyInstaller.__main__.run(pyinstaller_args)

# 3. Clean up the temporary obfuscated source
shutil.rmtree("obfuscated_src", ignore_errors=True)

print("Build complete! Check the 'dist' directory for the highly secure executable.")
