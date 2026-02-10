import os
from PyQt6.QtWidgets import (QHBoxLayout, QListWidgetItem, QScrollArea, 
    QWidget, QVBoxLayout, QLabel, QMessageBox, QListWidget,QApplication,
    QPushButton, QFileDialog, QTableWidget, QHeaderView, QTableWidgetItem)
from PyQt6.QtCore import Qt
from pathlib import Path
from json import load as json_load
from shutil import copy as shutil_copy
from pandas import read_csv as pd_read_csv, concat as pd_concat

class ReviewResultsWindow(QWidget):
    def __init__(self, study_path, parent_window=None):
        super().__init__()
        self.study_path = study_path
        self.parent_window = parent_window
        self.showMaximized()
        self.study_path = study_path
        self.setWindowTitle("Review Study Results")

        self.layout_main = QVBoxLayout(self)
        self.setLayout(self.layout_main)

        # ---------------- Metadata Display ----------------
        metadata_path = os.path.join(study_path, "study_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                metadata = json_load(f)
            
            self.study_name = metadata['study_name']
            self.questions = metadata['questions']
            self.graders = metadata['graders']
            metadata_label = QLabel()
            text = (
            f"<b>Study Name:</b> {self.study_name}<br>"
            f"<b>Assignment Mode:</b> {metadata['assignment_mode']}<br>"
            f"<b>Repeat Count:</b> {metadata['repeat_count']}<br>"
            f"<b>Graders:</b> {', '.join(self.graders)}<br>"
            f"<b>Questions:</b> {len(self.questions)}"
        )

            metadata_label.setText(text)
            metadata_label.setWordWrap(True)
            self.layout_main.addWidget(metadata_label)
        else:
            metadata = {}

        # ---------------- Grader Files Widget ----------------
        self.grader_files_widget = GraderFileWidget(study_path)
        self.layout_main.addWidget(self.grader_files_widget)

        # ---------------- Analyze Data Button ----------------
        self.analyze_btn = QPushButton("Analyze Data")
        self.analyze_btn.clicked.connect(self.analyze_data)
        self.layout_main.addWidget(self.analyze_btn)

        # ---------------- Summary Area ----------------
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(2)  # Question | Breakdown
        self.summary_table.setHorizontalHeaderLabels(["Question", "Option Breakdown"])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Make table scrollable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.summary_table)
        self.layout_main.addWidget(scroll_area)

        # ---------------- Download Button ----------------
        self.download_btn = QPushButton("Download Concatenated Results")
        self.download_btn.setVisible(False)
        self.download_btn.clicked.connect(self.download_concatenated_results)
        self.layout_main.addWidget(self.download_btn)

        # ---------------- Post Review Buttons ----------------
        self.back_btn = QPushButton("Back to Admin Landing")
        self.exit_btn = QPushButton("Exit Application")
        self.back_btn.clicked.connect(self.go_back_to_admin)
        self.exit_btn.clicked.connect(QApplication.instance().quit)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.back_btn)
        button_layout.addWidget(self.exit_btn)
        self.layout_main.addLayout(button_layout)

    def analyze_data(self):
        grader_files_dir = os.path.join(self.study_path, "Results", "Grader Files")
        files = [
            os.path.join(grader_files_dir, f)
            for f in os.listdir(grader_files_dir)
            if f.endswith(".csv")
        ]

        if not files:
            QMessageBox.warning(self, "No Files", "No grader files found to analyze.")
            return

        # Concatenate all grader files and store for download
        all_dfs = [pd_read_csv(f) for f in files]
        df_all = pd_concat(all_dfs, ignore_index=True)
        self.concat_df = df_all  # store in self for download

        # generate question column names from metadata
        q_cols = [q['question_text'] for q in self.questions]

        if not q_cols:
            QMessageBox.information(self, "No Questions", 
                "Error concatenating - differing questions in gradesheets from study metadata.")
            return

        # Update summary table: 2 columns only
        self.summary_table.setColumnCount(2)
        self.summary_table.setHorizontalHeaderLabels(["Question", "Option Breakdown"])
        self.summary_table.setRowCount(len(q_cols))

        for i, q_col in enumerate(q_cols):
            # Get options from metadata
            q_meta = next((q for q in self.questions if q['question_text'] == q_col), None)
            if q_meta:
                options = q_meta["options"]
            else:
                options = list(df_all[q_col].dropna().unique())  # fallback

            # Count percent of users choosing each option
            answers = df_all[q_col].dropna()
            counts = answers.value_counts(normalize=True) * 100
            breakdown_lines = [f"{opt}: {counts.get(opt, 0.0):.1f}%" for opt in options]
            breakdown = "\n".join(breakdown_lines)

            # ---------------- Populate Table ----------------
            q_item = QTableWidgetItem(q_col)
            q_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.summary_table.setItem(i, 0, q_item)

            breakdown_item = QTableWidgetItem(breakdown)
            breakdown_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            breakdown_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            breakdown_item.setToolTip(breakdown)  # tooltip for long breakdowns
            breakdown_item.setData(Qt.ItemDataRole.DisplayRole, breakdown)
            self.summary_table.setItem(i, 1, breakdown_item)

            # Adjust row height to fit text
            self.summary_table.setRowHeight(i, max(50, 20 * len(breakdown_lines)))

        self.download_btn.setVisible(True)

    def download_concatenated_results(self):
        # Save the concatenated results to the user's Downloads folder
        home = str(Path.home())
        downloads = os.path.join(home, "Downloads")
        if not os.path.exists(downloads):
            os.makedirs(downloads)
        output_path = os.path.join(downloads, f"{self.study_name}_concatenated_results.xlsx")

        self.concat_df.to_excel(output_path, index=False)
        QMessageBox.information(self, "Saved", f"Concatenated results saved to:\n{output_path}")

    def go_back_to_admin(self):
        if self.parent_window:
            self.parent_window.show()  # show the admin landing page
        self.close()  # Close the current page

class GraderFileWidget(QWidget):
    def __init__(self, study_path):
        super().__init__()
        self.study_path = study_path
        self.grader_dir = os.path.join(self.study_path, "Results", "Grader Files")
        os.makedirs(self.grader_dir, exist_ok=True)

        self.layout = QVBoxLayout(self)

        # List of current grader files
        self.file_list = QListWidget()
        self.layout.addWidget(self.file_list)

        # Buttons
        self.btn_layout = QHBoxLayout()
        self.load_btn = QPushButton("Add Grader Files")
        self.delete_btn = QPushButton("Delete Selected File")
        self.btn_layout.addWidget(self.load_btn)
        self.btn_layout.addWidget(self.delete_btn)
        self.layout.addLayout(self.btn_layout)

        # Connect signals
        self.load_btn.clicked.connect(self.add_grader_files)
        self.delete_btn.clicked.connect(self.delete_selected_file)

        # Initial population
        self.populate_file_list()

    def populate_file_list(self):
        """Load current files from Grader Files folder"""
        self.file_list.clear()
        for fname in sorted(os.listdir(self.grader_dir)):
            if fname.endswith(".csv"):
                item = QListWidgetItem(fname)
                self.file_list.addItem(item)

    def add_grader_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Grader Files",
            "",
            "CSV Files (*.csv)"
        )
        if not files:
            return

        # Try/Except block for filesystem operations
        try:
            # Copy selected files into Grader Files folder
            for f in files:
                dest = os.path.join(self.grader_dir, os.path.basename(f))
                shutil_copy(f, dest)

            self.populate_file_list()

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Add Grade Data Failed",
                f"An error occurred during add grade data:\n\n{e}"
            )
            return
    
    def delete_selected_file(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select a file to delete.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete the selected file(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        # Try/Except block for filesystem operations
        try:
            for item in selected_items:
                fname = item.text()
                path = os.path.join(self.grader_dir, fname)
                if os.path.exists(path):
                    os.remove(path)
                self.file_list.takeItem(self.file_list.row(item))
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Delete Grade Data Failed",
                f"An error occurred during delete grade data:\n\n{e}"
            )
            return