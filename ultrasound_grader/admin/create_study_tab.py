from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFileDialog, QLineEdit,
                             QScrollArea, QGroupBox, QMessageBox)
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

        content_layout.addWidget(study_box)
        content_layout.addWidget(question_box)
        content_layout.addStretch()

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
            QMessageBox.information(
                self,
                "Create Study",
                "TBD WORKFLOWWWW"
            )
