import os
from pathlib import Path
from PyQt6.QtCore import Qt
from pandas import read_csv as pd_read_csv
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QProgressBar, 
                             QRadioButton, QButtonGroup, QSlider, 
                             QMessageBox, QApplication)

from code.grader.video_player import VideoPlayer
from code.utils.app_paths import move_without_overwrite,get_app_support_resources_dir

class GradingSessionTab(QWidget):
    def __init__(self,
                 loaded_metadata,
                 current_study_path,
                 grader_name,
                 parent_window=None):
        super().__init__()
        self.showMaximized()
        self.parent_window = parent_window
        self.study_name = loaded_metadata['study_name']
        self.study_folder = current_study_path
        self.grader_name = grader_name
        self.questions = loaded_metadata['questions']
        self.current_index = 0
        output_dir = os.path.join(self.study_folder, "Output Grade Data")
        self.grade_data_path = os.path.join(output_dir, f"{self.grader_name}_{self.study_name}_grade_data.csv")
        self.grade_df = pd_read_csv(self.grade_data_path)
        # Convert all columns to string type (object dtype in older pandas versions)
        #self.grade_df = self.grade_df.astype(str)
        self.answers = {}

        self._build_ui()

    def _build_ui(self):
        self.layout_main = QVBoxLayout(self)
        self.setLayout(self.layout_main)

        # ---------------- Welcome Section ----------------
        self.welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_widget)
        # Count total and completed reviews
        total_reviews = len(self.grade_df)
        # generate question column names
        self.q_cols = []
        for q in self.questions:
            # Question label
            self.q_cols.append(f"{q['question_text']}")
        total_reviews = len(self.grade_df)
        completed_reviews = total_reviews - sum(self.grade_df[self.q_cols].isna().any(axis=1))
        self.current_index = completed_reviews
        study_info_label = QLabel()

        # Metadata display
        study_info_label = QLabel()
        text = (
            "<b>Grading Session Summary</b>\n"
            f"<b>Study Name:</b> {self.study_name}<br>"
            f"<b>Grader Name:</b> {self.grader_name}<br>"
            f"<b>Total Number of Reviews Assigned to You:</b> {total_reviews}<br>"
            f"<b>Reviews Completed So Far:</b> {completed_reviews}<br>"
            f"<b>Questions per Review:</b> {len(self.questions)}"
            )

        study_info_label.setText(text)
        study_info_label.setWordWrap(True)
        welcome_layout.addWidget(study_info_label)

        # Grader Instructions display
        grader_instruction_label = QLabel("<b>Grader Instructions:</b>\n\n")
        root = get_app_support_resources_dir()
        instructions_location = os.path.join(root, "grader_instructions.txt")
        with open(instructions_location) as f:
            instructions = f.read()
        instructions_label = QLabel(instructions)
        instructions_label.setWordWrap(True)
        welcome_layout.addWidget(grader_instruction_label)
        welcome_layout.addWidget(instructions_label)

        # Action buttons
        action_bar = QHBoxLayout()
        action_bar.addStretch()
        back_btn = QPushButton("Back to Grader Landing")
        back_btn.clicked.connect(self.go_back_to_grader_landing)
        start_btn = QPushButton("Start Grading")
        start_btn.clicked.connect(self.show_grading_ui)
        action_bar.addWidget(back_btn)
        action_bar.addWidget(start_btn)
        welcome_layout.addLayout(action_bar)

        welcome_layout.addStretch()

        self.layout_main.addWidget(self.welcome_widget)

        # ---------------- Grading Section ----------------
        self.grading_widget = QWidget()
        grading_layout = QHBoxLayout(self.grading_widget)  # Horizontal layout

        # -------- Left: Video player + controls --------
        video_container = QVBoxLayout()

        # Exit button in top-left
        exit_layout = QHBoxLayout()
        back_btn_2 = QPushButton("Back to Grader Landing")
        back_btn_2.clicked.connect(self.go_back_to_grader_landing)
        exit_btn = QPushButton("Exit Grading")
        exit_btn.clicked.connect(self.exit_grading)
        exit_layout.addWidget(back_btn_2)
        exit_layout.addWidget(exit_btn)
        exit_layout.addStretch()
        video_container.addLayout(exit_layout)

        # Video player
        self.video_player = VideoPlayer()
        video_container.addWidget(self.video_player,stretch=3)

        # Video controls
        controls_layout = QHBoxLayout()
        self.play_btn = QPushButton("Play")
        self.pause_btn = QPushButton("Pause")
        self.next_btn = QPushButton("Save Grades and Advance to Next Video")
        self.next_btn.clicked.connect(self.save_and_next)

        # Connect play/pause buttons
        self.play_btn.clicked.connect(self.video_player.play)
        self.pause_btn.clicked.connect(self.video_player.pause)

        controls_layout.addStretch()
        controls_layout.addWidget(self.play_btn)
        controls_layout.addWidget(self.pause_btn)
        controls_layout.addStretch()
        controls_layout.addWidget(self.next_btn)
        video_container.addLayout(controls_layout)

        # Scrubbing slider
        self.scrub_slider = QSlider(Qt.Orientation.Horizontal)
        self.scrub_slider.setMinimum(0)
        #self.scrub_slider.setMaximum(100)  # We'll update dynamically based on video length
        video_container.addWidget(self.scrub_slider)
        self.video_player.set_slider(self.scrub_slider)

        # Progress bar at the bottom of video container
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel(f"Video {self.current_index+1} of {len(self.grade_df)}")
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_label)
        video_container.addLayout(progress_layout)

        grading_layout.addLayout(video_container, stretch=3)  # Take 3/4 of horizontal space

        # -------- Right: Scrollable question area --------
        question_container = QVBoxLayout()
        self.question_layout = QVBoxLayout()  # Will hold question widgets

        scroll_widget = QWidget()
        scroll_widget.setLayout(self.question_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        question_container.addWidget(scroll_area)

        grading_layout.addLayout(question_container, stretch=1)  # Take 1/4 of horizontal space

        self.grading_widget.setVisible(False)
        self.layout_main.addWidget(self.grading_widget)

        # ---------------- Post-Grading Section ----------------
        self.post_grading_widget = QWidget()
        post_grading_layout = QVBoxLayout(self.post_grading_widget)

        # Post-Grading Panel with Instructions and Exit
        end_session_label = QLabel("<b>Grading Session Complete</b>\n\n")
        root = get_app_support_resources_dir()
        end_session_instructions_location = os.path.join(root, "session_end_instructions.txt")
        with open(end_session_instructions_location) as f:
            end_session_instructions = f.read()
        end_session_instructions_label = QLabel(end_session_instructions)
        end_session_instructions_label.setWordWrap(True)
        post_grading_layout.addWidget(end_session_label)
        post_grading_layout.addWidget(end_session_instructions_label)

        # Download data button
        download_box = QHBoxLayout()
        download_btn = QPushButton("Download Graded Data CSV")
        download_btn.clicked.connect(self.download_graded_data)
        download_box.addWidget(download_btn)
        download_box.addStretch()
        post_grading_layout.addLayout(download_box)
        post_grading_layout.addSpacing(20)

        # Exit action buttons
        action_bar_post = QHBoxLayout()
        action_bar_post.addStretch()
        back_btn_3 = QPushButton("Back to Grader Landing")
        back_btn_3.clicked.connect(self.go_back_to_grader_landing)
        exit_btn_2 = QPushButton("Exit Application")
        exit_btn_2.clicked.connect(self.confirm_exit)
        action_bar_post.addWidget(back_btn_3)
        action_bar_post.addWidget(exit_btn_2)
        post_grading_layout.addLayout(action_bar_post)
        post_grading_layout.addStretch()

        self.post_grading_widget.setVisible(False)
        self.layout_main.addWidget(self.post_grading_widget)


    # ---------------- Grading Functions ----------------
    def show_grading_ui(self):
        self.showMaximized()
        self.welcome_widget.setVisible(False)
        self.grading_widget.setVisible(True)
        # generate question column names
        #self.current_index = self.grade_df[self.q_cols].isna().any(axis=1).idxmax()
        #self.current_index = self.grade_df.dropna(subset=self.q_cols).shape[0]
        print("Current index for grading:", self.current_index)
        print("Grade DataFrame shape:", self.grade_df.shape)
        print("Grade DataFrame columns:", self.grade_df.columns)
        print("Grade DataFrame head:\n", self.grade_df.head())
        self.progress_bar.setMaximum(len(self.grade_df))
        self.load_current_video()

    def load_current_video(self):

        # Clear previous radio selections, if they exist
        if hasattr(self, "radio_groups"):
            for _, group in self.radio_groups:
                if group is not None:
                    group.setExclusive(False)
                    for btn in group.buttons():
                        btn.setChecked(False)
                    group.setExclusive(True)

        # Clear previous questions
        while self.question_layout.count():
            item = self.question_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub_item = item.layout().takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
                item.layout().deleteLater()

        row = self.grade_df.iloc[self.current_index]
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

        self.question_layout.addStretch()
        self.progress_bar.setValue(self.current_index)
        self.progress_label.setText(f"Video {self.current_index+1} of {len(self.grade_df)}")

    def save_and_next(self):
        row_index = self.current_index
    # Collect answers
        for q_id, btn_group in self.radio_groups:
            if btn_group is None:
                continue  # Annotation later

            selected = btn_group.checkedButton()
            if not selected:
                QMessageBox.warning(
                    self,
                    "Answer Required",
                    f"You must answer {q_id} before continuing."
                )
                return

            # Write directly into the existing column
            self.grade_df.at[row_index, q_id] = str(selected.text())

        # Try/Except block for filesystem operations
        try:
            self.grade_df.to_csv(self.grade_data_path, index=False)
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Grade Data Save Failed",
                f"An error occurred during graded data save:\n\n{e}"
            )
            return

        # Advance
        self.current_index += 1
        self.progress_bar.setValue(self.current_index)
        self.progress_label.setText(f"Video {self.current_index+1} of {len(self.grade_df)}")

        if self.current_index >= len(self.grade_df):
            # If grading is complete, show post-grading UI
            self.show_post_ui()
        else:
            # Otherwise, clear items and load next video
            #self.clear_button_groups()
            self.load_current_video()

    # ---------------- Exit Grading ----------------
    def show_post_ui(self):
        self.showMaximized()
        self.grading_widget.setVisible(False)
        self.post_grading_widget.setVisible(True)

    def download_graded_data(self):
        downloads_folder = str(Path.home() / "Downloads")
        move_without_overwrite(self.grade_data_path, downloads_folder, mode='copy')
        QMessageBox.information(self, "Download Complete", f"Grades copied to {downloads_folder}")

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
        QApplication.instance().quit()

    def go_back_to_grader_landing(self):
        if self.parent_window:
            self.parent_window.show()  # show the grader landing page
        self.close()

    def clear_button_groups(self):
        # Unselect previous questions
        for btn_group in self.radio_groups:
            print(btn_group)
            btn_group = QButtonGroup(btn_group)
            print(btn_group)
            if btn_group is None:
                continue  # Annotation later
            # Temporarily disable exclusivity
            btn_group.setExclusive(False)
            # Uncheck checked button
            checked_button = btn_group.checkedButton()
            if checked_button:
                checked_button.setChecked(False)
            # Re-enable
            btn_group.setExclusive(True)