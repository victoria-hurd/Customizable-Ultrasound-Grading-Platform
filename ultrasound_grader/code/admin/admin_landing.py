import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget,
    QPushButton, QMessageBox
)
from code.utils.app_paths import get_admin_studies_dir
from code.admin.create_study_tab import CreateStudyTab

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

        self.create_btn.clicked.connect(self.create_new)
        self.edit_btn.clicked.connect(self.edit_selected)

        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.edit_btn)

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


