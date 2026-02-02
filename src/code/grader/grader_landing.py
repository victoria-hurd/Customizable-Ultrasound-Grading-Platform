import os
from pathlib import Path
from zipfile import ZipFile
from json import load as json_load
from pandas import read_csv as pd_read_csv, NA as pd_NA
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QListWidget, 
                             QMessageBox, QFileDialog, QApplication)

from shutil import copy as shutil_copy
from code.utils.app_paths import get_grader_studies_dir
from code.grader.grading_session import GradingSessionTab

class GraderLanding(QWidget):
    def __init__(self,
        parent_window=None):
        super().__init__()
        self.setWindowTitle("Grader Landing Page")
        self.parent_window = parent_window
        #self.layout_main = QHBoxLayout(self)
        #self.setLayout(self.layout_main)
        self.layout_outer = QVBoxLayout(self)
        self.setLayout(self.layout_outer)
        self.layout_main = QHBoxLayout()
        # ---------------- Back and Exit Buttons ----------------
        action_bar = QHBoxLayout()
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(QApplication.instance().quit)
        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.go_back_to_main)
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.refresh)
        action_bar.addWidget(exit_btn)
        action_bar.addWidget(back_btn)
        action_bar.addWidget(refresh_btn)
        action_bar.addStretch()
        self.layout_outer.addLayout(action_bar)
        # ---------------- Rest of layout ----------------
        self.grader_studies_dir = str(get_grader_studies_dir())
        self.studies_list = QListWidget()
        self.studies_list.itemSelectionChanged.connect(self.on_study_selected)
        self.right_panel = QVBoxLayout()
        self.study_info_label = QLabel("Select a study to see details.")
        self.start_grading_btn = QPushButton("Begin Grading")
        self.start_grading_btn.setEnabled(False)
        self.start_grading_btn.clicked.connect(self.begin_grading)

        self.download_btn = QPushButton("Download Completed Grades")
        self.download_btn.setEnabled(False)
        self.download_btn.clicked.connect(self.download_grades)

        self.right_panel.addWidget(self.study_info_label)
        self.right_panel.addWidget(self.start_grading_btn)
        self.right_panel.addWidget(self.download_btn)

        # Top-level new study button
        self.new_study_btn = QPushButton("Add New Study from Zip")
        self.new_study_btn.clicked.connect(self.add_new_study)

        left_panel = QVBoxLayout()
        left_panel.addWidget(self.new_study_btn)
        left_panel.addWidget(self.studies_list)

        self.layout_main.addLayout(left_panel, stretch=1)
        self.layout_main.addLayout(self.right_panel, stretch=2)
        self.layout_outer.addLayout(self.layout_main)

        self.load_existing_studies()

    # ---------------- Load Existing Studies ----------------
    def load_existing_studies(self):
        self.studies_list.clear()
        studies_dir = Path(self.grader_studies_dir)
        for study_folder in studies_dir.iterdir():
            if study_folder.is_dir():
                self.studies_list.addItem(study_folder.name)

    # ---------------- Handle Study Selection ----------------
    def on_study_selected(self):
        selected = self.studies_list.currentItem()
        if not selected:
            return

        release_name = selected.text()
        self.current_study_path = os.path.join(self.grader_studies_dir, release_name)

        # Read study metadata
        study_metadata_path = os.path.join(self.current_study_path, "study_metadata.json")
        if os.path.exists(study_metadata_path):
            with open(study_metadata_path, "r") as f:
                self.loaded_metadata = json_load(f)
        else:
            QMessageBox.critical(self, "Error", f"Master info not found for {release_name}")
            return
        
        self.study_name = self.loaded_metadata['study_name']

        # Read grader request file
        grade_request_file = list(Path(self.current_study_path).glob("*_grade_request.csv"))[0]
        if os.path.exists(grade_request_file):
            df_request = pd_read_csv(grade_request_file)
            self.grader_name = df_request['assigned_grader'][0]
        else:
            QMessageBox.critical(self, "Error", f"Grade request CSV not found for {grade_request_file}")
            return

        # Create output folder for finished grades
        output_dir = os.path.join(self.current_study_path, "Output Grade Data")
        os.makedirs(output_dir, exist_ok=True)
        self.grade_data_path = os.path.join(output_dir, f"{self.grader_name}_{self.study_name}_grade_data.csv")

        # generate question column names
        q_cols = []
        for q in self.loaded_metadata['questions']:
            # Question label
            q_cols.append(f"{q['question_text']}")

        if not os.path.exists(self.grade_data_path):
            # Copy initial request CSV to output as working file
            shutil_copy(grade_request_file, self.grade_data_path)
            # Add empty columns for each question
            df_output = pd_read_csv(self.grade_data_path)
            # Add the new columns with NA values
            for col_name in q_cols:
                df_output[col_name] = pd_NA
            # Rewrite the grade data file with new columns
            df_output.to_csv(self.grade_data_path, index=False)
        else:
            df_output = pd_read_csv(self.grade_data_path)

        # Count total and completed reviews
        total_reviews = len(df_output)
        completed_reviews = total_reviews - sum(df_output[q_cols].isna().any(axis=1))
        self.study_info_label.setText(
            f"Study Name: {self.study_name}\n"
            f"Grader: {self.grader_name}\n"
            f"Total Requested Reviews: {total_reviews}\n"
            f"Completed Reviews: {completed_reviews}\n"
            f"Questions per Review: {len(self.loaded_metadata['questions'])}\n"
            f"Study Location: {self.current_study_path}"
        )
        self.study_info_label.setWordWrap(True)

        # Enable buttons based on completion status
        # If not all reviews are completed, enable start grading
        if completed_reviews != total_reviews:
            self.start_grading_btn.setEnabled(True)
            self.download_btn.setText("Download Unfinished Grades")
        else:
            # If all reviews are completed, disable start grading and enable download
            self.start_grading_btn.setEnabled(False)
            self.download_btn.setEnabled(True)
            self.download_btn.setText("Download Grades")

    # ---------------- Add New Study from Zip ----------------
    def add_new_study(self):
        zip_path, _ = QFileDialog.getOpenFileName(self, "Select Study Zip", filter="Zip Files (*.zip)")
        if not zip_path:
            return
        
        # Get the name of the zip file (without extension) to use as a subfolder
        archive_name = os.path.basename(zip_path).replace('.zip', '')
        # Create a specific output directory for this archive
        self.current_study_path = os.path.join(self.grader_studies_dir, archive_name)

        with ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(self.grader_studies_dir)

        self.load_existing_studies()
        QMessageBox.information(self, "Success", f"Successfully loaded grade request {archive_name}")

    # ---------------- Begin Grading ----------------
    def begin_grading(self):
        self.builder = GradingSessionTab(self.loaded_metadata,
                                         self.current_study_path,
                                         self.grader_name,
                                         parent_window=self)
        self.builder.show()
        self.study_info_label.setText("")
        self.hide()

    # ---------------- Download Grades ----------------
    def download_grades(self):
        downloads_folder = str(Path.home() / "Downloads")
        shutil_copy(self.grade_data_path, downloads_folder)
        QMessageBox.information(self, "Download Complete", f"Grades copied to {downloads_folder}")
        self.load_existing_studies()  # refresh landing page

    def go_back_to_main(self):
        if self.parent_window:
            self.parent_window.show()  # show the admin landing page
        self.close()

    def refresh(self):
        self.load_existing_studies()
        self.studies_list.clearSelection()
        

    
