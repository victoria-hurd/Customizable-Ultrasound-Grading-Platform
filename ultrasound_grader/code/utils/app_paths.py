from pathlib import Path

def get_project_root():
    # project_root/code/utils/app_paths.py → parents[2] = project_root
    return Path(__file__).resolve().parents[2]

def get_app_data_dir():
    return get_project_root() / "App Data"

def get_admin_studies_dir():
    return get_app_data_dir() / "Admin Studies"

def get_grader_studies_dir():
    return get_app_data_dir() / "Grader Studies"

def ensure_app_directories():
    get_admin_studies_dir().mkdir(parents=True, exist_ok=True)
    get_grader_studies_dir().mkdir(parents=True, exist_ok=True)
