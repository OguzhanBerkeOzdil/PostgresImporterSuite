#!/usr/bin/env python3
"""
Build script for PostgreSQL Data Import Tool

Creates a standalone executable using PyInstaller.
Author: Oğuzhan Berke Özdil
"""

import os
import subprocess
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller."""
    
    print("Building PostgreSQL Data Import Tool...")
    
    # PyInstaller command with minimal dependencies
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=PostgreSQL-Data-Import",
        "--clean",
        "--add-data=src;src",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.filedialog",
        "--hidden-import=tkinter.messagebox",
        "--exclude-module=matplotlib",
        "--exclude-module=torch",
        "--exclude-module=scipy",
        "--exclude-module=sklearn",
        "--exclude-module=cv2",
        "--exclude-module=PIL",
        "gui_app.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"Executable: dist/PostgreSQL-Data-Import.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Error: {e.stderr}")
        return False

if __name__ == "__main__":
    success = build_executable()
    if not success:
        print("Build failed. Check errors above.")
        exit(1)
