import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QApplication, QMessageBox
from code.admin.admin_landing import AdminLanding
from code.grader.grader_landing import GraderLanding
from code.utils.app_paths import delete_all_app_data, reveal_app_bundle_in_finder, get_app_support_resources_dir

class LandingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultrasound Grading Platform")

        layout = QVBoxLayout(self)

        # Top bar for exit button
        exit_bar = QHBoxLayout()
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(QApplication.instance().quit)
        exit_bar.addWidget(exit_btn)
        exit_bar.addStretch(5)
        layout.addLayout(exit_bar)

        # Title and welcome screen
        title = QLabel("Welcome to  Ultrasound Grader!")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        # Main functions
        layout.addStretch(1)
        admin_btn = QPushButton("Enter as Admin")
        grader_btn = QPushButton("Enter as Grader")
        layout.addWidget(admin_btn)
        layout.addWidget(grader_btn)
        layout.addStretch(2)
        changes

        # Backup options bar
        backup_options_bar = QHBoxLayout()
        uninstall_btn = QPushButton("Uninstall")
        readme_show_btn = QPushButton("View README")
        backup_options_bar.addWidget(readme_show_btn)
        backup_options_bar.addWidget(uninstall_btn)
        layout.addLayout(backup_options_bar)
        
        # Connect buttons
        admin_btn.clicked.connect(self.open_admin)
        grader_btn.clicked.connect(self.open_grader)
        readme_show_btn.clicked.connect(self.show_readme)
        uninstall_btn.clicked.connect(self.uninstall_app_data)


    def open_admin(self):
        self.admin_window = AdminLanding(parent_window=self)
        self.admin_window.show()
        self.close()

    def open_grader(self):
        self.grader_window = GraderLanding(parent_window=self)
        self.grader_window.show()
        self.close()

    def uninstall_app_data(self):
        reply = QMessageBox.question(
            self,
            "Remove All App Data",
            (
                "This will permanently delete all Ultrasound Grader data that has not been saved to Downloads or backed up outside of the app, including:\n\n"
                "• All created studies and associated metadata\n"
                "• All study results\n"
                "• All grader requests\n"
                "• All graded data\n\n"
                "This action cannot be undone.\n\n"
                "Continue with uninstall?"
            ),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            delete_all_app_data()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Uninstall Failed",
                f"Could not remove app data:\n\n{e}"
            )
            return

        QMessageBox.information(
            self,
            "Almost Done",
            (
                "All application data has been removed.\n\n"
                "The application folder has been opened in Finder.\n"
                "To finish uninstalling, drag the app to the Trash.\n\n"
                "The app will now quit."
            )
        )

        # Reveal the app in Finder so the user can delete it
        reveal_app_bundle_in_finder()

        QApplication.quit()

    def show_readme(self):
        readme_path = os.path.join(get_app_support_resources_dir(), "README.txt")
        try:
            with open(readme_path, "r") as f:
                readme_content = f.read()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not load README:\n\n{e}"
            )
            return

        QMessageBox.information(
            self,
            "README",
            readme_content
        )