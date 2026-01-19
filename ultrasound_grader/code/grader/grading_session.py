import os
import pandas as pd
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QProgressBar, QRadioButton,
                             QButtonGroup, QSlider, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from grader.video_player import VideoPlayer
from ultrasound_grader.code.schema import load_question_schema


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

        # Exit button in top-left
        exit_layout = QHBoxLayout()
        self.exit_btn = QPushButton("Exit Grading")
        self.exit_btn.clicked.connect(self.confirm_exit)
        exit_layout.addWidget(self.exit_btn)
        exit_layout.addStretch()
        video_container.addLayout(exit_layout)

        # Video player
        self.video_player = VideoPlayer()
        video_container.addWidget(self.video_player)

        # Video controls
        controls_layout = QHBoxLayout()
        self.play_btn = QPushButton("Play")
        self.pause_btn = QPushButton("Pause")
        self.next_btn = QPushButton("Save Grades and Advance to Next Video")
        self.next_btn.clicked.connect(self.save_and_next)

        # Connect play/pause buttons
        self.play_btn.clicked.connect(self.video_player.play)
        self.pause_btn.clicked.connect(self.video_player.pause)

        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.pause_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.next_btn)
        video_container.addLayout(controls_layout)

        # Scrubbing slider
        self.scrub_slider = QSlider(Qt.Orientation.Horizontal)
        self.scrub_slider.setMinimum(0)
        self.scrub_slider.setMaximum(100)  # We'll update dynamically based on video length
        video_container.addWidget(self.scrub_slider)
        self.video_player.set_slider(self.scrub_slider)
        #self.scrub_slider.sliderMoved.connect(self.scrub_video)
        self.scrub_slider.valueChanged.connect(self.scrub_video)

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

        grading_layout.addLayout(question_container, stretch=1)  # Take 1/4 of horizontal space

        self.grading_widget.setVisible(False)
        self.layout_main.addWidget(self.grading_widget)

    # ---------------- Welcome Functions ----------------
    def select_study_folder(self):

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

        # Load grader CSV
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

        # Determine grader name
        self.grader_name = os.path.splitext(csv_files[0])[0].replace("_questions", "")

        # Map schema questions to CSV columns using question_id as "Q{ID}"
        csv_cols = self.grader_df.columns.tolist()
        question_cols = []
        for q in self.questions:
            col_name = f"Q{q['question_id']}"
            if col_name in csv_cols:
                question_cols.append(col_name)
            else:
                print(f"Warning: Column '{col_name}' not found in CSV")

        if not question_cols:
            QMessageBox.warning(self, "No Question Columns", "Could not find any matching question columns in CSV.")
            return

        # Count empty rows and remaining reviews
        empty_rows = self.grader_df[question_cols].isna().all(axis=1).sum()
        remaining = self.grader_df[question_cols].isna().any(axis=1).sum()

        if empty_rows == len(self.grader_df):
            progress_text = "You haven't started grading yet."
        else:
            progress_text = f"You've already begun grading. You have {remaining} reviews remaining."

        # Update label
        self.grader_info_label.setText(
            f"Grader: {self.grader_name}\nTotal reviews assigned: {len(self.grader_df)}\n{progress_text}"
        )

        # Enable start button
        self.start_btn.setEnabled(True)
        self.question_cols = question_cols

    # ---------------- Grading Functions ----------------
    def show_grading_ui(self):
        self.welcome_widget.setVisible(False)
        self.grading_widget.setVisible(True)
        self.current_index = self.grader_df[self.question_cols].isna().any(axis=1).idxmax()
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
            # Question label
            q_label = QLabel(f"{q['question_text']} ({q['question_type']})")
            q_label.setWordWrap(True)  # wrap text
            q_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            self.question_layout.addWidget(q_label)

            if q['question_type'] == "Single Select":
                btn_group = QButtonGroup(self)
                btn_layout = QVBoxLayout()  # use vertical layout to left-align

                for option in q['options']:
                    rb = QRadioButton(option)
                    rb.setStyleSheet("text-align: left;")  # ensure left alignment
                    btn_group.addButton(rb)
                    btn_layout.addWidget(rb)

                self.question_layout.addLayout(btn_layout)
                self.radio_groups.append((q['question_text'], btn_group))

            elif q['question_type'] == "Annotation":
                # Placeholder for annotation widget (later will use coordinate click widget)
                placeholder = QLabel("[Annotation widget placeholder]")
                placeholder.setStyleSheet("border: 1px solid black; padding: 5px;")
                self.question_layout.addWidget(placeholder)
                self.radio_groups.append((q['question_text'], None))


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

        # Save answers into the grader_df
        for q_text, answer in row_answers.items():
            if q_text in self.grader_df.columns:
                self.grader_df.at[row_index, q_text] = answer
            else:
                # If the column doesn't exist, add it
                self.grader_df[q_text] = ""
                self.grader_df.at[row_index, q_text] = answer

        self.answers[row_index] = row_answers  # optional, still keep for tracking
        self.current_index += 1
        self.progress_bar.setValue(self.current_index)

        if self.current_index >= len(self.grader_df):
            # Save the entire DataFrame back to CSV
            save_path = os.path.join(self.study_folder, f"{self.grader_name}_questions.csv")
            self.grader_df.to_csv(save_path, index=False)
            QMessageBox.information(self, "Grading Complete", "All reviews completed! Answers saved.")
            self.exit_grading()
        else:
            self.load_current_video()

    # ---------------- Video Scrubbing ----------------
    def scrub_video(self):
        if hasattr(self.video_player, 'seek'):
            pos_percent = self.scrub_slider.value() / 100
            self.video_player.seek(pos_percent)

    # ---------------- Exit Grading ----------------
    def confirm_exit(self):
        reply = QMessageBox.question(
            self,
            "Confirm Exit",
            "Are you sure you want to exit? Your progress up until this video will be saved.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.exit_grading()

    def exit_grading(self):
        save_path = os.path.join(self.study_folder, f"{self.grader_name}_answers.csv")
        df_answers = pd.DataFrame.from_dict(self.answers, orient="index")
        df_answers.to_csv(save_path, index=False)
        self.parentWidget().close()
