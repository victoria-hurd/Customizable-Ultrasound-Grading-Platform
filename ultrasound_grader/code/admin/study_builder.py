import os
import pandas as pd
import random

VALID_EXTS = {".mp4", ".avi", ".mov", ".mkv", ".jpg", ".png"}

def detect_media_files(folder):
    if not os.path.isdir(folder):
        return []
    return [
        f for f in os.listdir(folder)
        if os.path.splitext(f)[1].lower() in VALID_EXTS
    ]

def assign_files_to_graders(files, graders, assignment_mode="all", repeat_count=1):
    """
    Returns list of dicts: [{'original': filename, 'deid': deid_name, 'grader': grader}, ...]
    """
    if not files or not graders:
        return []

    assignments = []
    deid_counter = 1

    files_to_assign = files

    if assignment_mode == "all":
        # Each grader gets all files
        for grader in graders:
            for f in files_to_assign:
                deid_name = f"MEDIA_{deid_counter:04d}{os.path.splitext(f)[1]}"
                # Repeat files if repeat_count > 1
                for i in range(repeat_count):
                    assignments.append({
                        "original_filename": f,
                        "deidentified_filename": deid_name,
                        "assigned_grader": grader,
                        "order": i+1
                    })
                deid_counter += 1
    else:
        # Split evenly among graders
        random.shuffle(files_to_assign)
        num_graders = len(graders)
        for idx, f in enumerate(files_to_assign):
            grader = graders[idx % num_graders]
            deid_name = f"IMG_{deid_counter:04d}{os.path.splitext(f)[1]}"
            # Repeat files if repeat_count > 1
            for i in range(repeat_count):
                assignments.append({
                    "original_filename": f,
                    "deidentified_filename": deid_name,
                    "assigned_grader": grader,
                    "order": i+1
                })
            deid_counter += 1

    return assignments

def create_master_study_csv(assignments, output_path):
    df = pd.DataFrame(assignments)
    df.to_csv(output_path, index=False)

def build_master_grader_dataframe(study_name, study_params, media_files):
    """
    Returns a dataframe with one row per review request.

    study_params: dict
        {
            "graders": ["Alice", "Bob"],
            "all_grade_all": True/False,
            "repeat": 1,
            "split_evenly": True/False,
            "custom_split": {"Alice": 5, "Bob": 7}  # optional
        }
    media_files: list of filenames
    """
    rows = []

    graders = study_params["graders"]
    repeat = study_params.get("repeat", 1)
    all_grade_all = study_params.get("all_grade_all", True)
    split_evenly = study_params.get("split_evenly", True)
    custom_split = study_params.get("custom_split", {})

    # Handle de-identification and order
    for r in range(repeat):
        if all_grade_all:
            for grader in graders:
                for idx, f in enumerate(media_files):
                    deid_name = f"{study_name}_VID{idx+1:03d}_R{r+1}"
                    rows.append({
                        "original_filename": f,
                        "deidentified_filename": deid_name,
                        "assigned_grader": grader,
                        "order": idx + 1,
                        "review_type": "nominal"
                    })
        else:
            # Split files among graders
            files_remaining = media_files.copy()
            for grader in graders:
                if split_evenly:
                    n_files = len(media_files) // len(graders)
                else:
                    n_files = custom_split.get(grader, 0)
                selected = files_remaining[:n_files]
                files_remaining = files_remaining[n_files:]
                for idx, f in enumerate(selected):
                    deid_name = f"{study_name}_VID{idx+1:03d}_R{r+1}"
                    rows.append({
                        "original_filename": f,
                        "deidentified_filename": deid_name,
                        "assigned_grader": grader,
                        "order": idx + 1,
                        "review_type": "nominal"
                    })

    df = pd.DataFrame(rows)
    # Randomize the order per grader
    df = df.sample(frac=1).reset_index(drop=True)
    return df
