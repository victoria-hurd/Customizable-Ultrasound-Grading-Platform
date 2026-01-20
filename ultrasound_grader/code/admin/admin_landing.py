import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget,
    QPushButton, QMessageBox
)
from code.utils.app_paths import get_admin_studies_dir
from code.admin.create_study_tab import CreateStudyTab
from code.admin.results_review import ReviewResultsWindow

class AdminLanding(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin: Studies")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Existing Studies"))

        self.study_list = QListWidget()
        layout.addWidget(self.study_list)

        self.refresh_studies()

        btn_layout = QVBoxLayout()

        self.create_btn = QPushButton("Create New Study")
        self.edit_btn = QPushButton("Edit Selected Study")
        self.results_btn = QPushButton("Review Results for Selected Study")

        self.create_btn.clicked.connect(self.create_new)
        self.edit_btn.clicked.connect(self.edit_selected)
        self.results_btn.clicked.connect(self.review_results)

        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.results_btn)

        layout.addLayout(btn_layout)

    def refresh_studies(self):
        self.study_list.clear()
        admin_dir = get_admin_studies_dir()
        self.admin_studies_dir = str(admin_dir)

        studies = [p.name for p in admin_dir.iterdir() if p.is_dir()]
        self.study_list.addItems(sorted(studies))

    def create_new(self):
        # No study name passed; CreateStudyTab will operate in 'new' mode
        self.builder = CreateStudyTab(mode="new")
        self.builder.show()
        self.hide()

    def edit_selected(self):
        selected = self.study_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a study to edit.")
            return
        study_name = selected.text()
        study_path = os.path.join(self.admin_studies_dir, study_name)
        self.builder = CreateStudyTab(mode="edit", study_name=study_name, source_study_path=study_path)
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



