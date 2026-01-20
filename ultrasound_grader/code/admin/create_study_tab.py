import os
import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFileDialog, QLineEdit,
                             QScrollArea, QGroupBox, QMessageBox,
                             QListWidget, QRadioButton, QSpinBox,
                             QButtonGroup, QProgressBar, QFrame,
                             QApplication)
from PyQt6.QtCore import pyqtSignal, Qt 
from zipfile import ZipFile
import shutil
import random
import pandas as pd
from code.utils.schema import load_question_schema
from code.admin.study_builder import (detect_media_files, 
                                 assign_files_to_graders, 
                                 create_master_study_csv)
from code.utils.app_paths import get_admin_studies_dir

# Create the study building tab for admin users
class CreateStudyTab(QWidget):
    def __init__(
        self,
        parent=None,
        mode="new",                    # "new" | "edit" 
        study_name=None,
        source_study_path=None
    ):
        super().__init__(parent)

        self.mode = mode
        self.study_name = study_name
        self.source_study_path = source_study_path

        self.questions = []
        self._build_ui()

        if self.mode == "edit":
            self.load_existing_study()

    def _build_ui(self):
        outer_layout = QVBoxLayout()
        content_layout = QVBoxLayout()

        # get info about the study being created (name, data folder)
        study_box = QGroupBox("Study Information")
        study_layout = QVBoxLayout()

        self.study_name_input = QLineEdit()
        self.study_name_input.setPlaceholderText("Enter study name")
        self.study_name_input.textChanged.connect(self.update_source_study_path)

        study_layout.addWidget(QLabel("Study Name"))
        study_layout.addWidget(self.study_name_input)

        folder_layout = QHBoxLayout()
        self.image_folder_label = QLabel("No folder selected")
        folder_btn = QPushButton("Select Image / Video Folder")
        folder_btn.clicked.connect(self.select_image_folder)

        folder_layout.addWidget(folder_btn)
        folder_layout.addWidget(self.image_folder_label)

        study_layout.addLayout(folder_layout)
        study_box.setLayout(study_layout)

        # Add the grader information
        grader_box = QGroupBox("Graders")
        grader_layout = QVBoxLayout()
        self.grader_widget = GraderInputWidget()
        grader_layout.addWidget(self.grader_widget)
        self.grader_widget.graders_changed.connect(self.update_grading_summary)
        grader_box.setLayout(grader_layout)

        # Add the grader split and assignment info
        split_box = QGroupBox("Grading Assignment")
        split_layout = QVBoxLayout()
        self.grader_split_widget = GraderSplitWidget()
        self.grader_split_widget.assignment_changed.connect(self.update_grading_summary)
        self.grader_widget.graders_changed.connect(self.update_grading_summary)
        split_layout.addWidget(self.grader_split_widget)
        self.grader_split_widget.assignment_changed.connect(self.update_grading_summary)
        split_box.setLayout(split_layout)

        # Show live look at grader split
        summary_box = QGroupBox("Grading Summary")
        summary_layout = QVBoxLayout()
        self.detected_files_label = QLabel("Detected files: 0")
        self.per_grader_label = QLabel("Each grader will review: 0")
        summary_layout.addWidget(self.detected_files_label)
        summary_layout.addWidget(self.per_grader_label)
        summary_box.setLayout(summary_layout)

        # Get questions as parsed by schema.py
        question_box = QGroupBox("Grading Questions")
        question_layout = QVBoxLayout()
        question_btn = QPushButton("Upload Question Spreadsheet")
        question_btn.clicked.connect(self.load_questions)
        self.question_summary_label = QLabel("No question file loaded")
        question_layout.addWidget(question_btn)
        question_layout.addWidget(self.question_summary_label)
        self.question_list_layout = QVBoxLayout()
        scroll_widget = QWidget()
        scroll_widget.setLayout(self.question_list_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_widget)
        question_layout.addWidget(scroll)
        question_box.setLayout(question_layout)

        # Create main layout
        content_layout.addWidget(study_box)
        content_layout.addWidget(grader_box)
        content_layout.addWidget(split_box)
        content_layout.addWidget(summary_box)
        content_layout.addWidget(question_box)
        content_layout.addStretch()

        # Create scroll area for content
        scroll_container = QWidget()
        scroll_container.setLayout(content_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_container)
        outer_layout.addWidget(scroll_area)

        action_bar = QHBoxLayout()
        action_bar.addStretch()

        create_btn = QPushButton("Create Study")
        create_btn.clicked.connect(self.create_study_clicked)

        action_bar.addWidget(create_btn)
        outer_layout.addLayout(action_bar)

        self.setLayout(outer_layout)

    def select_image_folder(self):
        # Open dialog to select input data folder
        folder = QFileDialog.getExistingDirectory(
            self, "Select Image / Video Folder"
        )
        if folder:
            self.image_folder_label.setText(folder)
        # Update the grading summary box
        self.update_grading_summary()

    def load_questions(self):
        # Open dialog to select question Excel file for schema.py
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Question Spreadsheet",
            "",
            "Excel Files (*.xlsx *.xls)"
        )

        if not path:
            return

        try:
            self.questions = load_question_schema(path)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error Loading Questions",
                str(e)
            )
            return

        # Clear previous question list
        while self.question_list_layout.count():
            item = self.question_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Display detected questions
        for q in self.questions:
            label = QLabel(
                f"Q{q['question_id']}: {q['question_text']} "
                f"({q['question_type']})"
            )
            label.setWordWrap(True)
            self.question_list_layout.addWidget(label)

        self.question_summary_label.setText(
            f"Detected {len(self.questions)} grading questions"
        )

    def create_study_clicked(self):
        study_name = self.study_name_input.text().strip()
        data_folder = self.image_folder_label.text()
        graders = self.grader_widget.get_graders()
        assignment = self.grader_split_widget.get_assignment_mode()
        repeat_count = assignment["repeat_count"]
        questions = self.questions

        if not study_name:
            QMessageBox.warning(self, "Missing Info", "Please enter study name.")
            return
        if not data_folder:
            QMessageBox.warning(self, "Missing Info", "Please enter video data folder.")
            return
        if not graders:
            QMessageBox.warning(self, "Missing Info", "Please enter grader names.")
            return
        if not questions:
            QMessageBox.warning(self, "Missing Info", "Please enter grading question spreadsheet.")
            return

        media_files = self._count_media_files_list()
        if not media_files:
            QMessageBox.warning(self, "No Files", "No valid image/video files found in folder.")
            return

        # If study is new, create folder
        if self.source_study_path == None:
            self.source_study_path = os.path.join(get_admin_studies_dir(),study_name)
        print(self.source_study_path)

        # Make study folder if it doesn't exist yet
        os.makedirs(self.source_study_path, exist_ok=True)

        # Make empty results folder
        results_folder = os.path.join(self.source_study_path, "Results")
        os.makedirs(results_folder, exist_ok=True)

        # OUTPUT 1: All Grader Requests Master CSV
        all_requests_csv_path = os.path.join(self.source_study_path, f"all_grader_requests_{study_name}.csv")

        assignments = []
        deid_counter = 1

        if assignment["mode"] == "all_graders_all_images":
            # Each grader gets all files
            for f in media_files:
                    deid_name = f"MEDIA_{deid_counter:04d}{os.path.splitext(f)[1]}"
                    for grader in graders:
                        # Repeat files if repeat_count > 1
                        for i in range(repeat_count):
                            assignments.append({
                                "original_filename": f,
                                "deidentified_filename": deid_name,
                                "assigned_grader": grader,
                                "repeat_num": i+1
                            })
                    deid_counter += 1

        else:
            # Split evenly among graders
            random.shuffle(media_files)
            num_graders = len(graders)
            for idx, f in enumerate(media_files):
                grader = graders[idx % num_graders]
                deid_name = f"MEDIA_{deid_counter:04d}{os.path.splitext(f)[1]}"
                # Repeat files if repeat_count > 1
                for i in range(repeat_count):
                    assignments.append({
                        "original_filename": f,
                        "deidentified_filename": deid_name,
                        "assigned_grader": grader,
                        "repeat_num": i+1
                    })
                deid_counter += 1

        import pandas as pd
        df = pd.DataFrame(assignments)
        df.to_csv(all_requests_csv_path, index=False)

        self.review_type = "nominal"

        # OUTPUT 2: Study Metadata
        study_metadata = {
            "study_name": study_name,
            "data_folder": data_folder,
            "graders": graders,
            "assignment_mode": assignment["mode"],
            "repeat_count": repeat_count,
            "questions": questions
        }
        metadata_path = os.path.join(self.source_study_path, "study_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(study_metadata, f, indent=4)

        # Show success panel with summary, study folder, and grader releases button
        self.show_study_success(study_name, self.source_study_path, data_folder, graders, assignment, repeat_count, len(media_files),)

    def _count_media_files(self):
        folder = self.image_folder_label.text()
        if not os.path.isdir(folder):
            return 0

        valid_exts = {".mp4", ".avi", ".mov", ".mkv", ".jpg", ".png"}
        return sum(
            1 for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in valid_exts
        )
    
    def _count_media_files_list(self):
        folder = self.image_folder_label.text()
        if not os.path.isdir(folder):
            return []

        valid_exts = {".mp4", ".avi", ".mov", ".mkv", ".jpg", ".png"}
        return [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in valid_exts]

    # Live-update the grading summary based on current inputs
    def update_grading_summary(self):
        # Get number of files and graders from inputs
        num_files = self._count_media_files()
        graders = self.grader_widget.get_graders()
        num_graders = len(graders)
        # Display number of detected files
        self.detected_files_label.setText(
            f"Detected files: {num_files}"
        )
        # Display number of inputted graders
        if num_files == 0 or num_graders == 0:
            self.per_grader_label.setText(
                "Each grader will review: —"
            )
            return
        # Get the assignment mode and repeat settings
        assignment = self.grader_split_widget.get_assignment_mode()
        # If no repeat set, then repeat is 1 review per image per grader
        repeat_multiplier = assignment["repeat_count"] if assignment["repeat"] else 1
        # Calculate number of images per grader
        # Mode 1: All graders grade all images (with repeats if set)
        if assignment["mode"] == "all_graders_all_images":
            per_grader = num_files * repeat_multiplier
            # Build summary string
            summary_lines = []
            for g in graders:
                summary_lines.append(f"{g}: {per_grader}")
            summary_text = "All graders grade all images:\n" + "\n".join(summary_lines)
            if assignment["repeat"]:
                summary_text += f"\nRepeated {repeat_multiplier}x"
            self.per_grader_label.setText(summary_text)
        else:
            # Mode 2: Split evenly among graders (with repeats if set)
            base_count = num_files // num_graders
            remainder = num_files % num_graders
            # Assign counts per grader
            grader_counts = [base_count] * num_graders
            # Distribute extra images to graders in order
            for i in range(remainder):
                grader_counts[i] += 1
            # Apply repeat multiplier
            if assignment["repeat"]:
                grader_counts = [c * repeat_multiplier for c in grader_counts]
            # Build summary string
            summary_lines = []
            for g, count in zip(graders, grader_counts):
                summary_lines.append(f"{g}: {count}")
            summary_text = "Split among graders:\n" + "\n".join(summary_lines)
            if assignment["repeat"]:
                summary_text += f"\nRepeated {repeat_multiplier}x"
            self.per_grader_label.setText(summary_text)

    def show_study_success(self, study_name, study_folder, data_folder, graders, assignment, repeat_count, num_files):
        # Hide all existing widgets in the tab (inputs, labels, etc.)
        central_layout = self.layout()
        for i in reversed(range(central_layout.count())):
            item = central_layout.itemAt(i)
            if item.widget():
                item.widget().hide()
            elif item.layout():
                # hide widgets inside nested layouts
                for j in range(item.layout().count()):
                    sub_item = item.layout().itemAt(j)
                    if sub_item.widget():
                        sub_item.widget().hide()

        # Create info string
        summary_str = f"Study Name: {study_name}\nStudy Folder: {study_folder}\nData Folder: {data_folder}\nNumber of Media Files: {num_files}\nNumber of Graders: {len(graders)}\n"
        # Success string
        success_str = "Study created successfully!\n\n"

        # Assignment summary below
        grader_assign = "Grader assignments:\n"
        if assignment["mode"] == "all_graders_all_images":
            for g in graders:
                grader_assign += f"  {g}: {num_files * repeat_count} images\n"
        else:
            base_count = num_files // len(graders)
            remainder = num_files % len(graders)
            counts = [base_count] * len(graders)
            for i in range(remainder):
                counts[i] += 1
            counts = [c * repeat_count if assignment["repeat"] else c for c in counts]
            for g, c in zip(graders, counts):
                grader_assign += f"  {g}: {c} images\n"
        if assignment["repeat"]:
            grader_assign += f"Repeat enabled: {repeat_count}x"

        # Create label for next step information
        info_str = "\nThe next step is to create grader release folders, which contain the media assigned to each grader and a per-grader master spreadsheet. These folders are zipped such that they can be sent to graders for review, named accordingly based on the provided grader names. Note that the images will be presented in a randomized, deidentified manner. \n"
        
        # Create widget
        success_widget = QLabel(success_str+summary_str+grader_assign+info_str)
        success_widget.setWordWrap(True)
        success_widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Add to layout
        success_frame = QFrame()
        success_layout = QVBoxLayout(success_frame)
        success_layout.addWidget(success_widget)

        # Button to move to next step
        self.current_study_folder = study_folder
        self.create_release_btn = QPushButton("Create Grader Release Folders")
        self.create_release_btn.clicked.connect(self.create_grader_release_folders)
        success_layout.addWidget(self.create_release_btn)

        # Add the frame to the main tab layout
        self.layout().addWidget(success_frame)

    def create_grader_release_folders(self):
        # Master study CSV
        study_name = self.study_name_input.text().strip()
        requests_csv = os.path.join(self.current_study_folder, f"all_grader_requests_{study_name}.csv")
        if not os.path.exists(requests_csv):
            QMessageBox.critical(self, "Error", "Master requests study CSV not found.")
            return

        # Read master CSV
        df = pd.read_csv(requests_csv)

        # Create grader releases root folder
        releases_folder = os.path.join(self.current_study_folder, "Grader Releases")
        os.makedirs(releases_folder, exist_ok=True)

        graders = df["assigned_grader"].unique()

        # Progress bar
        progress = QProgressBar()
        progress.setMaximum(len(graders))
        self.layout().addWidget(progress)

        for i, grader in enumerate(graders, start=1):
            grader_folder = os.path.join(releases_folder, f"{grader}_{study_name}")
            raw_folder = os.path.join(grader_folder, "Raw Data")
            os.makedirs(raw_folder, exist_ok=True)

            grader_df = df[df["assigned_grader"] == grader].copy()

            # Copy assigned files with de-identified names
            for _, row in grader_df.iterrows():
                src_file = os.path.join(self.image_folder_label.text(), row["original_filename"])
                dest_file = os.path.join(raw_folder, row["deidentified_filename"])
                if os.path.exists(src_file):
                    shutil.copy(src_file, dest_file)
                else:
                    print(f"Warning: source file not found: {src_file}")

            # Create per-grader master CSV
            grader_df = grader_df.drop(columns=["original_filename"]).copy()
            grader_df["review_type"] = self.review_type
            grader_csv_path = os.path.join(
                grader_folder,
                f"{grader}_{study_name}_grade_request.csv"
            )
            # # Add questions, make empty columns for answers
            # for q in self.questions:
            #     grader_df[f"Q{q['question_id']}"] = ""
            
            grader_df.to_csv(grader_csv_path, index=False)

            # Copy over the metadata file
            metadata_file = os.path.join(self.current_study_folder, "study_metadata.json")
            if os.path.exists(metadata_file):
                shutil.copy(metadata_file, os.path.join(grader_folder, "study_metadata.json"))
            else:
                print(f"Warning: source file not found: {metadata_file}")
            # Zip the grader folder
            zip_path = os.path.join(releases_folder, f"{grader}_{study_name}_release.zip")
            with ZipFile(zip_path, 'w') as zipf:
                for root, _, files in os.walk(grader_folder):
                    for file in files:
                        abs_path = os.path.join(root, file)
                        arcname = os.path.relpath(abs_path, start=releases_folder)
                        zipf.write(abs_path, arcname)

            progress.setValue(i)

        # Show success panel 
        self.show_release_success(study_name, self.current_study_folder, graders)

    def show_release_success(self, study_name, study_folder, graders):
        # Hide all existing widgets in the tab (inputs, labels, etc.)
        central_layout = self.layout()
        for i in reversed(range(central_layout.count())):
            item = central_layout.itemAt(i)
            if item.widget():
                item.widget().hide()
            elif item.layout():
                # hide widgets inside nested layouts
                for j in range(item.layout().count()):
                    sub_item = item.layout().itemAt(j)
                    if sub_item.widget():
                        sub_item.widget().hide()

        # Create info string
        grader_string = ", ".join(str(x) for x in graders)
        summary_str = f"Study Name: {study_name}\nStudy Folder: {study_folder}\nGrader Releases Created: {grader_string}\n"
        # Success string
        success_str = "Releases created successfully!\n\n"

        # Create label for next step information
        info_str = "\nThe next step is to send the release folders to their respective graders. Depending on the size of your study, these may need to be sent via large file transfer service or physically via thumb drive. \n"
        
        # Create widget
        success_widget = QLabel(success_str + summary_str + info_str)
        success_widget.setWordWrap(True)
        success_widget.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)

        # Add to layout
        success_frame = QFrame()
        success_layout = QVBoxLayout(success_frame)
        success_layout.addWidget(success_widget)

        # Button to close application
        self.exit_button = QPushButton("Exit Application")
        self.exit_button.clicked.connect(QApplication.instance().quit)

        success_layout.addSpacing(20)
        success_layout.addWidget(self.exit_button)
        success_layout.addStretch()

        # Add all to main layout
        self.layout().addWidget(success_frame)

    def load_existing_study(self):
        # Load existing study metadata and populate fields
        metadata_path = os.path.join(self.source_study_path, "study_metadata.json")
        if not os.path.exists(metadata_path):
            QMessageBox.critical(self, "Error", "Study metadata file not found. Creating new study instead.")
            return

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        # Populate fields
        self.study_name_input.setText(metadata.get("study_name", ""))
        self.image_folder_label.setText(metadata.get("data_folder", ""))

        # Populate graders
        graders = metadata.get("graders", [])
        for grader in graders:
            self.grader_widget.list_widget.addItem(grader)

        # Populate assignment mode
        assignment_mode = metadata.get("assignment_mode", "all_graders_all_images")
        repeat_count = metadata.get("repeat_count", 1)

        if assignment_mode == "all_graders_all_images":
            self.grader_split_widget.all_grade_all_radio.setChecked(True)
        else:
            self.grader_split_widget.split_radio.setChecked(True)

        if repeat_count > 1:
            self.grader_split_widget.repeat_yes_radio.setChecked(True)
            self.grader_split_widget.repeat_count_spin.setValue(repeat_count)
        else:
            self.grader_split_widget.repeat_no_radio.setChecked(True)

        # Load questions
        self.questions = metadata.get("questions", [])
        # Clear previous question list
        while self.question_list_layout.count():
            item = self.question_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        # Display detected questions
        for q in self.questions:
            label = QLabel(
                f"Q{q['question_id']}: {q['question_text']} "
                f"({q['question_type']})"
            )
            label.setWordWrap(True)
            self.question_list_layout.addWidget(label)

        self.question_summary_label.setText(
            f"Detected {len(self.questions)} grading questions"
        )

        # Update grading summary
        self.update_grading_summary()

    def update_source_study_path(self):
        """
        Update the source study path if the study name input changes.
        Should be called whenever self.study_name_input changes.
        """
        study_name = self.study_name_input.text().strip()
        if not study_name:
            return  # don't update if empty

        # Base admin studies folder
        admin_root = get_admin_studies_dir() 

        # Update source path
        self.source_study_path = admin_root / study_name


class GraderInputWidget(QWidget):
    graders_changed = pyqtSignal()
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Graders"))

        entry_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter grader name")
        self.add_button = QPushButton("Add")

        entry_layout.addWidget(self.name_input)
        entry_layout.addWidget(self.add_button)
        layout.addLayout(entry_layout)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        self.remove_button = QPushButton("Remove Selected")
        layout.addWidget(self.remove_button)

        self.add_button.clicked.connect(self.add_grader)
        self.remove_button.clicked.connect(self.remove_selected)

    def add_grader(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Name", "Grader name cannot be empty.")
            return

        existing = [
            self.list_widget.item(i).text()
            for i in range(self.list_widget.count())
        ]

        if name in existing:
            QMessageBox.warning(
                self,
                "Duplicate Grader",
                f"'{name}' is already added."
            )
            return

        self.list_widget.addItem(name)
        self.name_input.clear()

        # Signal for grader list change
        self.graders_changed.emit()

    def remove_selected(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(
                self.list_widget.row(item)
            )

        # Signal for grader list change
        self.graders_changed.emit()

    def get_graders(self):
        return [
            self.list_widget.item(i).text()
            for i in range(self.list_widget.count())
        ]


class GraderSplitWidget(QWidget):
    assignment_changed = pyqtSignal()
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        # LEFT SIDE: Grading assignment options
        # Set up the left side, with grading modes
        left_layout = QVBoxLayout()
        self.all_grade_all_radio = QRadioButton("All graders grade all images")
        self.split_radio = QRadioButton("Split images among graders")
        self.split_evenly_radio = QRadioButton("Split evenly")
        # Create button group to manage exclusivity
        self.assignment_group = QButtonGroup(self)
        self.assignment_group.addButton(self.all_grade_all_radio)
        self.assignment_group.addButton(self.split_radio)
        self.assignment_group.addButton(self.split_evenly_radio)
        # set defaults
        self.all_grade_all_radio.setChecked(True)
        self.split_evenly_radio.setEnabled(False)
        # Connect toggles and emit signals when changed
        # self.split_radio.toggled.connect(self.split_evenly_radio.setEnabled)
        # self.all_grade_all_radio.toggled.connect(self.assignment_changed.emit)
        # self.split_radio.toggled.connect(self.assignment_changed.emit)
        # Add to left side of HBox
        left_layout.addWidget(self.all_grade_all_radio)
        left_layout.addWidget(self.split_radio)
        left_layout.addWidget(self.split_evenly_radio)

        # RIGHT SIDE: Repeat options
        # Set up the right side, with repeat options for intra-rater reliability
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Repeat images per grader?"))
        self.repeat_no_radio = QRadioButton("No")
        self.repeat_yes_radio = QRadioButton("Yes")
        self.repeat_no_radio.setChecked(True) # set default
        # Put repeat radios in a button group
        self.repeat_group = QButtonGroup(self)
        self.repeat_group.addButton(self.repeat_no_radio)
        self.repeat_group.addButton(self.repeat_yes_radio)
        # Add to right side of HBox
        right_layout.addWidget(self.repeat_no_radio)
        right_layout.addWidget(self.repeat_yes_radio)
        # Add repeat count box
        self.repeat_count_label = QLabel("Number of times each image should be shown:")
        self.repeat_count_spin = QSpinBox()
        self.repeat_count_spin.setMinimum(2)
        self.repeat_count_spin.setMaximum(10)
        self.repeat_count_spin.setValue(2)
        self.repeat_count_label.setEnabled(False)
        self.repeat_count_spin.setEnabled(False)
        # Add to right side of HBox
        right_layout.addWidget(self.repeat_count_label)
        right_layout.addWidget(self.repeat_count_spin)
        # Enable repeats if user selects yes
        self.repeat_yes_radio.toggled.connect(self.repeat_count_label.setEnabled)
        self.repeat_yes_radio.toggled.connect(self.repeat_count_spin.setEnabled)
        # Connect toggles and emit signals when changed
        # self.repeat_no_radio.toggled.connect(self.assignment_changed.emit)
        # self.repeat_yes_radio.toggled.connect(self.assignment_changed.emit)
        # self.repeat_count_spin.valueChanged.connect(self.assignment_changed.emit)

        # COMBINE
        # Wiring
        self.split_radio.toggled.connect(lambda checked: (
            self.split_evenly_radio.setEnabled(checked),
            self.assignment_changed.emit()
        ))
        self.all_grade_all_radio.toggled.connect(self.assignment_changed.emit)

        self.repeat_yes_radio.toggled.connect(lambda checked: (
            self.repeat_count_spin.setEnabled(checked),
            self.assignment_changed.emit()
        ))
        self.repeat_no_radio.toggled.connect(self.assignment_changed.emit)

        self.repeat_count_spin.valueChanged.connect(self.assignment_changed.emit)
        # Add left and right layouts to main horizontal layout
        layout.addLayout(left_layout)
        layout.addSpacing(40)
        layout.addLayout(right_layout)


    def get_assignment_mode(self):
        return {
            "mode": (
                "all_graders_all_images"
                if self.all_grade_all_radio.isChecked()
                else "split_evenly"
            ),
            "repeat": self.repeat_yes_radio.isChecked(),
            "repeat_count": (
                self.repeat_count_spin.value()
                if self.repeat_yes_radio.isChecked()
                else 1
            )
        }