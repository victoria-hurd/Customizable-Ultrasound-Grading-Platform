from pathlib import Path
import shutil
import sys
import os

def get_project_root():
    # Start from the exe location if frozen, else script location
    if getattr(sys, 'frozen', False):
        path = os.path.dirname(sys.executable)
    else:
        path = os.path.dirname(os.path.abspath(__file__))

    # Move up two directories (adjust if needed)
    app_root = Path(os.path.abspath(os.path.join(path, ".." , "..", "..")))
    return app_root

def get_app_data_dir():
    return get_project_root() / "App Data"

def get_admin_studies_dir():
    return get_app_data_dir() / "Admin Studies"

def get_grader_studies_dir():
    return get_app_data_dir() / "Grader Studies"

def ensure_app_directories():
    get_admin_studies_dir().mkdir(parents=True, exist_ok=True)
    get_grader_studies_dir().mkdir(parents=True, exist_ok=True)

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