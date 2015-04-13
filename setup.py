import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": [
        "os", "time", "shutil", "datetime", 
        "PIL",
        "PySide"
        #"PySide.QtCore.Slot", "PySide.QtCore.QMetaObject",
        #"PySide.QtUiTools.QUiLoader", 
        #"PySide.QtGui.QApplication", "PySide.QtGui.QMainWindow", "PySide.QtGui.QMessageBox"
        ], 
    "include_files": ["main.py"],
    "excludes": ["tkinter"]
}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "photospy",
    version = "0.1",
    description = "My GUI application!",
    options = {"build_exe": build_exe_options},
    executables = [Executable("main.py", base=base)]
)
