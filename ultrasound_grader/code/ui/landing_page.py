from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)
from code.admin.admin_landing import AdminLanding
from code.grader.grader_landing import GraderLanding

class LandingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultrasound Grading Platform")

        layout = QVBoxLayout(self)

        title = QLabel("Welcome to the Ultrasound Grading Platform")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        admin_btn = QPushButton("Enter as Admin")
        grader_btn = QPushButton("Enter as Grader")

        admin_btn.clicked.connect(self.open_admin)
        grader_btn.clicked.connect(self.open_grader)

        layout.addWidget(admin_btn)
        layout.addWidget(grader_btn)

    def open_admin(self):
        self.admin_window = AdminLanding()
        self.admin_window.show()
        self.close()

    def open_grader(self):
        self.grader_window = GraderLanding()
        self.grader_window.show()
        self.close()
