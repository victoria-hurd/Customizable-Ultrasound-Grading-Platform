from pathlib import Path
import shutil
import sys
import subprocess
from shutil import copytree as shutil_copyfolder

APP_NAME = "Ultrasound Grader"

# ---------- CORE PATHS ----------
def get_project_root():
    """
    Returns the base path for bundled resources.
    Works in dev and PyInstaller.
    """
    dev_base_path = Path(__file__).resolve().parent.parent
    return Path(getattr(sys, "_MEIPASS", dev_base_path))


def get_resource_dir():
    """
    Read-only resources bundled with the app.
    """
    return get_project_root() / "app_resources"


# ---------- USER DATA (WRITABLE) ----------
def get_user_app_support_dir():
    """
    macOS-native writable app data directory:
    ~/Library/Application Support/Ultrasound Grader
    """
    return (
        Path.home()
        / "Library"
        / "Application Support"
        / APP_NAME
    )


def get_app_data_dir():
    """
    Alias for clarity / backward compatibility.
    """
    return get_user_app_support_dir()


def get_admin_studies_dir():
    return get_app_data_dir() / "Admin Studies"


def get_grader_studies_dir():
    return get_app_data_dir() / "Grader Studies"

def get_app_support_resources_dir():
    return get_app_data_dir() / "Resources"

def ensure_app_directories():
    """
    Ensure all writable directories exist.
    Safe to call at startup.
    """
    if not Path(get_admin_studies_dir()):
        get_admin_studies_dir().mkdir(parents=True, exist_ok=True)
        # copy over example study
        shutil_copyfolder(get_resource_dir / "examples" / "example_admin", 
                          get_admin_studies_dir() / "Example Study", 
                          dirs_exist_ok=True)

    if not Path(get_grader_studies_dir()):
        get_grader_studies_dir().mkdir(parents=True, exist_ok=True)
        # copy over example study
        shutil_copyfolder(get_resource_dir / "examples" / "example_grader", 
                          get_grader_studies_dir() / "Example Study", 
                          dirs_exist_ok=True)

    if not Path(get_app_support_resources_dir()):
        get_app_support_resources_dir().mkdir(parents=True, exist_ok=True)
        # copy over instructions
        shutil_copyfolder(get_resource_dir / "instructions", 
                          get_app_support_resources_dir(), 
                          dirs_exist_ok=True)

def reveal_in_finder(path: Path):
    """
    Reveal a file or folder in macOS Finder.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Path does not exist:\n{path}")

    subprocess.run(
        ["open", "-R", str(path)],
        check=False
    )

def move_without_overwrite(source_path, destination_dir, mode='move'):
    source_path = Path(source_path)
    destination_dir = Path(destination_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)  # Create destination directory if it doesn't exist

    # Start with the original destination path
    destination_path = destination_dir / source_path.name
    
    if not destination_path.exists():
        # If the file does not exist, just move it/copy it, depending on mode
        if mode == 'copy':
            shutil.copy(str(source_path), str(destination_path))
        else:
            shutil.move(str(source_path), str(destination_path))
        return destination_path

    else:
        # If the file exists, generate a new name
        stem = destination_path.stem
        suffix = destination_path.suffix
        counter = 1
        
        while True:
            new_filename = f"{stem}_{counter}{suffix}"
            new_destination_path = destination_dir / new_filename
            
            if not new_destination_path.exists():
                # Found a unique name, move/copy it, depending on mode
                if mode == 'copy':
                    shutil.copy(str(source_path), str(new_destination_path))
                else:
                    shutil.move(str(source_path), str(new_destination_path))
                return new_destination_path
            counter += 1

def unique_folder_in_dir(destination_dir,source_path):
    source_path = Path(source_path)
    destination_dir = Path(destination_dir)
    # Start with the original destination path
    destination_path = destination_dir / source_path.stem
    if not destination_path.exists():
        # If doesn't exist, destination path is just destination + filename
        return destination_path
    else:
        # If the file exists, generate a new name
        stem = source_path.stem # file without extension
        counter = 1
        
        while True:
            new_filename = f"{stem}_{counter}"
            new_destination_path = destination_dir / new_filename
            
            if not new_destination_path.exists():
                # Found a unique name, return it
                return new_destination_path
            counter += 1