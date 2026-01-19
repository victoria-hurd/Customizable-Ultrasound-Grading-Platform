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
