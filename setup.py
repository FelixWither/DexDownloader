from cx_Freeze import setup, Executable
import sys
import os
import shutil

# Determine the base depending on the platform
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # Use this for Windows GUI applications
elif sys.platform == "darwin":
    if sys.maxsize > 2**32:  # Check if running on a 64-bit system
        base = "Console"  # Use this for macOS 64-bit console applications
    else:
        base = None  # Use the default base for macOS

executables = [Executable("main.py", base=base)]

# Define the list of additional files to be included
additional_files = [
    "download.py",
    "search.py",
    "views.py",
    # Add more files here if needed
]

# Define the destination directory for the additional files
additional_files_dest = "additional_files"

# Define the destination directory for the dynamic libraries within the build folder
dylib_dest = os.path.join("build/exe.macosx-11-universal2-3.8", "dylib")

# Create a list of tuples specifying the source and destination paths of the additional files
include_files = [(file, os.path.join(additional_files_dest, file)) for file in additional_files]

setup(
    name="Your Program",
    version="1.0",
    description="Description of your program",
    executables=executables,
    options={
        "build_exe": {
            "include_files": include_files,
            "excludes": [],
            "zip_include_packages": [],
            "zip_exclude_packages": []
        }
    }
)

# Move the dynamic libraries to the dylib_dest directory within the build folder
os.makedirs(dylib_dest, exist_ok=True)
build_dir = "build/exe.macosx-11-universal2-3.8"
for filename in os.listdir(build_dir):
    if filename.endswith(".dylib"):
        shutil.move(os.path.join(build_dir, filename), os.path.join(dylib_dest, filename))
