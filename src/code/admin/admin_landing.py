import os
from pathlib import Path
from shutil import rmtree as shutil_rmtree
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget, 
                             QPushButton, QMessageBox, QHBoxLayout, 
                             QApplication)
from code.utils.app_paths import get_admin_studies_dir, reveal_in_finder
from code.admin.create_study_tab import CreateStudyTab
from code.admin.results_review import ReviewResultsWindow

class AdminLanding(QWidget):
    def __init__(self,
        parent_window=None):
        super().__init__()
        self.setWindowTitle("Admin: Studies")
        self.parent_window = parent_window

        layout = QVBoxLayout(self)

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
        action_bar.addStretch()
        action_bar.addWidget(refresh_btn)
        
        layout.addLayout(action_bar)

        # ---------------- Admin Functions ----------------

        layout.addWidget(QLabel("Existing Studies"))

        self.study_list = QListWidget()
        layout.addWidget(self.study_list)

        self.refresh_studies()

        btn_layout = QVBoxLayout()

        self.create_btn = QPushButton("Create New Study")
        self.edit_btn = QPushButton("Edit Selected Study")
        self.results_btn = QPushButton("Review Results for Selected Study")
        self.show_finder_btn = QPushButton("Show Stored Data in Finder for Selected Study")
        self.rm_study_btn = QPushButton("Delete Selected Study")

        self.create_btn.clicked.connect(self.create_new)
        self.edit_btn.clicked.connect(self.edit_selected)
        self.results_btn.clicked.connect(self.review_results)
        self.show_finder_btn.clicked.connect(self.on_reveal_clicked)
        self.rm_study_btn.clicked.connect(self.delete_study)

        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.results_btn)
        btn_layout.addWidget(self.show_finder_btn)
        btn_layout.addWidget(self.rm_study_btn)

        layout.addLayout(btn_layout)


    def refresh_studies(self):
        self.study_list.clear()
        admin_dir = get_admin_studies_dir()
        self.admin_studies_dir = str(admin_dir)

        studies = [p.name for p in admin_dir.iterdir() if p.is_dir()]
        self.study_list.addItems(sorted(studies))

    def create_new(self):
        # No study name passed; CreateStudyTab will operate in 'new' mode
        self.builder = CreateStudyTab(mode="new", parent_window=self)
        self.builder.show()
        self.hide()

    def edit_selected(self):
        selected = self.study_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a study to edit.")
            return
        study_name = selected.text()
        study_path = os.path.join(self.admin_studies_dir, study_name)
        self.builder = CreateStudyTab(mode="edit", study_name=study_name, source_study_path=study_path, parent_window=self)
        self.builder.show()
        self.hide()

    def review_results(self):
        selected = self.study_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a study.")
            return

        study_name = selected.text()
        study_path = os.path.join(self.admin_studies_dir, study_name)

        results_dir = os.path.join(study_path, "Results")
        os.makedirs(results_dir, exist_ok=True)

        self.review_window = ReviewResultsWindow(study_path, parent_window=self)
        self.review_window.show()
        self.hide()

    def go_back_to_main(self):
        if self.parent_window:
            self.parent_window.show()  # show the admin landing page
        self.close()

    def refresh(self):
        self.refresh_studies()
        self.study_list.clearSelection()

    def delete_study(self):
        selected = self.study_list.currentItem()
        if not selected:
            return
        # Ask if they really do want to remove
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {selected.text()}? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            dir_to_rm = Path(self.admin_studies_dir) / selected.text()
            shutil_rmtree(dir_to_rm)
            self.study_list.clearSelection()
            self.refresh()
        return
    
    def on_reveal_clicked(self):
        selected = self.study_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a study.")
            return

        study_name = selected.text()
        study_path = os.path.join(self.admin_studies_dir, study_name)
        try:
            reveal_in_finder(Path(study_path))
        except Exception as e:
            QMessageBox.warning(
                self,
                "Unable to Reveal Folder",
                str(e)
            )

#Fixing bug here

