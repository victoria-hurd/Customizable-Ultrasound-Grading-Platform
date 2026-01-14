import os
import pandas as pd
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QProgressBar, QRadioButton,
                             QButtonGroup, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from grader.video_player import VideoPlayer
from data.schema import load_question_schema

class GradingSessionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.study_folder = None
        self.grader_name = None
        self.grader_df = None
        self.questions = []
        self.current_index = 0
        self.answers = {}

        self._build_ui()

    def _build_ui(self):
        self.layout_main = QVBoxLayout(self)
        self.setLayout(self.layout_main)

        # ---------------- Welcome Section ----------------
        self.welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_widget)

        # Folder selection
        folder_layout = QHBoxLayout()
        self.folder_label = QLabel("No study folder selected")
        folder_btn = QPushButton("Select Study Folder")
        folder_btn.clicked.connect(self.select_study_folder)
        folder_layout.addWidget(folder_btn)
        folder_layout.addWidget(self.folder_label)
        welcome_layout.addLayout(folder_layout)

        # Grader info
        self.grader_info_label = QLabel("")
        self.grader_info_label.setWordWrap(True)
        welcome_layout.addWidget(self.grader_info_label)

        # Instructions placeholder
        self.instructions_label = QLabel("Instructions placeholder: fill in later.")
        self.instructions_label.setWordWrap(True)
        welcome_layout.addWidget(self.instructions_label)

        # Start grading button
        self.start_btn = QPushButton("Start Grading")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.show_grading_ui)
        welcome_layout.addWidget(self.start_btn)

        self.layout_main.addWidget(self.welcome_widget)

        # ---------------- Grading Section ----------------
        self.grading_widget = QWidget()
        grading_layout = QHBoxLayout(self.grading_widget)  # Horizontal layout

        # -------- Left: Video player + controls --------
        video_container = QVBoxLayout()

        self.video_player = VideoPlayer()
        video_container.addWidget(self.video_player)

        # Play/Pause/Other controls
        controls_layout = QHBoxLayout()
        self.next_btn = QPushButton("Next Video")
        self.next_btn.clicked.connect(self.save_and_next)
        controls_layout.addStretch()
        controls_layout.addWidget(self.next_btn)
        video_container.addLayout(controls_layout)

        # Progress bar at the bottom of video container
        self.progress_bar = QProgressBar()
        video_container.addWidget(self.progress_bar)

        grading_layout.addLayout(video_container, stretch=3)  # Take 3/4 of horizontal space

        # -------- Right: Scrollable question area --------
        question_container = QVBoxLayout()
        self.question_layout = QVBoxLayout()  # Will hold question widgets

        scroll_widget = QWidget()
        scroll_widget.setLayout(self.question_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)

        question_container.addWidget(scroll_area)

        # Exit button at the bottom
        self.exit_btn = QPushButton("Exit Grading")
        self.exit_btn.clicked.connect(self.exit_grading)
        question_container.addWidget(self.exit_btn)

        grading_layout.addLayout(question_container, stretch=1)  # Take 1/4 of horizontal space

        self.grading_widget.setVisible(False)
        self.layout_main.addWidget(self.grading_widget)

    # ---------------- Welcome Functions ----------------
    def select_study_folder(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import os, pandas as pd

        folder = QFileDialog.getExistingDirectory(self, "Select Study Folder")
        if not folder:
            return

        self.study_folder = folder
        self.folder_label.setText(folder)

        # Load demoGradeSheet.xlsx from folder
        questions_path = os.path.join(folder, "demoGradeSheet.xlsx")
        try:
            self.questions = load_question_schema(questions_path)
        except Exception as e:
            QMessageBox.critical(self, "Question Load Error", str(e))
            return

        # Update grader info from their master
        csv_files = [f for f in os.listdir(folder) if f.endswith("_questions.csv")]
        if not csv_files:
            QMessageBox.warning(self, "No CSV Found", "No grader CSV found in this folder.")
            return

        csv_path = os.path.join(folder, csv_files[0])
        try:
            self.grader_df = pd.read_csv(csv_path)
        except Exception as e:
            QMessageBox.critical(self, "CSV Load Error", str(e))
            return

        num_reviews = len(self.grader_df)
        self.grader_name = os.path.splitext(csv_files[0])[0].replace("_questions", "")
        self.grader_info_label.setText(
            f"Grader: {self.grader_name}\nNumber of reviews assigned: {num_reviews}"
        )

        self.start_btn.setEnabled(True)

    # ---------------- Grading Functions ----------------
    def show_grading_ui(self):
        self.welcome_widget.setVisible(False)
        self.grading_widget.setVisible(True)
        self.current_index = 0
        self.progress_bar.setMaximum(len(self.grader_df))
        self.load_current_video()

    def load_current_video(self):
        import os
        from PyQt6.QtWidgets import QMessageBox

        # Clear previous questions
        while self.question_layout.count():
            item = self.question_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        row = self.grader_df.iloc[self.current_index]
        video_path = os.path.join(self.study_folder, "Raw Data", row["deidentified_filename"])
        if not os.path.exists(video_path):
            QMessageBox.warning(self, "Video Missing", f"Video not found: {video_path}")
            return

        self.video_player.load_video(video_path)

        # Dynamically create questions from schema
        self.radio_groups = []
        for q in self.questions:
            q_label = QLabel(f"{q['question_text']} ({q['question_type']})")
            q_label.setWordWrap(True)
            self.question_layout.addWidget(q_label)

            if q['question_type'] == "Single Select":
                btn_group = QButtonGroup(self)
                btn_layout = QHBoxLayout()
                for option in q['options']:
                    rb = QRadioButton(option)
                    btn_group.addButton(rb)
                    btn_layout.addWidget(rb)
                self.question_layout.addLayout(btn_layout)
                self.radio_groups.append((q['question_text'], btn_group))

            elif q['question_type'] == "Annotation":
                # Placeholder for annotation widget (later will use coordinate click widget)
                placeholder = QLabel("[Annotation widget placeholder]")
                placeholder.setStyleSheet("border: 1px solid black; padding: 5px;")
                self.question_layout.addWidget(placeholder)
                self.radio_groups.append((q['question_text'], None))  # None for now


        self.progress_bar.setValue(self.current_index)

    def save_and_next(self):
        row_index = self.current_index
        row_answers = {}
        for q_text, btn_group in self.radio_groups:
            if btn_group is None:
                continue  # Skip Annotation for now
            selected = btn_group.checkedButton()
            if selected:
                row_answers[q_text] = selected.text()
            else:
                QMessageBox.warning(self, "Answer Required", f"You must answer {q_text} before moving on.")
                return

        self.answers[row_index] = row_answers
        self.current_index += 1
        self.progress_bar.setValue(self.current_index)

        if self.current_index >= len(self.grader_df):
            QMessageBox.information(self, "Grading Complete", "All reviews completed!")
            self.exit_grading()
        else:
            self.load_current_video()

    def exit_grading(self):
        import os, pandas as pd
        save_path = os.path.join(self.study_folder, f"{self.grader_name}_answers.csv")
        df_answers = pd.DataFrame.from_dict(self.answers, orient="index")
        df_answers.to_csv(save_path, index=False)
        self.parentWidget().close()
