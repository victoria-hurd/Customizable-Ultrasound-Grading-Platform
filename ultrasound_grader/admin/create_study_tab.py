from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFileDialog, QLineEdit,
                             QScrollArea, QGroupBox, QMessageBox,
                             QListWidget, QRadioButton, QSpinBox)
from PyQt6.QtCore import pyqtSignal
from data.schema import load_question_schema
import os

# Create the study building tab for admin users
class CreateStudyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.questions = []
        self._build_ui()

    def _build_ui(self):
        outer_layout = QVBoxLayout()
        content_layout = QVBoxLayout()

        # get info about the study being created (name, data folder)
        study_box = QGroupBox("Study Information")
        study_layout = QVBoxLayout()

        self.study_name_input = QLineEdit()
        self.study_name_input.setPlaceholderText("Enter study name")

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
        self.grader_widget.graders_changed.connect(
        self.update_grading_summary
        )
        grader_box.setLayout(grader_layout)

        # Add the grader split and assignment info
        split_box = QGroupBox("Grading Assignment")
        split_layout = QVBoxLayout()
        self.grader_split_widget = GraderSplitWidget()
        split_layout.addWidget(self.grader_split_widget)
        self.grader_split_widget.assignment_changed.connect(
            self.update_grading_summary
        )
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
        # get grader assignments from inputs
        assignment_settings = self.grader_split_widget.get_assignment_mode()

        # temporary
        QMessageBox.information(
            self,
            "Create Study",
            "TBD WORKFLOWWWW"
        )

    def _count_media_files(self):
        folder = self.image_folder_label.text()
        if not os.path.isdir(folder):
            return 0

        valid_exts = {".mp4", ".avi", ".mov", ".mkv", ".jpg", ".png"}
        return sum(
            1 for f in os.listdir(folder)
            if os.path.splitext(f)[1].lower() in valid_exts
        )
    
    # Live-update the grading summary based on current inputs
    def update_grading_summary(self):
        num_files = self._count_media_files()
        graders = self.grader_widget.get_graders()
        num_graders = len(graders)

        self.detected_files_label.setText(
            f"Detected files: {num_files}"
        )

        if num_files == 0 or num_graders == 0:
            self.per_grader_label.setText(
                "Each grader will review: —"
            )
            return

        assignment = self.grader_split_widget.get_assignment_mode()

        repeat_multiplier = assignment["repeat_count"]

        if assignment["mode"] == "all_graders_all_images":
            per_grader = num_files
            mode_text = "All graders grade all images"
        else:
            per_grader = num_files // num_graders
            remainder = num_files % num_graders
            mode_text = "Split evenly"
            if remainder:
                mode_text += f" (+{remainder} distributed)"

        per_grader *= repeat_multiplier

        if assignment["repeat"]:
            mode_text += f", repeated {repeat_multiplier}×"

        self.per_grader_label.setText(
            f"Each grader will review: {per_grader} ({mode_text})"
        )


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

        layout = QVBoxLayout(self)

        # Button creation
        self.all_grade_all_radio = QRadioButton(
            "All graders grade all images"
        )
        self.split_radio = QRadioButton(
            "Split images among graders"
        )
        self.split_evenly_radio = QRadioButton(
            "Split evenly"
        )

        # set defaults
        self.all_grade_all_radio.setChecked(True)
        self.split_evenly_radio.setEnabled(False)

        # emit signals when toggled to update the live summary
        self.split_radio.toggled.connect(
            self.split_evenly_radio.setEnabled
        )

        self.all_grade_all_radio.toggled.connect(
            self.assignment_changed.emit
        )
        self.split_radio.toggled.connect(
            self.assignment_changed.emit
        )

        # Add widgets to layout
        layout.addWidget(self.all_grade_all_radio)
        layout.addWidget(self.split_radio)
        layout.addWidget(self.split_evenly_radio)

        # Add repeats for intra-rater reliability studies
        layout.addSpacing(10)
        layout.addWidget(QLabel("Repeat images per grader?"))

        self.repeat_no_radio = QRadioButton("No")
        self.repeat_yes_radio = QRadioButton("Yes")
        self.repeat_no_radio.setChecked(True)

        layout.addWidget(self.repeat_no_radio)
        layout.addWidget(self.repeat_yes_radio)

        self.repeat_count_label = QLabel(
            "Number of times each image should be shown:"
        )
        self.repeat_count_spin = QSpinBox()
        self.repeat_count_spin.setMinimum(2)
        self.repeat_count_spin.setMaximum(10)
        self.repeat_count_spin.setValue(2)

        self.repeat_count_label.setEnabled(False)
        self.repeat_count_spin.setEnabled(False)

        layout.addWidget(self.repeat_count_label)
        layout.addWidget(self.repeat_count_spin)

        # Enable repeats if user selects yes
        self.repeat_yes_radio.toggled.connect(
            self.repeat_count_label.setEnabled
        )
        self.repeat_yes_radio.toggled.connect(
            self.repeat_count_spin.setEnabled
        )

        # Emit signals if repeats changed
        self.repeat_no_radio.toggled.connect(
            self.assignment_changed.emit
        )
        self.repeat_yes_radio.toggled.connect(
            self.assignment_changed.emit
        )
        self.repeat_count_spin.valueChanged.connect(
            self.assignment_changed.emit
        )

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