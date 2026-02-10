from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication, QMessageBox
from code.admin.admin_landing import AdminLanding
from code.grader.grader_landing import GraderLanding
from code.utils.app_paths import delete_all_app_data, reveal_app_bundle_in_finder

class LandingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultrasound Grading Platform")

        layout = QVBoxLayout(self)

        title = QLabel("Welcome to  Ultrasound Grader!")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        admin_btn = QPushButton("Enter as Admin")
        grader_btn = QPushButton("Enter as Grader")
        exit_btn = QPushButton("Exit Application")
        uninstall_btn = QPushButton("Uninstall")

        admin_btn.clicked.connect(self.open_admin)
        grader_btn.clicked.connect(self.open_grader)
        exit_btn.clicked.connect(QApplication.instance().quit)
        uninstall_btn.clicked.connect(self.uninstall_app_data)

        layout.addWidget(admin_btn)
        layout.addWidget(grader_btn)
        layout.addWidget(exit_btn)
        layout.addWidget(uninstall_btn)

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
                "This will permanently delete all Ultrasound Grader data,\n\n"
                "including:\n"
                "• All studies\n"
                "• All grader results\n"
                "• All settings\n\n"
                "This action cannot be undone.\n\n"
                "Do you want to continue?"
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
        
        # Reveal the app in Finder so the user can delete it
        reveal_app_bundle_in_finder()

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

        QApplication.quit()